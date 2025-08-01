from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer, text
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

# ✅ CORREÇÃO: Configuração robusta para Vercel
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

def get_database_url():
    """Obtém URL do banco de dados com fallbacks robustos"""
    
    # 🔍 DEBUG: Log de todas as configurações
    print(f"🔍 [DEBUG] IS_VERCEL: {IS_VERCEL}")
    print(f"🔍 [DEBUG] settings.database_url: {settings.database_url}")
    print(f"🔍 [DEBUG] settings.supabase_url: {settings.supabase_url}")
    print(f"🔍 [DEBUG] settings.supabase_anon_key: {'[DEFINIDO]' if settings.supabase_anon_key else '[VAZIO]'}")
    print(f"🔍 [DEBUG] settings.supabase_service_role_key: {'[DEFINIDO]' if settings.supabase_service_role_key else '[VAZIO]'}")
    
    # 1. Tentar DATABASE_URL direto (se definido)
    if settings.database_url:
        print(f"✅ [DEBUG] Usando DATABASE_URL: {settings.database_url[:50]}...")
        return settings.database_url
    
    # 2. Construir URL do Supabase se configurado
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            # Extrair host do Supabase URL
            host = settings.supabase_url.replace('https://', '').replace('http://', '')
            # Construir URL PostgreSQL correta usando SERVICE_ROLE_KEY
            url = f"postgresql://postgres.{host.split('.')[0]}:{settings.supabase_service_role_key}@{host}:5432/postgres"
            print(f"✅ [DEBUG] Construindo URL Supabase: postgresql://postgres.{host.split('.')[0]}:[KEY]@{host}:5432/postgres")
            return url
        except Exception as e:
            print(f"❌ Erro ao construir URL Supabase: {e}")
    
    # 3. Fallback para SQLite local
    if IS_VERCEL:
        # No Vercel, usar SQLite em /tmp
        sqlite_path = "/tmp/chatbot_vercel.db"
        print(f"⚠️ [DEBUG] FALLBACK: Usando SQLite no Vercel: {sqlite_path}")
    else:
        sqlite_path = Path("chatbot_local.db")
        print(f"⚠️ [DEBUG] FALLBACK: Usando SQLite local: {sqlite_path}")
    
    return f"sqlite:///{sqlite_path}"

# ✅ CORREÇÃO: Configuração da engine com tratamento robusto
try:
    database_url = get_database_url()
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    if database_url.startswith('sqlite'):
        # ✅ CORREÇÃO: Configuração SQLite para Vercel
        if IS_VERCEL:
            # No Vercel, usar /tmp
            engine = create_engine(
                database_url, 
                connect_args={"check_same_thread": False},
                pool_pre_ping=True
            )
        else:
            engine = create_engine(
                database_url, 
                connect_args={"check_same_thread": False}
            )
        print("📁 Usando banco SQLite")
    else:
        # PostgreSQL com configuração robusta e fallback
        try:
            print("🔄 Tentando conectar ao PostgreSQL/Supabase...")
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=60,
                pool_timeout=5,
                connect_args={
                    "connect_timeout": 3,  # Timeout rápido para falhar cedo
                    "options": "-c statement_timeout=10000"
                },
                echo=False
            )
            # Testar conexão rapidamente
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL/Supabase conectado com sucesso!")
            
        except Exception as pg_error:
            print(f"⚠️ PostgreSQL falhou: {pg_error}")
            print("🔄 Usando fallback SQLite...")
            
            # Fallback para SQLite
            sqlite_path = Path("chatbot_fallback.db")
            fallback_url = f"sqlite:///{sqlite_path}"
            engine = create_engine(
                fallback_url, 
                connect_args={"check_same_thread": False},
                echo=False
            )
            print(f"✅ Fallback SQLite ativo: {fallback_url}")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # ✅ CORREÇÃO: Criar tabelas apenas se necessário
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados configurado com sucesso")
    except Exception as create_error:
        print(f"⚠️ Erro ao criar tabelas: {create_error}")
        print("🔄 Continuando sem criar tabelas...")
    
except Exception as e:
    print(f"❌ Erro ao configurar banco: {e}")
    print("🔄 Usando configuração de fallback...")
    
    # ✅ CORREÇÃO: Fallback robusto
    try:
        if IS_VERCEL:
            fallback_url = "sqlite:////tmp/chatbot_fallback.db"
        else:
            fallback_url = "sqlite:///chatbot_fallback.db"
        
        engine = create_engine(
            fallback_url, 
            connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Tentar criar tabelas no fallback
        try:
            Base.metadata.create_all(bind=engine)
            print("💾 Banco de fallback configurado com sucesso")
        except Exception as fallback_error:
            print(f"⚠️ Erro ao criar tabelas no fallback: {fallback_error}")
            print("🔄 Usando mock database...")
            # Se tudo falhar, usar mock
            engine = None
            SessionLocal = None
            
    except Exception as fallback_e:
        print(f"❌ Erro no fallback: {fallback_e}")
        print("🔄 Usando mock database...")
        engine = None
        SessionLocal = None

# ✅ CORREÇÃO: Mock database melhorado
class MockDB:
    def __init__(self):
        self.conversations = []
        self.appointments = []
        self.waiting_list = []
        print("🎭 Usando Mock Database")

    def add(self, obj):
        if hasattr(obj, 'id') and not obj.id:
            obj.id = str(uuid.uuid4())
        if hasattr(obj, 'created_at') and not obj.created_at:
            obj.created_at = datetime.utcnow()
        if hasattr(obj, 'updated_at'):
            obj.updated_at = datetime.utcnow()
        
        # Adicionar à lista apropriada
        if isinstance(obj, Conversation):
            self.conversations.append(obj)
        elif isinstance(obj, Appointment):
            self.appointments.append(obj)
        elif isinstance(obj, WaitingList):
            self.waiting_list.append(obj)

    def commit(self):
        print("💾 Mock commit realizado")

    def close(self):
        print("🔒 Mock database fechado")

    def query(self, model):
        return MockQuery(model, self)

    def refresh(self, obj):
        print("🔄 Mock refresh realizado")

class MockQuery:
    def __init__(self, model, db):
        self.model = model
        self.db = db
        self._filter_conditions = []

    def filter(self, condition):
        self._filter_conditions.append(condition)
        return self

    def filter_by(self, **kwargs):
        # Simular filter_by para compatibilidade
        self._filter_conditions.append(kwargs)
        return self

    def first(self):
        # Buscar na lista de conversas se for Conversation
        if self.model == Conversation:
            for conv in self.db.conversations:
                # Simular filtro simples
                if hasattr(conv, 'phone'):
                    return conv
        return None

    def all(self):
        # Retornar lista vazia
        return []

def get_db():
    """Retorna sessão do banco de dados"""
    if SessionLocal:
        try:
            db = SessionLocal()
            return db
        except Exception as e:
            print(f"❌ Erro ao criar sessão: {e}")
            return MockDB()
    else:
        return MockDB() 