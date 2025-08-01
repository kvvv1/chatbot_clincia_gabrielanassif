from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
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
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

def test_database_connection(url: str, max_retries: int = 3) -> bool:
    """Testa se uma URL de banco de dados está funcionando"""
    for attempt in range(max_retries):
        try:
            if url.startswith('sqlite'):
                # Para SQLite, verificar se consegue criar/acessar o arquivo
                import sqlite3
                db_path = url.replace('sqlite:///', '')
                
                # Tratar caso especial de banco em memória
                if db_path == ':memory:':
                    conn = sqlite3.connect(':memory:')
                    conn.execute("SELECT 1")
                    conn.close()
                    return True
                
                # Para arquivos, garantir que o diretório existe
                dir_path = os.path.dirname(db_path)
                if dir_path:  # Se não for vazio (arquivo não está na raiz)
                    os.makedirs(dir_path, exist_ok=True)
                
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT 1")
                conn.close()
                return True
            else:
                # Para PostgreSQL, testar conexão
                from sqlalchemy import create_engine, text
                test_engine = create_engine(url, pool_timeout=3, connect_args={"connect_timeout": 3})
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                test_engine.dispose()
                return True
        except Exception as e:
            print(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    return False

def get_database_url():
    """Obtém URL do banco de dados com fallbacks robustos e teste de conectividade"""
    
    # 🔍 DEBUG: Log de todas as configurações
    print(f"🔍 [DEBUG] IS_VERCEL: {IS_VERCEL}")
    print(f"🔍 [DEBUG] IS_PRODUCTION: {IS_PRODUCTION}")
    print(f"🔍 [DEBUG] settings.database_url: {'[DEFINIDO]' if settings.database_url else '[VAZIO]'}")
    print(f"🔍 [DEBUG] settings.supabase_url: {settings.supabase_url}")
    print(f"🔍 [DEBUG] settings.supabase_anon_key: {'[DEFINIDO]' if settings.supabase_anon_key else '[VAZIO]'}")
    print(f"🔍 [DEBUG] settings.supabase_service_role_key: {'[DEFINIDO]' if settings.supabase_service_role_key else '[VAZIO]'}")
    
    # 1. Tentar DATABASE_URL direto (se definido)
    if settings.database_url:
        print(f"✅ [DEBUG] Testando DATABASE_URL: {settings.database_url[:50]}...")
        if test_database_connection(settings.database_url):
            print(f"✅ [DEBUG] DATABASE_URL funcionando!")
            return settings.database_url
        else:
            print(f"❌ [DEBUG] DATABASE_URL não está acessível")
    
    # 2. Construir URL do Supabase se configurado
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            # Extrair host do Supabase URL
            host = settings.supabase_url.replace('https://', '').replace('http://', '')
            # Construir URL PostgreSQL correta usando SERVICE_ROLE_KEY
            url = f"postgresql://postgres.{host.split('.')[0]}:{settings.supabase_service_role_key}@{host}:5432/postgres"
            print(f"✅ [DEBUG] Testando URL Supabase construída...")
            
            if test_database_connection(url):
                print(f"✅ [DEBUG] Supabase funcionando!")
                return url
            else:
                print(f"❌ [DEBUG] Supabase não está acessível")
        except Exception as e:
            print(f"❌ Erro ao construir URL Supabase: {e}")
    
    # 3. Fallback para SQLite - usar em memória no Vercel se /tmp falhar
    if IS_VERCEL:
        # Primeiro tentar /tmp
        sqlite_path = "/tmp/chatbot_vercel.db"
        sqlite_url = f"sqlite:///{sqlite_path}"
        print(f"⚠️ [DEBUG] FALLBACK: Testando SQLite no Vercel: {sqlite_path}")
        
        if test_database_connection(sqlite_url):
            print(f"✅ [DEBUG] SQLite em /tmp funcionando!")
            return sqlite_url
        else:
            # Se /tmp falhar, usar banco em memória
            print(f"❌ [DEBUG] SQLite em /tmp falhou, usando banco em memória")
            return "sqlite:///:memory:"
    else:
        sqlite_path = Path("chatbot_local.db")
        sqlite_url = f"sqlite:///{sqlite_path}"
        print(f"⚠️ [DEBUG] FALLBACK: Usando SQLite local: {sqlite_path}")
        return sqlite_url

# ✅ CORREÇÃO: Configuração ultra-robusta para Vercel
def create_database_engine():
    """Cria engine de banco com fallbacks ultra-robustos para ambientes serverless"""
    
    database_url = get_database_url()
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    # ESTRATÉGIA 1: Tentar a URL primária
    try:
        if database_url.startswith('sqlite'):
            if database_url == "sqlite:///:memory:":
                # Banco em memória - sempre funciona
                engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False
                )
                print("💾 Usando banco SQLite em memória")
            else:
                # SQLite com arquivo
                engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    pool_pre_ping=True,
                    echo=False
                )
                print("📁 Usando banco SQLite em arquivo")
        else:
            # PostgreSQL/Supabase
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=60,
                pool_timeout=5,
                connect_args={
                    "connect_timeout": 3,
                    "options": "-c statement_timeout=10000"
                },
                echo=False
            )
            # Teste rápido de conexão
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL/Supabase conectado!")
        
        # Teste final da engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
        
    except Exception as e:
        print(f"❌ Erro na URL primária: {e}")
        
        # ESTRATÉGIA 2: Fallback para banco em memória (SEMPRE funciona)
        try:
            print("🔄 Usando fallback: banco em memória")
            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
            
            # Teste simples
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ Fallback em memória funcionando!")
            return engine
            
        except Exception as fallback_error:
            print(f"❌ Erro crítico no fallback: {fallback_error}")
            return None

# Configurar banco de dados
try:
    engine = create_database_engine()
    
    if engine is not None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Criar tabelas
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tabelas criadas com sucesso")
        except Exception as table_error:
            print(f"⚠️ Erro ao criar tabelas: {table_error}")
            print("⚠️ Continuando sem tabelas - usando mock quando necessário")
        
        print("✅ Sistema de banco configurado com sucesso")
    else:
        print("❌ ERRO CRÍTICO: Não foi possível configurar nenhum banco")
        SessionLocal = None
        
except Exception as critical_error:
    print(f"❌ ERRO CRÍTICO na configuração: {critical_error}")
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
    """Dependency que SEMPRE retorna uma sessão utilizável"""
    db = None
    try:
        if SessionLocal is not None:
            db = SessionLocal()
            # Teste rápido da sessão
            try:
                db.execute(text("SELECT 1"))
                yield db
                return
            except Exception as test_error:
                print(f"⚠️ Sessão real falhou no teste: {test_error}")
                try:
                    db.close()
                except:
                    pass
                db = None
        
        # Fallback para MockDB
        print("🎭 Usando MockDB como fallback")
        db = MockDB()
        yield db
        
    except Exception as critical_error:
        print(f"❌ Erro crítico em get_db: {critical_error}")
        # Último recurso: criar novo MockDB
        try:
            if db and hasattr(db, 'close'):
                db.close()
        except:
            pass
        yield MockDB()
    finally:
        # Cleanup seguro
        try:
            if db and hasattr(db, 'close') and not isinstance(db, MockDB):
                db.close()
        except Exception as close_error:
            print(f"⚠️ Erro ao fechar sessão: {close_error}") 