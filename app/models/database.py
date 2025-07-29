from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from app.config import settings

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, nullable=False, index=True)
    state = Column(String, default="inicio")
    context = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False)
    patient_name = Column(String)
    patient_phone = Column(String)
    appointment_date = Column(DateTime)
    appointment_type = Column(String)
    status = Column(String, default="scheduled")
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WaitingList(Base):
    __tablename__ = "waiting_list"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False)
    patient_name = Column(String)
    patient_phone = Column(String)
    preferred_dates = Column(JSON)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 