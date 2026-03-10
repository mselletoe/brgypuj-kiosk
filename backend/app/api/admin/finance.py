"""
Financial Statement API
------------------------
Provides a single PDF export endpoint used by the admin dashboard
to generate and download a financial statement for the treasurer.

Accessible by both Admin and Superadmin roles.
(Either admin on duty can export — treasurer doesn't have a system login.)

Route map (prefix: /admin/financial)
--------------------------------------
  GET /statement/export  — returns a PDF file as a download

Query parameters
----------------
  date_from   : YYYY-MM-DD  (required)
  date_to     : YYYY-MM-DD  (required)
  service     : "documents" | "id_services" | "equipment" | omit for all
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.services.finance_service import generate_financial_statement_pdf

router = APIRouter(prefix="/finance")


@router.get(
    "/statement/export",
    summary="[Admin] Export financial statement as PDF",
    description=(
        "Generates a PDF financial statement covering Document Services, "
        "I.D Services, and/or Equipment Borrowing for a given date range. "
        "Accessible by all admin roles."
    ),
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF file download",
        }
    },
)
def export_financial_statement(
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to:   date = Query(..., description="End date   (YYYY-MM-DD)"),
    service:   Optional[str] = Query(
        None,
        description="Filter: 'documents', 'id_services', 'equipment', or omit for all",
    ),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),   # any authenticated admin
):
    # Basic date validation
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be on or before date_to",
        )

    # Service filter validation
    allowed_services = {"documents", "id_services", "equipment", None}
    if service not in allowed_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service filter '{service}'. Use: documents, id_services, equipment",
        )

    pdf_bytes = generate_financial_statement_pdf(
        db=db,
        date_from=date_from,
        date_to=date_to,
        service_filter=service,
    )

    # Build a descriptive filename
    service_slug = service or "all-services"
    filename = (
        f"financial-statement_{service_slug}"
        f"_{date_from.strftime('%Y%m%d')}-{date_to.strftime('%Y%m%d')}.pdf"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )