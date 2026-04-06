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


@router.post("/preview", response_model=RecipientCountResponse)
def preview_recipients(payload: SMSRequest, db: Session = Depends(get_db)):
    return get_recipient_count(db, payload)


@router.post("/send", response_model=SMSSendResponse, status_code=201)
def send_announcement(payload: SMSRequest, db: Session = Depends(get_db)):
    return send_sms_announcement(db, payload)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/send-stream")
async def send_announcement_stream(
    payload: SMSRequest,
    db: Session = Depends(get_db),
):

    async def event_stream() -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()

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

        progress_queue: asyncio.Queue = asyncio.Queue()

        def on_progress(current, total_, number, ok, error=None):
            if error:
                progress_queue.put_nowait(("error", {"detail": error}))
            else:
                progress_queue.put_nowait((
                    "progress",
                    {"current": current, "total": total_, "number": number, "ok": ok},
                ))

        gateway = get_gateway()

        async def run_gateway():
            result = await loop.run_in_executor(
                None,
                lambda: gateway.send_bulk(phone_numbers, payload.message, on_progress),
            )
            progress_queue.put_nowait(("__done__", result))

        asyncio.ensure_future(run_gateway())

        result = None
        while True:
            event_type, data = await progress_queue.get()
            if event_type == "__done__":
                result = data
                break
            yield _sse(event_type, data)
            if event_type == "error":
                return

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


@router.get("/history", response_model=List[SMSHistoryItem])
def list_sms_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_sms_history(db, limit=limit)