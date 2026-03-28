"""
app/services/sms_service.py
──────────────────────────────────────────────────────────────────────────────
Business logic for the SMS Announcement feature.
SMS delivery is handled by sms_gateway.py (A7670E serial modem).

Recipient resolution
────────────────────
  groups   → query Resident + Address + ResidentRFID based on group rules
  puroks   → query Resident joined through Address by purok_id
  specific → use the phone numbers supplied directly

Group definitions
──────────────────
  female    → gender == 'female'
  male      → gender == 'male'
  adult     → calculated age >= 18  (birthdate <= today - 18 years)
  youth     → age in [15, 30]
  senior    → age >= 60             (birthdate <= today - 60 years)
  with_rfid → has at least one active ResidentRFID row

SMS gateway
───────────
  Replace _dispatch_sms() with your actual gateway SDK call
  (e.g. Semaphore, Vonage, Twilio, etc.).
"""

from datetime import date
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

from app.models.resident import Resident, Address, ResidentRFID, Purok
from app.services.sms_gateway import get_gateway
from app.models.sms import SMSLog
from app.schemas.sms import (
    SMSRequest,
    RecipientMode,
    ResidentGroup,
    RecipientCountResponse,
    SMSSendResponse,
    SMSHistoryItem,
)


# ============================================================================
# Internal helpers
# ============================================================================

def _age_cutoff(years: int) -> date:
    """Return the latest birthdate that makes a person exactly `years` old today."""
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)  # Feb 29 edge-case


def _collect_phone_numbers_by_groups(db: Session, groups: List[str]) -> List[str]:
    conditions = []

    for group in groups:
        if group == ResidentGroup.female:
            conditions.append(Resident.gender == "female")

        elif group == ResidentGroup.male:
            conditions.append(Resident.gender == "male")

        elif group == ResidentGroup.adult:
            conditions.append(Resident.birthdate <= _age_cutoff(18))

        elif group == ResidentGroup.youth:
            conditions.append(
                and_(
                    Resident.birthdate >= _age_cutoff(30),
                    Resident.birthdate <= _age_cutoff(15),
                )
            )

        elif group == ResidentGroup.senior:
            conditions.append(Resident.birthdate <= _age_cutoff(60))

        elif group == ResidentGroup.with_rfid:
            conditions.append(
                Resident.rfids.any(ResidentRFID.is_active == True)  # noqa: E712
            )

    residents = (
        db.query(Resident)
        .options(joinedload(Resident.rfids))
        .filter(or_(*conditions))
        .filter(Resident.phone_number.isnot(None))
        .filter(Resident.phone_number != "")
        .all()
    )
    return list({r.phone_number for r in residents})


def _collect_phone_numbers_by_puroks(db: Session, purok_ids: List[int]) -> List[str]:
    residents = (
        db.query(Resident)
        .join(
            Address,
            and_(Address.resident_id == Resident.id, Address.is_current == True)  # noqa: E712
        )
        .filter(Address.purok_id.in_(purok_ids))
        .filter(Resident.phone_number.isnot(None))
        .filter(Resident.phone_number != "")
        .all()
    )
    return list({r.phone_number for r in residents})


def _resolve_phone_numbers(db: Session, payload: SMSRequest) -> List[str]:
    """Return a deduplicated list of phone numbers for the given payload."""
    mode = payload.recipient_mode

    if mode == RecipientMode.groups:
        if not payload.groups:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'groups' field is required when recipient_mode is 'groups'",
            )
        return _collect_phone_numbers_by_groups(db, payload.groups)

    if mode == RecipientMode.puroks:
        if not payload.purok_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'purok_ids' field is required when recipient_mode is 'puroks'",
            )
        return _collect_phone_numbers_by_puroks(db, payload.purok_ids)

    if mode == RecipientMode.specific:
        if not payload.phone_numbers:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'phone_numbers' field is required when recipient_mode is 'specific'",
            )
        return list({n.strip() for n in payload.phone_numbers if n.strip()})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown recipient_mode: {mode}",
    )


# ============================================================================
# Population count helpers  (ALL residents, regardless of phone number)
# Used by get_recipient_count for single-group / single-purok card badges.
# ============================================================================

def _count_residents_by_group(db: Session, group: str) -> int:
    """
    Count ALL residents that belong to a group, regardless of whether they
    have a phone number.  This gives the UI card an accurate population figure
    rather than just the SMS-able subset.
    """
    q = db.query(func.count(Resident.id))

    if group == ResidentGroup.female:
        q = q.filter(Resident.gender == "female")

    elif group == ResidentGroup.male:
        q = q.filter(Resident.gender == "male")

    elif group == ResidentGroup.adult:
        q = q.filter(Resident.birthdate <= _age_cutoff(18))

    elif group == ResidentGroup.youth:
        q = q.filter(
            and_(
                Resident.birthdate >= _age_cutoff(30),
                Resident.birthdate <= _age_cutoff(15),
            )
        )

    elif group == ResidentGroup.senior:
        q = q.filter(Resident.birthdate <= _age_cutoff(60))

    elif group == ResidentGroup.with_rfid:
        q = q.filter(
            Resident.rfids.any(ResidentRFID.is_active == True)  # noqa: E712
        )

    return q.scalar() or 0


def _count_residents_by_purok(db: Session, purok_id: int) -> int:
    """
    Count ALL residents whose current address belongs to the given purok,
    regardless of whether they have a phone number.
    """
    return (
        db.query(func.count(Resident.id))
        .join(
            Address,
            and_(
                Address.resident_id == Resident.id,
                Address.is_current == True,  # noqa: E712
            ),
        )
        .filter(Address.purok_id == purok_id)
        .scalar()
        or 0
    )


# ============================================================================
# SMS Gateway stub — replace with real gateway SDK
# ============================================================================

def _dispatch_sms(phone_numbers: List[str], message: str) -> Dict[str, Any]:
    """
    Send SMS via the A7670E serial modem (sms_gateway.py).

    Returns a dict with keys: sent (int), failed (int), failures (List[str]).
    Raises HTTPException if the modem itself cannot be opened, so the caller
    surfaces a clear error to the frontend instead of logging a silent zero.
    """
    try:
        gateway = get_gateway()
        return gateway.send_bulk(phone_numbers, message)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"SMS gateway error: {exc}",
        )


# Human-readable labels for each group enum value
_GROUP_LABELS: Dict[str, str] = {
    ResidentGroup.female:    "Female",
    ResidentGroup.male:      "Male",
    ResidentGroup.adult:     "18 Years Old & Above",
    ResidentGroup.youth:     "Youth (15–30)",
    ResidentGroup.senior:    "Senior Citizens",
    ResidentGroup.with_rfid: "With RFID",
}


# ============================================================================
# Public service functions
# ============================================================================

def get_recipient_count(db: Session, payload: SMSRequest) -> RecipientCountResponse:
    """
    Dry-run: resolve recipients and return the count WITHOUT sending anything.
    Used by the /preview endpoint so the frontend can show "X recipients".

    Card-badge behaviour (single group or purok selected):
      → counts ALL residents in that group/purok (ignores phone_number),
        so the UI card shows real population figures.

    Selection-badge behaviour (multiple groups/puroks selected):
      → counts only SMS-able residents (have a phone number), because
        that is the actual number of messages that would be sent.
    """
    group_labels: Optional[List[str]] = None
    purok_names:  Optional[List[str]] = None
    count: int = 0

    if payload.recipient_mode == RecipientMode.groups:
        if not payload.groups:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'groups' field is required when recipient_mode is 'groups'",
            )
        group_labels = [_GROUP_LABELS.get(g, g) for g in payload.groups]

        if len(payload.groups) == 1:
            # Single-group → total population count for the card badge
            count = _count_residents_by_group(db, payload.groups[0])
        else:
            # Multi-group selection → deduplicated SMS-able count
            count = len(_collect_phone_numbers_by_groups(db, payload.groups))

    elif payload.recipient_mode == RecipientMode.puroks:
        if not payload.purok_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'purok_ids' field is required when recipient_mode is 'puroks'",
            )
        puroks = db.query(Purok).filter(Purok.id.in_(payload.purok_ids)).all()
        purok_names = [p.purok_name for p in puroks]

        if len(payload.purok_ids) == 1:
            # Single-purok → total population count for the card badge
            count = _count_residents_by_purok(db, payload.purok_ids[0])
        else:
            # Multi-purok selection → deduplicated SMS-able count
            count = len(_collect_phone_numbers_by_puroks(db, payload.purok_ids))

    elif payload.recipient_mode == RecipientMode.specific:
        if not payload.phone_numbers:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'phone_numbers' field is required when recipient_mode is 'specific'",
            )
        count = len({n.strip() for n in payload.phone_numbers if n.strip()})

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown recipient_mode: {payload.recipient_mode}",
        )

    return RecipientCountResponse(
        recipient_mode=payload.recipient_mode,
        group_labels=group_labels,
        purok_names=purok_names,
        count=count,
    )


def send_sms_announcement(db: Session, payload: SMSRequest) -> SMSSendResponse:
    """Resolve recipients, dispatch SMS, and log the blast."""
    phone_numbers = _resolve_phone_numbers(db, payload)

    if not phone_numbers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No phone numbers found for the selected recipients.",
        )

    result = _dispatch_sms(phone_numbers, payload.message)

    # Build a human-readable mode label for the audit log
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

    return SMSSendResponse(
        success=True,
        recipients=result["sent"],
        message_preview=payload.message[:80],
        failed=result.get("failed", 0),
        queued_at=queued_at,
    )


def get_sms_history(db: Session, limit: int = 20) -> List[SMSHistoryItem]:
    """Return the most recent SMS blasts for the history panel."""
    logs = (
        db.query(SMSLog)
        .order_by(SMSLog.sent_at.desc())
        .limit(limit)
        .all()
    )
    return [
        SMSHistoryItem(
            id=log.id,
            message=log.message,
            mode=log.mode,
            recipients=log.recipients,
            sent_at=log.sent_at.isoformat(),
        )
        for log in logs
    ]