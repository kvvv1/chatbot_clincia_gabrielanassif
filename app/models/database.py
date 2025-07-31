from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os
from pathlib import Path
from app.config import settings

# Importar novas tabelas de auditoria
from app.models.patient_transaction import (
    PatientTransaction, PatientCache, ContextHistory, 
    DecisionLog, ValidationRule
)

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

# Database setup - Simplificado para Vercel
# Configuração robusta do banco de dados
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

def get_database_url():
    """Obtém URL do banco de dados com fallbacks robustos"""
    
    # 1. Tentar DATABASE_URL direto (se definido)
    if settings.database_url:
        return settings.database_url
    
    # 2. Construir URL do Supabase se configurado
    if settings.supabase_url and settings.supabase_anon_key:
        # Extrair host do Supabase URL
        host = settings.supabase_url.replace('https://', '').replace('http://', '')
        return f"postgresql://postgres.{host.split('.')[0]}:@{host}:5432/postgres"
    
    # 3. Fallback para SQLite local
    sqlite_path = Path("chatbot_local.db")
    return f"sqlite:///{sqlite_path.absolute()}"

# Configuração da engine
try:
    database_url = get_database_url()
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    if database_url.startswith('sqlite'):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        print("📁 Usando banco SQLite local")
    else:
        engine = create_engine(database_url)
        print("☁️ Usando banco na nuvem")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados configurado com sucesso")
    
except Exception as e:
    print(f"❌ Erro ao configurar banco: {e}")
    print("🔄 Usando configuração de fallback...")
    
    # Fallback final: SQLite in-memory
    engine = create_engine("sqlite:///chatbot_fallback.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    print("💾 Usando banco SQLite de fallback")
# Configuração já realizada acima na seção robusta

def get_db():
    if SessionLocal is None:
        # Mock database for development/Vercel
        class MockDB:
            def __init__(self):
                self.data = {}
                self.conversations = []
                self.appointments = []
                self.waiting_list = []
            
            def add(self, obj):
                if hasattr(obj, '__tablename__'):
                    if obj.__tablename__ == 'conversations':
                        self.conversations.append(obj)
                    elif obj.__tablename__ == 'appointments':
                        self.appointments.append(obj)
                    elif obj.__tablename__ == 'waiting_list':
                        self.waiting_list.append(obj)
                return obj
            
            def commit(self):
                pass
            
            def close(self):
                pass
            
            def query(self, model):
                return MockQuery(model, self)
        
        class MockQuery:
            def __init__(self, model, db):
                self.model = model
                self.db = db
                self._filter_conditions = []
                self._filter_by_conditions = {}
            
            def filter(self, condition):
                self._filter_conditions.append(condition)
                return self
            
            def filter_by(self, **kwargs):
                # Simular filter_by para compatibilidade
                self._filter_by_conditions.update(kwargs)
                return self
            
            def first(self):
                # Buscar na lista de conversas se for Conversation
                if self.model.__name__ == 'Conversation':
                    phone = self._filter_by_conditions.get('phone')
                    if phone:
                        for conv in self.db.conversations:
                            if conv.phone == phone:
                                return conv
                return None
            
            def all(self):
                # Retornar lista vazia
                return []
        
        return MockDB()
    else:
        return SessionLocal()

def get_session():
    """Obtém sessão do banco de dados - versão contextmanager"""
    if SessionLocal is None:
        # Mock database for development/Vercel
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