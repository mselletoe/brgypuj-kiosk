"""
================================================================================
File: models.py
Description:
    This module defines the SQLAlchemy ORM models.
    It maps Python Classes to Database Tables.
    
    Entities covered:
      - Resident: Personal info.
      - Address: Location details linked to Residents.
      - BrgyStaff: Admin accounts (linked to Residents).
      - RequestType/Template: Configuration for document requests.
      - EquipmentInventory/Request: Management of borrowable items.
================================================================================
"""

from sqlalchemy import Column, Integer, String, Date, SmallInteger, Boolean, ForeignKey, Text, TIMESTAMP, LargeBinary, DateTime, JSON, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
import enum

# ... (Resident, Address, Purok, RfidUID models are unchanged) ...

# ==============================================================================
# Model: Resident
# ==============================================================================
class Resident(Base):
    __tablename__ = "residents"
    id = Column(SmallInteger, primary_key=True, index=True)
    last_name = Column(String(128))
    first_name = Column(String(128))
    middle_name = Column(String(128))
    suffix = Column(String(8))
    gender = Column(Text)
    birthdate = Column(Date)
    years_residency = Column(SmallInteger)
    email = Column(String(64), unique=True)
    phone_number = Column(String(11))
    account_pin = Column(Text)
    created_at = Column(TIMESTAMP)
    address = relationship("Address", back_populates="resident", uselist=False)
    rfid = relationship("RfidUID", back_populates="resident", uselist=False)

# ==============================================================================
# Model: Address
# ==============================================================================
class Address(Base):
    __tablename__ = "addresses"
    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    unit_blk_street = Column(String(255))
    purok_id = Column(SmallInteger, ForeignKey("puroks.id", ondelete="SET NULL", onupdate="CASCADE"))
    barangay = Column(String(64))
    municipality = Column(String(16))
    province = Column(String(16))
    region = Column(String(64))
    created_at = Column(TIMESTAMP)
    is_current = Column(Boolean, default=True)
    resident = relationship("Resident", back_populates="address")
    purok = relationship("Purok", back_populates="addresses")

# ==============================================================================
# Model: Purok
# ==============================================================================
class Purok(Base):
    __tablename__ = "puroks"
    id = Column(SmallInteger, primary_key=True, index=True)
    purok_name = Column(String(8))
    addresses = relationship("Address", back_populates="purok")

# ==============================================================================
# Model: RfidUID
# ==============================================================================
class RfidUID(Base):
    __tablename__ = "rfid_uid"
    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    rfid_uid = Column(String(20), unique=True, nullable=False) 
    status = Column(Text)
    created_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    resident = relationship("Resident", back_populates="rfid")

# ==============================================================================
# Model: BrgyStaff (UPDATED)
# ==============================================================================
class BrgyStaff(Base):
    __tablename__ = "brgy_staff"

    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False) # <-- REQUIRED
    staff_name = Column(String(255), nullable=True) 
    email = Column(String(64), unique=True, nullable=False) # <-- REQUIRED
    password = Column(Text, nullable=False)  # <-- REQUIRED
    role = Column(String(128), nullable=False) # <-- REQUIRED
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    resident = relationship("Resident", backref="staff")

# ... (Rest of the models: RequestType, Template, Equipment, etc. are unchanged) ...

# ==============================================================================
# Model: RequestType
# ==============================================================================
class RequestType(Base):
    __tablename__ = "request_types"
    id = Column(Integer, primary_key=True, index=True)
    request_type_name = Column(String(64))
    description = Column(Text)
    status = Column(String(16), default="active")
    price = Column(Integer, default=0)
    fields = Column(JSON, nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    template = relationship("Template", back_populates="request_type", uselist=False)

# ==============================================================================
# Model: Template
# ==============================================================================
class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(64), nullable=False)
    description = Column(Text)
    file = Column(LargeBinary)
    file_name = Column(String(128))
    request_type_id = Column(Integer, ForeignKey("request_types.id", ondelete="SET NULL", onupdate="CASCADE"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    request_type = relationship("RequestType", back_populates="template")

# ==============================================================================
# Model: EquipmentInventory
# ==============================================================================
class EquipmentInventory(Base):
    __tablename__ = "equipment_inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    total_quantity = Column(Integer, nullable=False, default=0)
    available_quantity = Column(Integer, nullable=False, default=0)
    rate = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    rate_per = Column(String(16), default='day')
    request_items = relationship("EquipmentRequestItem", back_populates="item")

# ==============================================================================
# Model: EquipmentRequest
# ==============================================================================
class EquipmentRequest(Base):
    __tablename__ = "equipment_requests"
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    borrower_name = Column(String(255), nullable=False)
    contact_number = Column(String(16))
    purpose = Column(String(255))
    notes = Column(Text, nullable=True)
    borrow_date = Column(TIMESTAMP(timezone=True), nullable=False)
    return_date = Column(TIMESTAMP(timezone=True), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    requested_via = Column(String(64))
    status = Column(String(32), default='Pending')
    paid = Column(Boolean, default=False)
    refunded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    resident = relationship("Resident", backref="equipment_requests")
    items = relationship("EquipmentRequestItem", back_populates="request")

# ==============================================================================
# Model: EquipmentRequestItem (Join Table)
# ==============================================================================
class EquipmentRequestItem(Base):
    __tablename__ = "equipment_request_items"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("equipment_requests.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("equipment_inventory.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    request = relationship("EquipmentRequest", back_populates="items")
    item = relationship("EquipmentInventory", back_populates="request_items")

# ==============================
# Request Status
# ==============================
class RequestStatus(Base):
    __tablename__ = "request_status"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    requests = relationship("Request", back_populates="status_obj")

# ==============================
# Requests
# ==============================
class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    request_type_id = Column(Integer, ForeignKey("request_types.id", ondelete="CASCADE", onupdate="CASCADE"))
    processed_by = Column(SmallInteger, ForeignKey("brgy_staff.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    rejected_by = Column(SmallInteger, ForeignKey("brgy_staff.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    request_file = Column(LargeBinary, nullable=True)
    status_id = Column(Integer, ForeignKey("request_status.id", ondelete="SET NULL"), nullable=False)
    form_data = Column(JSON, nullable=True)
    payment_status = Column(String(16), default="Unpaid")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    status_obj = relationship("RequestStatus", back_populates="requests")
    resident = relationship("Resident", backref="requests")
    request_type = relationship("RequestType", backref="requests")
    processed_staff = relationship("BrgyStaff", foreign_keys=[processed_by])
    rejected_staff = relationship("BrgyStaff", foreign_keys=[rejected_by])

# ==============================================================================
# Model: Announcement
# ==============================================================================
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)
    event_day = Column(String(32), nullable=True)
    event_time = Column(String(32), nullable=True)
    location = Column(String(255), nullable=False)
    image = Column(LargeBinary, nullable=True)   # Store uploaded image as binary
    image_name = Column(String(255), nullable=True)  # Keep original filename
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
