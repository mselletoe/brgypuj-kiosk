# models.py
from sqlalchemy import Column, Integer, String, Date, SmallInteger, Boolean, ForeignKey, Text, TIMESTAMP, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

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

    # Relationships
    address = relationship("Address", back_populates="resident", uselist=False)
    rfid = relationship("RfidUID", back_populates="resident", uselist=False)

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

    # Relationships
    resident = relationship("Resident", back_populates="address")
    purok = relationship("Purok", back_populates="addresses")

class Purok(Base):
    __tablename__ = "puroks"

    id = Column(SmallInteger, primary_key=True, index=True)
    purok_name = Column(String(8))

    # Relationships
    addresses = relationship("Address", back_populates="purok")

class RfidUID(Base):
    __tablename__ = "rfid_uid"

    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    rfid_uid = Column(String(20), unique=True, nullable=False) 
    status = Column(Text)
    created_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)

    # Relationships
    resident = relationship("Resident", back_populates="rfid")

class BrgyStaff(Base):
    __tablename__ = "brgy_staff"

    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    email = Column(String(64), unique=True, nullable=False)
    password = Column(Text, nullable=False)  # hashed password
    role = Column(String(128))
    created_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)

    # Relationships
    resident = relationship("Resident", backref="staff")

class RequestType(Base):
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True, index=True)
    request_type_name = Column(String(64))
    description = Column(Text)
    status = Column(String(16), default="active")
    price = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship
    template = relationship("Template", back_populates="request_type", uselist=False)

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(64), nullable=False)
    description = Column(Text)
    file = Column(LargeBinary)
    request_type_id = Column(Integer, ForeignKey("request_types.id", ondelete="SET NULL", onupdate="CASCADE"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    request_type = relationship("RequestType", back_populates="template")