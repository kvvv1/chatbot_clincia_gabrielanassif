from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from app.config import settings
import os

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

def get_supabase_url():
    """Obtém URL do Supabase das variáveis de ambiente"""
    return os.getenv('SUPABASE_URL')

def get_supabase_key():
    """Obtém chave do Supabase das variáveis de ambiente"""
    return os.getenv('SUPABASE_ANON_KEY')

def get_supabase_engine():
    """Cria engine do Supabase"""
    supabase_url = get_supabase_url()
    supabase_key = get_supabase_key()
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem ser configurados")
    
    # Formato: postgresql://postgres:[password]@[host]:5432/postgres
    database_url = f"postgresql://postgres:{supabase_key}@{supabase_url.replace('https://', '').replace('http://', '')}:5432/postgres"
    
    return create_engine(database_url)

# Database setup
try:
    if settings.environment == "production":
        engine = get_supabase_engine()
    else:
        engine = create_engine(settings.database_url)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  Aviso: Não foi possível conectar ao banco de dados: {e}")
    print("💡 Para desenvolvimento, você pode usar SQLite ou PostgreSQL via Docker")
    engine = None
    SessionLocal = None

def get_db():
    if SessionLocal is None:
        # Mock database for development
        class MockDB:
            def __init__(self):
                self.data = {}
            
            def add(self, obj):
                if not hasattr(self, 'conversations'):
                    self.conversations = []
                self.conversations.append(obj)
                return obj
            
            def commit(self):
                pass
            
            def close(self):
                pass
        
        db = MockDB()
        try:
            yield db
        finally:
            db.close()
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close() 