from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Announcement
from datetime import date
from typing import List
import io
import base64

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"]
)

def serialize_announcement(a):
    return {
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "event_date": a.event_date,
        "event_day": a.event_day,
        "event_time": a.event_time,
        "location": a.location,
        "image": base64.b64encode(a.image).decode("utf-8") if a.image else None,
        "image_name": a.image_name,
        "created_at": a.created_at,
    }

# CREATE
@router.post("/")
async def create_announcement(
    title: str = Form(...),
    description: str = Form(None),
    event_date: date = Form(...),
    event_day: str = Form(None),
    event_time: str = Form(None),
    location: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_data = await image.read() if image else None
    new_announcement = Announcement(
        title=title,
        description=description,
        event_date=event_date,
        event_day=event_day,
        event_time=event_time,
        location=location,
        image=image_data,
        image_name=image.filename if image else None
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return {"message": "Announcement created successfully", "id": new_announcement.id}

# READ ALL
@router.get("/")
def get_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).order_by(Announcement.event_date.desc()).all()
    return [serialize_announcement(a) for a in announcements]

# READ SINGLE
@router.get("/{announcement_id}")
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return serialize_announcement(announcement)

# DELETE
@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(announcement)
    db.commit()
    return {"message": "Announcement deleted successfully"}
