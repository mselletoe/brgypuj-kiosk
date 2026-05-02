from sqlalchemy import Column, SmallInteger, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Admin(Base):
    __tablename__ = "admin"

    id = Column(SmallInteger, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    position = Column(String(100), nullable=True)           # e.g. "Barangay Secretary", "Treasurer" — cosmetic label
    system_role = Column(String(50), nullable=False, server_default="admin")   # "admin" | "superadmin" — controls permissions
    photo = Column(LargeBinary, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    token_version = Column(Integer, nullable=False, server_default="0")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    resident = relationship("Resident", back_populates="admin_accounts")
    document_requests_processed = relationship("DocumentRequest", back_populates="processed_by_admin")


from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, LargeBinary
from sqlalchemy.sql import func
from app.db.base import Base

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    event_time = Column(String(32))
    location = Column(String(255), nullable=False)
    image = Column(LargeBinary)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


# backend/app/models/audit.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=True) # Optional: link to your admin users table
    action = Column(String(100), nullable=False) # e.g., "Approved Request", "Added Resident"
    details = Column(String(255)) # e.g., "DOC-002 - Barangay Clearance"
    entity_type = Column(String(50)) # e.g., "doc", "equip", "resident", "blotter", "system"
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


from sqlalchemy import (
    Column, Integer, SmallInteger, String, Date,
    ForeignKey, TIMESTAMP, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class BarangayID(Base):
    __tablename__ = "barangay_ids"
    id = Column(Integer, primary_key=True)
    brgy_id_number = Column(String(10), unique=True, nullable=True)
    resident_id = Column(
        Integer,
        ForeignKey("residents.id", ondelete="CASCADE"),
        nullable=False,
    )
    rfid_id = Column(
        Integer,
        ForeignKey("resident_rfid.id", ondelete="SET NULL"),
        nullable=True,
    )
    request_id = Column(
        Integer,
        ForeignKey("document_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    issued_date   = Column(Date, nullable=True)          # date card was released
    expiration_date = Column(Date, nullable=True)        # mirrors ResidentRFID.expiration_date
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    resident = relationship("Resident", back_populates="barangay_ids")
    rfid     = relationship("ResidentRFID", back_populates="barangay_id")
    request  = relationship("DocumentRequest", back_populates="barangay_id")


from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Time
from app.db.base import Base


class BlotterRecord(Base):
    __tablename__ = "blotter_records"

    id = Column(Integer, primary_key=True)
    blotter_no = Column(String(20), unique=True, nullable=False)

    # Complainant (Nagreklamo)
    complainant_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    complainant_name = Column(String(255), nullable=False)
    complainant_age = Column(Integer, nullable=True)
    complainant_address = Column(String(255), nullable=True)

    # Respondent (Inireklamo)
    respondent_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    respondent_name = Column(String(255), nullable=True)
    respondent_age = Column(Integer, nullable=True)
    respondent_address = Column(String(255), nullable=True)

    incident_date = Column(Date, nullable=True)
    incident_time = Column(Time, nullable=True)
    incident_place = Column(String(255), nullable=True)
    incident_type = Column(String(128), nullable=True)
    narrative = Column(Text, nullable=True)
    recorded_by = Column(String(255), nullable=True)
    contact_no = Column(String(16), nullable=True)

    status = Column(String(20), nullable=False, server_default="active")

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    resolved_at = Column(TIMESTAMP, nullable=True)

    complainant = relationship(
        "Resident",
        foreign_keys=[complainant_id],
        back_populates="blotter_records_as_complainant",
    )
    respondent = relationship(
        "Resident",
        foreign_keys=[respondent_id],
        back_populates="blotter_records_as_respondent",
    )


from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class ContactInformation(Base):
    __tablename__ = "contact_information"

    id = Column(Integer, primary_key=True, default=1)
    emergency_number = Column(String(20), nullable=False, server_default="911")
    emergency_desc = Column(String(255), server_default="For life-threatening emergencies")
    phone = Column(String(50), server_default="")
    email = Column(String(255), server_default="")
    office_hours = Column(String(255), server_default="Monday to Friday, 8:00 AM - 5:00 PM")
    address = Column(Text, server_default="")
    tech_support = Column(Text, server_default="")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


from sqlalchemy import Column, SmallInteger, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, Numeric, LargeBinary, FetchedValue, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(SmallInteger, primary_key=True)
    doctype_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), server_default="0.00")
    file = Column(LargeBinary)
    fields = Column(JSON, server_default="'[]'")
    is_available = Column(Boolean, nullable=False, server_default="true")
    requirements = Column(JSON, server_default="'[]'")
    is_id_application = Column(Boolean, nullable=False, server_default="false")

    document_requests = relationship("DocumentRequest", back_populates="doctype")

    @property
    def has_template(self) -> bool:
        return bool(self.file and len(self.file) > 0)

class DocumentRequest(Base):
    __tablename__ = "document_requests"

    id = Column(Integer, primary_key=True)
    transaction_no = Column(String(20), unique=True, nullable=False, server_default=FetchedValue())
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    doctype_id = Column(SmallInteger, ForeignKey("document_types.id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=False, server_default="0.00")
    processed_by = Column(SmallInteger, ForeignKey("admin.id", ondelete="SET NULL"))
    status = Column(
        String(32), 
        CheckConstraint("status IN ('Pending', 'Approved', 'Ready', 'Released', 'Rejected')"),
        nullable=False, 
        server_default="Pending"
    )
    payment_status = Column(
        String(20), 
        CheckConstraint("payment_status IN ('unpaid', 'paid')"),
        nullable=False, 
        server_default="unpaid"
    )
    form_data = Column(JSONB)
    request_file_path = Column(Text)
    requested_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    notes = Column(Text, nullable=True)

    resident = relationship("Resident", back_populates="document_requests")
    doctype = relationship("DocumentType", back_populates="document_requests")
    processed_by_admin = relationship("Admin", back_populates="document_requests_processed")
    barangay_id = relationship("BarangayID", back_populates="request", uselist=False)


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


from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True)
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"))
    category = Column(
        String(50), 
        CheckConstraint("category IN ('Service Quality', 'Interface Design', 'System Speed', 'Accessibility', 'General Experience')"),
        nullable=False
    )
    rating = Column(
        Integer, 
        CheckConstraint("rating >= 1 AND rating <= 5"),
        nullable=False
    )
    additional_comments = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    resident = relationship("Resident", back_populates="feedbacks")


class RFIDReport(Base):
    __tablename__ = "rfid_reports"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"))
    status = Column(String(32), default="Pending")
    created_at = Column(TIMESTAMP, server_default=func.now())

    resident = relationship("Resident", back_populates="rfid_reports")


from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base  # adjust import to match your project

class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    type       = Column(String(50), nullable=False)   # Document, Equipment, Feedback, etc.
    msg        = Column(Text, nullable=False)
    is_read    = Column(Boolean, default=False)
    event = Column(String, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


from sqlalchemy import Column, Integer, SmallInteger, String, Date, Boolean, TIMESTAMP, DateTime, CheckConstraint, ForeignKey, LargeBinary
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
    rfid_pin = Column(String(255), nullable=False)
    failed_pin_attempts = Column(Integer, nullable=False, default=0, server_default='0')
    locked_until = Column(DateTime(timezone=True), nullable=True)
    photo = Column(LargeBinary, nullable=True)
    registered_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    blotter_records_as_complainant = relationship("BlotterRecord", foreign_keys="BlotterRecord.complainant_id", back_populates="complainant")
    blotter_records_as_respondent = relationship("BlotterRecord", foreign_keys="BlotterRecord.respondent_id", back_populates="respondent")
    addresses = relationship("Address", back_populates="resident", cascade="all, delete")
    rfids = relationship("ResidentRFID", back_populates="resident", cascade="all, delete")
    barangay_ids = relationship("BarangayID", back_populates="resident", cascade="all, delete-orphan")
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
    expiration_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")

    resident = relationship("Resident", back_populates="rfids")
    barangay_id = relationship("BarangayID", back_populates="rfid", uselist=False)


from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id         = Column(Integer, primary_key=True)
    message    = Column(Text, nullable=False)
    mode       = Column(String(64), nullable=False)   # 'groups' | 'puroks' | 'specific'
    recipients = Column(Integer, nullable=False, default=0)
    sent_at    = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

