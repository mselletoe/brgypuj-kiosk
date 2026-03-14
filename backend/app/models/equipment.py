from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, Text, Numeric, CheckConstraint, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class EquipmentInventory(Base):
    __tablename__ = "equipment_inventory"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    total_quantity = Column(Integer, nullable=False, server_default="0")
    available_quantity = Column(Integer, nullable=False, server_default="0")
    rate_per_day = Column(Numeric(10, 2), nullable=False, server_default="0.00")

    __table_args__ = (
        CheckConstraint(
            "available_quantity >= 0 AND available_quantity <= total_quantity", 
            name="chk_available_range"
        ),
    )


class EquipmentRequest(Base):
    __tablename__ = "equipment_requests"

    id = Column(Integer, primary_key=True)
    transaction_no = Column(String(20), unique=True, nullable=False, server_default=FetchedValue())
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="RESTRICT"), nullable=False)
    contact_person = Column(String(255))
    contact_number = Column(String(16))
    purpose = Column(String(255))
    status = Column(
        String(32), 
        CheckConstraint("status IN ('Pending', 'Approved', 'Picked-Up', 'Returned', 'Rejected')"),
        server_default="Pending"
    )
    notes = Column(Text)
    borrow_date = Column(TIMESTAMP(timezone=True), nullable=False)
    return_date = Column(TIMESTAMP(timezone=True), nullable=False)
    returned_at = Column(TIMESTAMP(timezone=True))
    total_cost = Column(Numeric(10, 2), nullable=False, server_default="0.00")
    payment_status = Column(
        String(20), 
        CheckConstraint("payment_status IN ('unpaid', 'paid')"),
        server_default="unpaid"
    )
    is_refunded = Column(Boolean, nullable=False, server_default="false")
    requested_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    resident = relationship("Resident", back_populates="equipment_requests")
    items = relationship("EquipmentRequestItem", back_populates="equipment_request", cascade="all, delete-orphan")


class EquipmentRequestItem(Base):
    __tablename__ = "equipment_request_items"

    id = Column(Integer, primary_key=True)
    equipment_request_id = Column(Integer, ForeignKey("equipment_requests.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("equipment_inventory.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(
        Integer, 
        CheckConstraint("quantity > 0"), 
        nullable=False, 
        server_default="1"
    )

    equipment_request = relationship("EquipmentRequest", back_populates="items")
    inventory_item = relationship("EquipmentInventory")