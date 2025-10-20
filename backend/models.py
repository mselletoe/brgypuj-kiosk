# models.py
from sqlalchemy import Column, Integer, String, Date, SmallInteger, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

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

    resident = relationship("Resident", back_populates="address")
    purok = relationship("Purok", back_populates="addresses")

class Purok(Base):
    __tablename__ = "puroks"

    id = Column(SmallInteger, primary_key=True, index=True)
    purok_name = Column(String(8))

    addresses = relationship("Address", back_populates="purok")

class RfidUID(Base):
    __tablename__ = "rfid_uid"

    id = Column(SmallInteger, primary_key=True, index=True)
    resident_id = Column(SmallInteger, ForeignKey("residents.id", ondelete="CASCADE", onupdate="CASCADE"))
    rfid_uid = Column(String(9), unique=True)
    status = Column(Text)
    created_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)

    resident = relationship("Resident", back_populates="rfid")