from sqlalchemy import Column, Integer, SmallInteger, String, Date, Boolean, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Purok(Base):
    __tablename__ = "puroks"

    id = Column(SmallInteger, primary_key=True)
    purok_name = Column(String(16), nullable=False, unique=True)

    addresses = relationship("Address", back_populates="purok")


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True)
    last_name = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=False)
    middle_name = Column(String(128))
    suffix = Column(String(8))
    gender = Column(String(10), CheckConstraint("gender IN ('male', 'female', 'other')"), nullable=False)
    birthdate = Column(Date, nullable=False)
    residency_start_date = Column(Date, server_default=func.current_date(), nullable=False)
    email = Column(String(255), unique=True)
    phone_number = Column(String(15))
    rfid_pin = Column(String(255))
    registered_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    addresses = relationship("Address", back_populates="resident", cascade="all, delete")
    rfids = relationship("ResidentRFID", back_populates="resident", cascade="all, delete")
    admin_accounts = relationship("Admin", back_populates="resident")
    feedbacks = relationship("Feedback", back_populates="resident", cascade="all, delete-orphan")
    rfid_reports = relationship("RFIDReport", back_populates="resident", cascade="all, delete-orphan")
    document_requests = relationship("DocumentRequest", back_populates="resident", cascade="all, delete-orphan")
    equipment_requests = relationship("EquipmentRequest", back_populates="resident", cascade="all, delete-orphan")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    house_no_street = Column(String(255), nullable=False)
    purok_id = Column(SmallInteger, ForeignKey("puroks.id", ondelete="RESTRICT"), nullable=False)
    barangay = Column(String(64), server_default="Poblacion Uno")
    municipality = Column(String(16), server_default="Amadeo")
    province = Column(String(16), server_default="Cavite")
    region = Column(String(64), server_default="Region IV-A")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    is_current = Column(Boolean, nullable=False, server_default="true")

    resident = relationship("Resident", back_populates="addresses")
    purok = relationship("Purok", back_populates="addresses")


class ResidentRFID(Base):
    __tablename__ = "resident_rfid"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    rfid_uid = Column(String(16), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_active = Column(Boolean, nullable=False, server_default="true")

    resident = relationship("Resident", back_populates="rfids")