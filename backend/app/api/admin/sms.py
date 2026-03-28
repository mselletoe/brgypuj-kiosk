import json
import asyncio
from typing import List, AsyncGenerator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.schemas.sms import (
    SMSRequest,
    RecipientCountResponse,
    SMSSendResponse,
    SMSHistoryItem,
    RecipientMode,
)
from app.services.sms_service import (
    get_recipient_count,
    send_sms_announcement,
    get_sms_history,
    _resolve_phone_numbers,
    _GROUP_LABELS,
)
from app.services.sms_gateway import get_gateway
from app.models.sms import SMSLog
from app.models.resident import Purok
from app.api.deps import get_db

router = APIRouter(prefix="/sms")


# ============================================================================
# Preview (dry-run)
# ============================================================================

@router.post("/preview", response_model=RecipientCountResponse)
def preview_recipients(payload: SMSRequest, db: Session = Depends(get_db)):
    """
    Resolve recipients for the given payload and return the count WITHOUT
    actually sending any messages.

    Use this to power the live "X recipients selected" badge in the UI.
    """
    return get_recipient_count(db, payload)


# ============================================================================
# Send (standard — returns when fully done)
# ============================================================================

@router.post("/send", response_model=SMSSendResponse, status_code=201)
def send_announcement(payload: SMSRequest, db: Session = Depends(get_db)):
    """
    Send an SMS blast to the resolved recipient list and log the operation.

    recipient_mode options
    ──────────────────────
    - **groups**   → pass `groups` list with one or more of:
        `female`, `male`, `adult`, `youth`, `senior`, `with_rfid`
    - **puroks**   → pass `purok_ids` list with purok IDs from the database
    - **specific** → pass `phone_numbers` list with raw phone numbers

    Example (groups):
    ```json
    {
      "message": "Barangay assembly bukas ng 5PM sa covered court.",
      "recipient_mode": "groups",
      "groups": ["senior", "with_rfid"]
    }
    ```

    Example (puroks):
    ```json
    {
      "message": "Water interruption scheduled tomorrow, 8AM–5PM.",
      "recipient_mode": "puroks",
      "purok_ids": [1, 3]
    }
    ```
    """
    return send_sms_announcement(db, payload)


# ============================================================================
# Send (streaming — Server-Sent Events progress)
# ============================================================================

def _sse(event: str, data: dict) -> str:
    """Format a single SSE frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/send-stream")
async def send_announcement_stream(
    payload: SMSRequest,
    db: Session = Depends(get_db),
):
    """
    Stream SMS send progress as Server-Sent Events.

    Events emitted:
      start    → { total: int }
      progress → { current: int, total: int, number: str, ok: bool }
      done     → { sent: int, failed: int, failures: str[], queued_at: str }
      error    → { detail: str }
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()

        # 1. Resolve recipients
        try:
            phone_numbers = await loop.run_in_executor(
                None, _resolve_phone_numbers, db, payload
            )
        except Exception as exc:
            yield _sse("error", {"detail": str(exc)})
            return

        if not phone_numbers:
            yield _sse("error", {"detail": "No phone numbers found for the selected recipients."})
            return

        total = len(phone_numbers)
        yield _sse("start", {"total": total})

        # 2. Progress queue — gateway thread posts here, we stream from here
        progress_queue: asyncio.Queue = asyncio.Queue()

        def on_progress(current, total_, number, ok, error=None):
            if error:
                progress_queue.put_nowait(("error", {"detail": error}))
            else:
                progress_queue.put_nowait((
                    "progress",
                    {"current": current, "total": total_, "number": number, "ok": ok},
                ))

        # 3. Run gateway in background thread
        gateway = get_gateway()

        async def run_gateway():
            result = await loop.run_in_executor(
                None,
                lambda: gateway.send_bulk(phone_numbers, payload.message, on_progress),
            )
            progress_queue.put_nowait(("__done__", result))

        asyncio.ensure_future(run_gateway())

        # 4. Stream progress events as they arrive
        result = None
        while True:
            event_type, data = await progress_queue.get()
            if event_type == "__done__":
                result = data
                break
            yield _sse(event_type, data)
            if event_type == "error":
                return

        # 5. Log to DB then emit done
        queued_at = ""
        if result:
            try:
                if payload.recipient_mode == RecipientMode.groups and payload.groups:
                    mode_label = ", ".join(_GROUP_LABELS.get(g, g) for g in payload.groups)
                elif payload.recipient_mode == RecipientMode.puroks and payload.purok_ids:
                    puroks = db.query(Purok).filter(Purok.id.in_(payload.purok_ids)).all()
                    mode_label = ", ".join(p.purok_name for p in puroks)
                else:
                    mode_label = "Specific Numbers"

                log_entry = SMSLog(
                    message=payload.message,
                    mode=mode_label,
                    recipients=result["sent"],
                )
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                queued_at = log_entry.sent_at.isoformat() if log_entry.sent_at else ""
            except Exception:
                pass

            yield _sse("done", {
                "sent":      result["sent"],
                "failed":    result.get("failed", 0),
                "failures":  result.get("failures", []),
                "queued_at": queued_at,
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# History
# ============================================================================

@router.get("/history", response_model=List[SMSHistoryItem])
def list_sms_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Return recent SMS blasts in descending order for the history panel.
    """
    return get_sms_history(db, limit=limit)