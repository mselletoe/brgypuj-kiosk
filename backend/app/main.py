from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = "postgresql://admin:admin7890@localhost:5432/kioskdb"

app = FastAPI(title="Kiosk Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        raise

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}

@app.get("/api/residents")
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
