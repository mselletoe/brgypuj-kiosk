from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class EquipmentInventory(Base):
    __tablename__ = "equipment_inventory"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    total_quantity = Column(Integer, default=0, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    rate_per_day = Column(DECIMAL(10,2), default=0.00, nullable=False)


class EquipmentRequest(Base):
    __tablename__ = "equipment_requests"

    id = Column(Integer, primary_key=True)
    transaction_no = Column(String(20), unique=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"))
    borrower_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    contact_number = Column(String(16))
    purpose = Column(String(255))
    status = Column(String(32), default="Pending")
    notes = Column(Text)
    borrow_date = Column(TIMESTAMP, nullable=False)
    return_date = Column(TIMESTAMP, nullable=False)
    returned_at = Column(TIMESTAMP)
    total_cost = Column(DECIMAL(10,2), default=0.00)
    payment_status = Column(String(20), default="unpaid")
    is_refunded = Column(Boolean, default=False)
    requested_at = Column(TIMESTAMP, server_default=func.now())

    resident = relationship("Resident", back_populates="equipment_requests")
    items = relationship("EquipmentRequestItem", back_populates="equipment_request", cascade="all, delete-orphan")


class EquipmentRequestItem(Base):
    __tablename__ = "equipment_request_items"

    id = Column(Integer, primary_key=True)
    equipment_request_id = Column(Integer, ForeignKey("equipment_requests.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("equipment_inventory.id", ondelete="RESTRICT"))
    quantity = Column(Integer, default=1)

    equipment_request = relationship("EquipmentRequest", back_populates="items")