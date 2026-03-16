from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String
from app.api.deps import get_db
from app.models.resident import Resident
from app.models.document import DocumentRequest, DocumentType
from app.models.equipment import EquipmentInventory, EquipmentRequest, EquipmentRequestItem
from app.models.blotter import BlotterRecord
from app.models.announcement import Announcement
from app.models.faqs import FAQ
from app.models.misc import Feedback
from app.models.contact import ContactInformation

router = APIRouter(prefix="/search")

STATIC_PAGES = [
    { "label": "System Settings",      "subtitle": "Page", "route": "/system-settings",      "type": "page" },
    { "label": "SMS Announcements",    "subtitle": "Page", "route": "/sms-announcements",    "type": "page" },
    { "label": "Kiosk Announcements",  "subtitle": "Page", "route": "/kiosk-announcements",  "type": "page" },
    { "label": "Notifications",        "subtitle": "Page", "route": "/notifications",         "type": "page" },
    { "label": "Contact Information",  "subtitle": "Page", "route": "/contact-information",  "type": "page" },
    { "label": "FAQs Management",      "subtitle": "Page", "route": "/faqs-management",      "type": "page" },
    { "label": "Blotter & KP Logs",    "subtitle": "Page", "route": "/blotter-kp-logs",      "type": "page" },
    { "label": "Equipment Inventory",  "subtitle": "Page", "route": "/equipment-inventory",  "type": "page" },
    { "label": "Residents Management", "subtitle": "Page", "route": "/residents-management", "type": "page" },
    { "label": "Document Services",    "subtitle": "Page", "route": "/document-services",    "type": "page" },
    { "label": "Feedback & Reports",   "subtitle": "Page", "route": "/feedback-and-reports", "type": "page" },
    { "label": "Account Settings",     "subtitle": "Page", "route": "/account-settings",     "type": "page" },
    { "label": "Help & Support",       "subtitle": "Page", "route": "/system-guide",     "type": "page" },
]


@router.get("")
def global_search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    term = f"%{q.lower()}%"
    results = {}

    # ── Static pages ──────────────────────────────────────────────────────────
    matched_pages = [
        {**p, "id": i}
        for i, p in enumerate(STATIC_PAGES)
        if q.lower() in p["label"].lower()
    ]
    if matched_pages:
        results["pages"] = matched_pages

    # ── Residents ─────────────────────────────────────────────────────────────
    residents = (
        db.query(Resident)
        .filter(
            or_(
                Resident.first_name.ilike(term),
                Resident.last_name.ilike(term),
                Resident.middle_name.ilike(term),
                Resident.phone_number == q.strip(),
                cast(Resident.id, String) == q.strip(),
            )
        )
        .limit(5)
        .all()
    )
    results["members"] = [
    {
        "id": r.id,
        "label": f"{r.first_name} {r.last_name}",
        "subtitle": f"Resident · ID #{r.id}",
        "route": f"/residents-management?q={r.id}",  # ← use ID not name
        "type": "member",
    }
    for r in residents
]

    # ── Document Requests ─────────────────────────────────────────────────────
    # joins Resident + DocumentType so we can search by name and doc type
    doc_requests = (
        db.query(DocumentRequest)
        .join(DocumentRequest.resident)
        .outerjoin(DocumentRequest.doctype)
        .options(
            joinedload(DocumentRequest.resident),
            joinedload(DocumentRequest.doctype)
        )
        .filter(
            or_(
                DocumentRequest.transaction_no.ilike(term),
                DocumentRequest.status.ilike(term),
                DocumentRequest.payment_status.ilike(term),
                Resident.first_name.ilike(term),
                Resident.last_name.ilike(term),
                Resident.middle_name.ilike(term),
                DocumentType.doctype_name.ilike(term),  # ← search by doc type name
            )
        )
        .limit(5)
        .all()
    )
    results["documents"] = [
        {
            "id": d.id,
            "label": (
                d.doctype.doctype_name if d.doctype else "I.D Application"
            ) + (
                f" – {d.resident.first_name} {d.resident.last_name}"
                if d.resident else ""
            ),
            "subtitle": f"{d.transaction_no} · {d.status}",
            "route": f"/document-requests/{d.status}?q={d.transaction_no}",
            "type": "document",
        }
        for d in doc_requests
    ]

    # ── Equipment Inventory ───────────────────────────────────────────────────
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.name.ilike(term))
        .limit(5)
        .all()
    )
    results["equipment"] = [
        {
            "id": e.id,
            "label": e.name,
            "subtitle": f"Equipment · {e.available_quantity}/{e.total_quantity} available",
            "route": f"/equipment-inventory?q={e.name.replace(' ', '+')}",
            "type": "equipment",
        }
        for e in equipment
    ]

    # ── Equipment Requests ────────────────────────────────────────────────────
    # joins Resident + EquipmentRequestItem + EquipmentInventory
    # so searching "monobloc chairs" finds requests that include that item
    equip_requests = (
        db.query(EquipmentRequest)
        .join(EquipmentRequest.resident)
        .outerjoin(EquipmentRequest.items)
        .outerjoin(EquipmentRequestItem.inventory_item)
        .options(joinedload(EquipmentRequest.resident))
        .filter(
            or_(
                EquipmentRequest.transaction_no.ilike(term),
                EquipmentRequest.status.ilike(term),
                EquipmentRequest.purpose.ilike(term),
                Resident.first_name.ilike(term),
                Resident.last_name.ilike(term),
                Resident.middle_name.ilike(term),
                EquipmentInventory.name.ilike(term),  # ← search by item name
            )
        )
        .distinct()  # outerjoin can produce duplicates, this prevents that
        .limit(5)
        .all()
    )
    results["equipment_requests"] = [
        {
            "id": er.id,
            "label": (
                f"Equipment Request – {er.resident.first_name} {er.resident.last_name}"
                if er.resident else f"Request #{er.id}"
            ),
            "subtitle": f"{er.transaction_no} · {er.status}",
            "route": f"/equipment-requests/{er.status}?q={er.transaction_no}",
            "type": "equipment_request",
        }
        for er in equip_requests
    ]

    # ── Blotter Records ───────────────────────────────────────────────────────
    blotter = (
        db.query(BlotterRecord)
        .filter(
            or_(
                BlotterRecord.blotter_no.ilike(term),
                BlotterRecord.complainant_name.ilike(term),
                BlotterRecord.respondent_name.ilike(term),
                BlotterRecord.incident_type.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["blotter"] = [
        {
            "id": b.id,
            "label": f"{b.blotter_no} – {b.incident_type or 'Blotter Record'}",
            "subtitle": f"vs. {b.respondent_name or 'Unknown'} · {str(b.incident_date) if b.incident_date else 'No date'}",
            "route": f"/blotter-kp-logs?q={b.blotter_no}",
            "type": "blotter",
        }
        for b in blotter
    ]

    # ── Announcements ─────────────────────────────────────────────────────────
    announcements = (
        db.query(Announcement)
        .filter(
            or_(
                Announcement.title.ilike(term),
                Announcement.location.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["announcements"] = [
    {
        "id": a.id,
        "label": a.title,
        "subtitle": f"Announcement · {a.location}",
        "route": f"/kiosk-announcements?q={a.title.replace(' ', '+')}",
        "type": "announcement",
    }
    for a in announcements
]

    # ── FAQs ──────────────────────────────────────────────────────────────────
    faqs = (
        db.query(FAQ)
        .filter(
            or_(
                FAQ.question.ilike(term),
                FAQ.answer.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["faqs"] = [
        {
            "id": faq.id,
            "label": faq.question,
            "subtitle": "FAQ",
            "route": f"/faqs-management?q={faq.question[:30].replace(' ', '+')}",
            "type": "faq",
        }
        for faq in faqs
    ]

    # ── Feedback ──────────────────────────────────────────────────────────────
    feedbacks = (
        db.query(Feedback)
        .filter(
            or_(
                Feedback.category.ilike(term),
                cast(Feedback.rating, String).ilike(term),
                Feedback.additional_comments.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["feedback"] = [
        {
            "id": fb.id,
            "label": fb.category,
            "subtitle": f"Rating: {fb.rating}/5",
            "route": f"/feedback-and-reports?q={fb.category.replace(' ', '+')}",
            "type": "feedback",
        }
        for fb in feedbacks
    ]

# ── Document Services (Document Types) ───────────────────────────────────
    doc_types = (
        db.query(DocumentType)
        .filter(
            or_(
                DocumentType.doctype_name.ilike(term),
                DocumentType.description.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["doc_services"] = [
        {
            "id": dt.id,
            "label": dt.doctype_name,
            "subtitle": f"Document Service · {'Available' if dt.is_available else 'Unavailable'} · ₱{dt.price}",
            "route": f"/document-services?q={dt.doctype_name.replace(' ', '+')}",
            "type": "doc_service",
        }
        for dt in doc_types
    ]

# ── Contact Information ───────────────────────────────────────────────────
    contact = db.query(ContactInformation).first()
    if contact:
        contact_fields = [
            ("Emergency Number", contact.emergency_number),
            ("Emergency Description", contact.emergency_desc),
            ("Phone", contact.phone),
            ("Email", contact.email),
            ("Office Hours", contact.office_hours),
            ("Address", contact.address),
            ("Technical Support", contact.tech_support),
        ]
        matched_contact = [
            {
                "id": i,
                "label": label,
                "subtitle": f"Contact Information · {value}",
                "route": "/contact-information",
                "type": "contact",
            }
            for i, (label, value) in enumerate(contact_fields)
            if value and q.lower() in value.lower()
        ]
        if matched_contact:
            results["contact"] = matched_contact

    return {k: v for k, v in results.items() if v}