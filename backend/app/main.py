from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import psycopg2
import os
import csv
from docx import Document
from io import BytesIO

DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@db:5432/kioskdb")

app = FastAPI(title="Kiosk Backend")

def get_conn():
    return psycopg2.connect(DB_URL)

@app.get("/api/residents")
def list_residents(limit: int = 100):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, last_name, first_name, sex_gender, age FROM residents LIMIT %s", (limit,))
            rows = cur.fetchall()
            return [{"id": r[0], "last": r[1], "first": r[2], "sex": r[3], "age": r[4]} for r in rows]

class CertificateRequest(BaseModel):
    resident_id: int

@app.post("/api/generate-certificate")
def generate_certificate(req: CertificateRequest):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT first_name, last_name, brgy FROM residents WHERE id = %s", (req.resident_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Resident not found")
            first, last, brgy = row[0], row[1], row[2]

    # create a simple Word doc
    doc = Document()
    doc.add_heading("Barangay Certificate", level=1)
    doc.add_paragraph(f"This certifies that {first} {last} is a resident of {brgy}.")
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)

    return FileResponse(path_or_bytes=bio.read(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"certificate_{req.resident_id}.docx")
