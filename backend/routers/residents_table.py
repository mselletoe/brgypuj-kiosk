from fastapi import APIRouter, HTTPException
from db import get_conn

router = APIRouter(prefix="/api/residents", tags=["Residents"])

@router.get("/")
def list_residents(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.id, r.first_name, r.last_name, r.middle_name,
                           ru.rfid_uid, a.unit_blk_street, a.purok, r.phone_number
                    FROM residents r
                    LEFT JOIN addresses a ON a.resident_id = r.id AND a.is_current = TRUE
                    LEFT JOIN rfid_uid ru ON ru.resident_id = r.id AND ru.is_active = TRUE
                    ORDER BY r.id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM residents")
                total = cur.fetchone()[0]

                data = [
                    {
                        "id": r[0],
                        "first_name": r[1],
                        "last_name": r[2],
                        "middle_name": r[3],
                        "rfid_uid": r[4],
                        "unit_blk_street": r[5],
                        "purok": r[6],
                        "phone_number": r[7],
                    }
                    for r in rows
                ]
                return {"data": data, "total": total}

    except Exception as e:
        print("Failed to fetch residents:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch residents")