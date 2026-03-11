"""
Financial Statement Service
-----------------------------
Aggregates financial data from Document Requests, ID Applications,
and Equipment Borrowing Requests and renders a professional PDF
report that admins can download and forward to the treasurer.

Usage
-----
  from app.services.financial_service import generate_financial_statement_pdf

  pdf_bytes = generate_financial_statement_pdf(
      db,
      date_from=date(2025, 1, 1),
      date_to=date(2025, 12, 31),
      service_filter=None,   # or "documents" / "id_services" / "equipment"
  )
"""

from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from sqlalchemy.orm import Session

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE  (matches a professional government document look)
# ─────────────────────────────────────────────────────────────
PRIMARY     = colors.HexColor("#03335C")
SECONDARY   = colors.HexColor("#2563eb")   # accent blue
LIGHT_BG    = colors.HexColor("#f0f4f8")   # alternating row fill
BORDER      = colors.HexColor("#cbd5e1")   # table border
GREEN       = colors.HexColor("#16a34a")
RED         = colors.HexColor("#dc2626")
GOLD        = colors.HexColor("#ca8a04")
DARK_TEXT   = colors.HexColor("#1e293b")
MUTED_TEXT  = colors.HexColor("#64748b")
WHITE       = colors.white


# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()

    return {
        "brgy_name": ParagraphStyle(
            "brgy_name",
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "brgy_sub": ParagraphStyle(
            "brgy_sub",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#cbd5e1"),
            alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "report_title": ParagraphStyle(
            "report_title",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=2,
        ),
        "report_period": ParagraphStyle(
            "report_period",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#bfdbfe"),
            alignment=TA_CENTER,
        ),
        "section_heading": ParagraphStyle(
            "section_heading",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=PRIMARY,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=8,
            textColor=DARK_TEXT,
        ),
        "table_cell_right": ParagraphStyle(
            "table_cell_right",
            fontName="Helvetica",
            fontSize=8,
            textColor=DARK_TEXT,
            alignment=TA_RIGHT,
        ),
        "table_cell_center": ParagraphStyle(
            "table_cell_center",
            fontName="Helvetica",
            fontSize=8,
            textColor=DARK_TEXT,
            alignment=TA_CENTER,
        ),
        "total_label": ParagraphStyle(
            "total_label",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=DARK_TEXT,
            alignment=TA_RIGHT,
        ),
        "total_value": ParagraphStyle(
            "total_value",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=PRIMARY,
            alignment=TA_RIGHT,
        ),
        "summary_label": ParagraphStyle(
            "summary_label",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_TEXT,
        ),
        "summary_value": ParagraphStyle(
            "summary_value",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=PRIMARY,
            alignment=TA_RIGHT,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=7,
            textColor=MUTED_TEXT,
            alignment=TA_CENTER,
        ),
        "note": ParagraphStyle(
            "note",
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            textColor=MUTED_TEXT,
        ),
        "grand_total_label": ParagraphStyle(
            "grand_total_label",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "grand_total_value": ParagraphStyle(
            "grand_total_value",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=WHITE,
            alignment=TA_RIGHT,
        ),
        "pill_paid": ParagraphStyle(
            "pill_paid",
            fontName="Helvetica-Bold",
            fontSize=7,
            textColor=GREEN,
            alignment=TA_CENTER,
        ),
        "pill_unpaid": ParagraphStyle(
            "pill_unpaid",
            fontName="Helvetica-Bold",
            fontSize=7,
            textColor=RED,
            alignment=TA_CENTER,
        ),
    }


# ─────────────────────────────────────────────────────────────
# DATA AGGREGATION
# ─────────────────────────────────────────────────────────────

def _get_document_data(db: Session, date_from: date, date_to: date) -> dict:
    """
    Pulls paid Document Requests (excluding ID Applications) within the date range.
    Only Released + Paid rows count as actual income.
    """
    from app.models.document import DocumentRequest

    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to   = datetime.combine(date_to,   datetime.max.time())

    rows = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.requested_at >= dt_from,
            DocumentRequest.requested_at <= dt_to,
            DocumentRequest.doctype_id.isnot(None),   # exclude ID Applications
        )
        .order_by(DocumentRequest.requested_at.asc())
        .all()
    )

    transactions = []
    total_collected = Decimal("0")
    total_pending   = Decimal("0")

    for r in rows:
        doctype_name = r.doctype.doctype_name if r.doctype else "Unknown"
        resident_name = "N/A"
        if r.resident:
            parts = filter(None, [r.resident.first_name, r.resident.middle_name, r.resident.last_name])
            resident_name = " ".join(parts)

        is_paid = r.payment_status == "paid"
        price   = r.price or Decimal("0")

        if is_paid:
            total_collected += price
        else:
            total_pending += price

        transactions.append({
            "transaction_no": r.transaction_no,
            "resident_name": resident_name,
            "document_type": doctype_name,
            "status": r.status,
            "payment_status": r.payment_status,
            "amount": price,
            "date": r.requested_at.strftime("%m/%d/%Y") if r.requested_at else "—",
        })

    return {
        "transactions": transactions,
        "total_collected": total_collected,
        "total_pending": total_pending,
        "count": len(transactions),
    }


def _get_id_application_data(db: Session, date_from: date, date_to: date) -> dict:
    """
    Pulls ID Application rows (doctype_id IS NULL) within the date range.
    """
    from app.models.document import DocumentRequest

    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to   = datetime.combine(date_to,   datetime.max.time())

    rows = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.requested_at >= dt_from,
            DocumentRequest.requested_at <= dt_to,
            DocumentRequest.doctype_id.is_(None),    # only ID Applications
        )
        .order_by(DocumentRequest.requested_at.asc())
        .all()
    )

    transactions = []
    total_collected = Decimal("0")
    total_pending   = Decimal("0")

    for r in rows:
        resident_name = "N/A"
        if r.resident:
            parts = filter(None, [r.resident.first_name, r.resident.last_name])
            resident_name = " ".join(parts)

        is_paid = r.payment_status == "paid"
        price   = r.price or Decimal("0")

        if is_paid:
            total_collected += price
        else:
            total_pending += price

        transactions.append({
            "transaction_no": r.transaction_no,
            "resident_name": resident_name,
            "status": r.status,
            "payment_status": r.payment_status,
            "amount": price,
            "date": r.requested_at.strftime("%m/%d/%Y") if r.requested_at else "—",
        })

    return {
        "transactions": transactions,
        "total_collected": total_collected,
        "total_pending": total_pending,
        "count": len(transactions),
    }


def _get_equipment_data(db: Session, date_from: date, date_to: date) -> dict:
    """
    Pulls Equipment Borrowing Requests within the date range.
    """
    from app.models.equipment import EquipmentRequest

    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to   = datetime.combine(date_to,   datetime.max.time())

    rows = (
        db.query(EquipmentRequest)
        .filter(
            EquipmentRequest.requested_at >= dt_from,
            EquipmentRequest.requested_at <= dt_to,
        )
        .order_by(EquipmentRequest.requested_at.asc())
        .all()
    )

    transactions = []
    total_collected = Decimal("0")
    total_pending   = Decimal("0")
    total_refunded  = Decimal("0")

    for r in rows:
        resident_name = "N/A"
        if r.resident:
            parts = filter(None, [r.resident.first_name, r.resident.last_name])
            resident_name = " ".join(parts)

        item_names = ", ".join(
            (item.inventory_item.name if item.inventory_item else "?")
            for item in r.items
        ) if r.items else "—"

        is_paid    = r.payment_status == "paid"
        is_refunded = r.is_refunded
        cost       = r.total_cost or Decimal("0")

        if is_refunded:
            total_refunded += cost
        elif is_paid:
            total_collected += cost
        else:
            total_pending += cost

        transactions.append({
            "transaction_no": r.transaction_no,
            "resident_name": resident_name,
            "items": item_names,
            "borrow_date": r.borrow_date.strftime("%m/%d/%Y") if r.borrow_date else "—",
            "return_date": r.return_date.strftime("%m/%d/%Y") if r.return_date else "—",
            "status": r.status,
            "payment_status": r.payment_status,
            "is_refunded": is_refunded,
            "amount": cost,
            "date": r.requested_at.strftime("%m/%d/%Y") if r.requested_at else "—",
        })

    return {
        "transactions": transactions,
        "total_collected": total_collected,
        "total_pending": total_pending,
        "total_refunded": total_refunded,
        "count": len(transactions),
    }


# ─────────────────────────────────────────────────────────────
# PDF BUILDING HELPERS
# ─────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN


def _header_table(styles, date_from: date, date_to: date, service_filter: Optional[str]) -> Table:
    """Renders the navy-blue banner at the top of the report."""
    period_str = f"{date_from.strftime('%B %d, %Y')}  –  {date_to.strftime('%B %d, %Y')}"

    service_label = {
        "documents":   "Document Services",
        "id_services": "I.D Services",
        "equipment":   "Equipment Borrowing",
    }.get(service_filter, "All Services")

    header_content = [
        [
            Paragraph("BARANGAY KIOSK FINANCIAL STATEMENT", styles["brgy_name"]),
        ],
        [
            Paragraph("Barangay Poblacion I, Amadeo, Cavite  ·  Kiosk System", styles["brgy_sub"]),
        ],
        [
            Paragraph(f"Report Coverage: {service_label}", styles["report_title"]),
        ],
        [
            Paragraph(f"Period: {period_str}", styles["report_period"]),
        ],
        [
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}",
                styles["report_period"],
            )
        ],
    ]

    t = Table([[row[0]] for row in header_content], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING",  (0, 0), (-1,  0), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING",   (0, 1), (-1, -2), 1),
        ("BOTTOMPADDING",(0, 1), (-1, -2), 1),
    ]))
    return t


def _summary_card(styles, label: str, collected: Decimal, pending: Decimal, extra: dict = None) -> Table:
    """
    Renders a single summary card with collected / pending / optional extra rows.
    Returns a Table so it can be used inside a KeepTogether block.
    """
    rows = [
        [
            Paragraph(label, ParagraphStyle(
                "card_label",
                fontName="Helvetica-Bold",
                fontSize=10,
                textColor=WHITE,
            )),
            "",
        ],
        [
            Paragraph("Collected:", styles["summary_label"]),
            Paragraph(f"₱ {collected:,.2f}", styles["summary_value"]),
        ],
        [
            Paragraph("Pending:", styles["summary_label"]),
            Paragraph(
                f"₱ {pending:,.2f}",
                ParagraphStyle("pend_val", fontName="Helvetica-Bold", fontSize=10,
                               textColor=GOLD, alignment=TA_RIGHT),
            ),
        ],
    ]

    ts = [
        ("BACKGROUND",    (0, 0), (-1, 0),  SECONDARY),
        ("SPAN",          (0, 0), (1,  0)),
        ("TOPPADDING",    (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  8),
        ("LEFTPADDING",   (0, 0), (-1,-1),  10),
        ("RIGHTPADDING",  (0, 0), (-1,-1),  10),
        ("TOPPADDING",    (0, 1), (-1,-1),  5),
        ("BOTTOMPADDING", (0, 1), (-1,-1),  5),
        ("BACKGROUND",    (0, 1), (-1,-1),  colors.HexColor("#f8fafc")),
        ("BOX",           (0, 0), (-1,-1),  0.5, BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.5, BORDER),
        ("ROWBACKGROUNDS",(0, 1), (-1,-1),  [colors.white, LIGHT_BG]),
    ]

    if extra:
        for row_label, row_value, row_color in extra:
            val_style = ParagraphStyle(
                "extra_val",
                fontName="Helvetica-Bold",
                fontSize=10,
                textColor=row_color,
                alignment=TA_RIGHT,
            )
            rows.append([Paragraph(row_label, styles["summary_label"]),
                         Paragraph(f"₱ {row_value:,.2f}", val_style)])

    half_w = (CONTENT_W - 6) / 2

    t = Table(rows, colWidths=[half_w * 0.55, half_w * 0.45])
    t.setStyle(TableStyle(ts))
    return t


def _transaction_table_docs(styles, transactions: list) -> Table:
    """Document requests table."""
    header = [
        Paragraph("TXN #",         styles["table_header"]),
        Paragraph("Resident",       styles["table_header"]),
        Paragraph("Document Type",  styles["table_header"]),
        Paragraph("Status",         styles["table_header"]),
        Paragraph("Payment",        styles["table_header"]),
        Paragraph("Amount",         styles["table_header"]),
        Paragraph("Date",           styles["table_header"]),
    ]

    col_w = [
        CONTENT_W * 0.12,
        CONTENT_W * 0.20,
        CONTENT_W * 0.20,
        CONTENT_W * 0.11,
        CONTENT_W * 0.10,
        CONTENT_W * 0.13,
        CONTENT_W * 0.14,
    ]

    data = [header]
    for i, tx in enumerate(transactions):
        pay_style = styles["pill_paid"] if tx["payment_status"] == "paid" else styles["pill_unpaid"]
        data.append([
            Paragraph(tx["transaction_no"],  styles["table_cell"]),
            Paragraph(tx["resident_name"],   styles["table_cell"]),
            Paragraph(tx["document_type"],   styles["table_cell"]),
            Paragraph(tx["status"],          styles["table_cell_center"]),
            Paragraph(tx["payment_status"].title(), pay_style),
            Paragraph(f"₱ {tx['amount']:,.2f}", styles["table_cell_right"]),
            Paragraph(tx["date"],            styles["table_cell_center"]),
        ])

    return _styled_table(data, col_w)


def _transaction_table_id(styles, transactions: list) -> Table:
    """ID Application table."""
    header = [
        Paragraph("TXN #",    styles["table_header"]),
        Paragraph("Resident", styles["table_header"]),
        Paragraph("Status",   styles["table_header"]),
        Paragraph("Payment",  styles["table_header"]),
        Paragraph("Amount",   styles["table_header"]),
        Paragraph("Date",     styles["table_header"]),
    ]

    col_w = [
        CONTENT_W * 0.15,
        CONTENT_W * 0.30,
        CONTENT_W * 0.13,
        CONTENT_W * 0.13,
        CONTENT_W * 0.15,
        CONTENT_W * 0.14,
    ]

    data = [header]
    for tx in transactions:
        pay_style = styles["pill_paid"] if tx["payment_status"] == "paid" else styles["pill_unpaid"]
        data.append([
            Paragraph(tx["transaction_no"],  styles["table_cell"]),
            Paragraph(tx["resident_name"],   styles["table_cell"]),
            Paragraph(tx["status"],          styles["table_cell_center"]),
            Paragraph(tx["payment_status"].title(), pay_style),
            Paragraph(f"₱ {tx['amount']:,.2f}", styles["table_cell_right"]),
            Paragraph(tx["date"],            styles["table_cell_center"]),
        ])

    return _styled_table(data, col_w)


def _transaction_table_equipment(styles, transactions: list) -> Table:
    """Equipment requests table."""
    header = [
        Paragraph("TXN #",    styles["table_header"]),
        Paragraph("Resident", styles["table_header"]),
        Paragraph("Items",    styles["table_header"]),
        Paragraph("Borrow",   styles["table_header"]),
        Paragraph("Return",   styles["table_header"]),
        Paragraph("Status",   styles["table_header"]),
        Paragraph("Payment",  styles["table_header"]),
        Paragraph("Amount",   styles["table_header"]),
    ]

    col_w = [
        CONTENT_W * 0.10,
        CONTENT_W * 0.15,
        CONTENT_W * 0.21,
        CONTENT_W * 0.10,
        CONTENT_W * 0.10,
        CONTENT_W * 0.10,
        CONTENT_W * 0.10,
        CONTENT_W * 0.14,
    ]

    data = [header]
    for tx in transactions:
        if tx["is_refunded"]:
            pay_label = "Refunded"
            pay_style = ParagraphStyle("ref", fontName="Helvetica-Bold", fontSize=7,
                                       textColor=SECONDARY, alignment=TA_CENTER)
        elif tx["payment_status"] == "paid":
            pay_label = "Paid"
            pay_style = styles["pill_paid"]
        else:
            pay_label = "Unpaid"
            pay_style = styles["pill_unpaid"]

        data.append([
            Paragraph(tx["transaction_no"],  styles["table_cell"]),
            Paragraph(tx["resident_name"],   styles["table_cell"]),
            Paragraph(tx["items"],           styles["table_cell"]),
            Paragraph(tx["borrow_date"],     styles["table_cell_center"]),
            Paragraph(tx["return_date"],     styles["table_cell_center"]),
            Paragraph(tx["status"],          styles["table_cell_center"]),
            Paragraph(pay_label,             pay_style),
            Paragraph(f"₱ {tx['amount']:,.2f}", styles["table_cell_right"]),
        ])

    return _styled_table(data, col_w)


def _styled_table(data: list, col_w: list) -> Table:
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY),
        ("TOPPADDING",    (0, 0), (-1, 0),  7),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
        ("LEFTPADDING",   (0, 0), (-1,-1),  5),
        ("RIGHTPADDING",  (0, 0), (-1,-1),  5),
        # Data rows
        ("FONTSIZE",      (0, 1), (-1,-1),  8),
        ("TOPPADDING",    (0, 1), (-1,-1),  4),
        ("BOTTOMPADDING", (0, 1), (-1,-1),  4),
        ("ROWBACKGROUNDS",(0, 1), (-1,-1),  [colors.white, LIGHT_BG]),
        # Grid
        ("GRID",          (0, 0), (-1,-1),  0.4, BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  1,   SECONDARY),
        # Valign
        ("VALIGN",        (0, 0), (-1,-1),  "MIDDLE"),
    ]))
    return t


def _section_total_row(styles, label: str, collected: Decimal, pending: Decimal) -> Table:
    """Right-aligned totals row below each section table."""
    data = [[
        Paragraph(f"{label} — Total Collected:", styles["total_label"]),
        Paragraph(f"₱ {collected:,.2f}", styles["total_value"]),
        Paragraph(f"  Pending: ₱ {pending:,.2f}", ParagraphStyle(
            "pend",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=GOLD,
        )),
    ]]
    t = Table(data, colWidths=[CONTENT_W * 0.46, CONTENT_W * 0.27, CONTENT_W * 0.27])
    t.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1,-1), 4),
        ("BOTTOMPADDING", (0, 0), (-1,-1), 4),
        ("ALIGN",         (0, 0), (0,  0), "RIGHT"),
        ("ALIGN",         (1, 0), (1,  0), "RIGHT"),
        ("BACKGROUND",    (0, 0), (-1,-1), colors.HexColor("#f0f4f8")),
        ("BOX",           (0, 0), (-1,-1), 0.4, BORDER),
    ]))
    return t


def _grand_total_banner(styles, total: Decimal, label: str = "GRAND TOTAL COLLECTED") -> Table:
    data = [[
        Paragraph(label, styles["grand_total_label"]),
        Paragraph(f"₱ {total:,.2f}", styles["grand_total_value"]),
    ]]
    t = Table(data, colWidths=[CONTENT_W * 0.6, CONTENT_W * 0.4])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,-1), PRIMARY),
        ("TOPPADDING",    (0, 0), (-1,-1), 10),
        ("BOTTOMPADDING", (0, 0), (-1,-1), 10),
        ("LEFTPADDING",   (0, 0), (-1,-1), 14),
        ("RIGHTPADDING",  (0, 0), (-1,-1), 14),
    ]))
    return t


def _empty_notice(styles, message: str) -> Paragraph:
    return Paragraph(
        f"<i>{message}</i>",
        ParagraphStyle(
            "empty",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=MUTED_TEXT,
            leftIndent=10,
        ),
    )


def _page_footer(canvas, doc):
    """Draws page number and disclaimer at the bottom of each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED_TEXT)

    footer_text = (
        "This document is system-generated and is intended for official barangay use only. "
        "Only Released / Returned transactions appear as income."
    )
    canvas.drawCentredString(PAGE_W / 2, 18 * mm, footer_text)
    canvas.drawRightString(PAGE_W - MARGIN, 18 * mm, f"Page {doc.page}")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────

def generate_financial_statement_pdf(
    db: Session,
    date_from: date,
    date_to: date,
    service_filter: Optional[str] = None,
) -> bytes:
    """
    Build and return the financial statement as PDF bytes.

    Parameters
    ----------
    db             : SQLAlchemy session
    date_from      : Start of the report period (inclusive)
    date_to        : End of the report period (inclusive)
    service_filter : One of "documents", "id_services", "equipment", or None (all)
    """
    styles = _build_styles()
    buf    = BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=25 * mm,
        title="Barangay Financial Statement",
        author="Barangay Management System",
    )

    story = []

    # ── Banner ───────────────────────────────────────────────
    story.append(_header_table(styles, date_from, date_to, service_filter))
    story.append(Spacer(1, 10))

    include_docs  = service_filter in (None, "documents")
    include_id    = service_filter in (None, "id_services")
    include_equip = service_filter in (None, "equipment")

    grand_collected = Decimal("0")
    grand_pending   = Decimal("0")

    # ── DOCUMENT SERVICES ────────────────────────────────────
    if include_docs:
        doc_data = _get_document_data(db, date_from, date_to)
        grand_collected += doc_data["total_collected"]
        grand_pending   += doc_data["total_pending"]

        story.append(Paragraph("📄  Document Services", styles["section_heading"]))
        story.append(HRFlowable(width=CONTENT_W, thickness=1, color=SECONDARY,
                                spaceAfter=6, spaceBefore=0))

        if doc_data["transactions"]:
            story.append(_transaction_table_docs(styles, doc_data["transactions"]))
            story.append(Spacer(1, 4))
            story.append(_section_total_row(
                styles, "Document Services",
                doc_data["total_collected"], doc_data["total_pending"]
            ))
        else:
            story.append(_empty_notice(styles, "No document requests found for this period."))

    # ── ID SERVICES ──────────────────────────────────────────
    if include_id:
        id_data = _get_id_application_data(db, date_from, date_to)
        grand_collected += id_data["total_collected"]
        grand_pending   += id_data["total_pending"]

        story.append(Paragraph("🪪  I.D Services", styles["section_heading"]))
        story.append(HRFlowable(width=CONTENT_W, thickness=1, color=SECONDARY,
                                spaceAfter=6, spaceBefore=0))

        if id_data["transactions"]:
            story.append(_transaction_table_id(styles, id_data["transactions"]))
            story.append(Spacer(1, 4))
            story.append(_section_total_row(
                styles, "I.D Services",
                id_data["total_collected"], id_data["total_pending"]
            ))
        else:
            story.append(_empty_notice(styles, "No ID applications found for this period."))

    # ── EQUIPMENT BORROWING ──────────────────────────────────
    if include_equip:
        eq_data = _get_equipment_data(db, date_from, date_to)
        grand_collected += eq_data["total_collected"]
        grand_pending   += eq_data["total_pending"]

        story.append(Paragraph("🔧  Equipment Borrowing", styles["section_heading"]))
        story.append(HRFlowable(width=CONTENT_W, thickness=1, color=SECONDARY,
                                spaceAfter=6, spaceBefore=0))

        if eq_data["transactions"]:
            story.append(_transaction_table_equipment(styles, eq_data["transactions"]))
            story.append(Spacer(1, 4))

            extra = None
            if eq_data["total_refunded"] > 0:
                extra = [("Refunded:", eq_data["total_refunded"], SECONDARY)]

            story.append(_section_total_row(
                styles, "Equipment Borrowing",
                eq_data["total_collected"], eq_data["total_pending"]
            ))
        else:
            story.append(_empty_notice(styles, "No equipment requests found for this period."))

    # ── GRAND TOTAL ──────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width=CONTENT_W, thickness=1.5, color=PRIMARY,
                            spaceAfter=8, spaceBefore=0))

    # Collected / Pending summary row
    summary_data = [[
        Paragraph("Total Collected:", ParagraphStyle(
            "sc_label", fontName="Helvetica-Bold", fontSize=10, textColor=DARK_TEXT, alignment=TA_RIGHT,
        )),
        Paragraph(f"₱ {grand_collected:,.2f}", ParagraphStyle(
            "sc_val", fontName="Helvetica-Bold", fontSize=10, textColor=PRIMARY, alignment=TA_RIGHT,
        )),
        Paragraph("Total Pending:", ParagraphStyle(
            "sp_label", fontName="Helvetica-Bold", fontSize=10, textColor=DARK_TEXT, alignment=TA_RIGHT,
        )),
        Paragraph(f"₱ {grand_pending:,.2f}", ParagraphStyle(
            "sp_val", fontName="Helvetica-Bold", fontSize=10, textColor=GOLD, alignment=TA_RIGHT,
        )),
    ]]
    summary_row = Table(
        summary_data,
        colWidths=[CONTENT_W * 0.25, CONTENT_W * 0.25, CONTENT_W * 0.25, CONTENT_W * 0.25],
    )
    summary_row.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0f4f8")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBEFORE",    (2, 0), (2, -1),  0.5, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(summary_row)
    story.append(Spacer(1, 6))

    # Grand total banner
    story.append(_grand_total_banner(styles, grand_collected))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Note: 'Collected' figures include only transactions with payment_status = Paid. "
        "'Pending' includes all other active transactions regardless of status.",
        styles["note"],
    ))

    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return buf.getvalue()