from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base
from datetime import datetime

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    radius_m = Column(Integer)
    capacity = Column(Integer)

class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    vehicle_plate = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    zone = relationship("Zone")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, unique=True)
    country = Column(String)

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lat = Column(Float)
    lng = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)