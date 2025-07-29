from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from app.models.database import Base

class ConversationStatus(enum.Enum):
    PENDING = "pending"          # Aguardando revisão
    IN_PROGRESS = "in_progress"  # Em atendimento
    COMPLETED = "completed"      # Finalizada
    REQUIRES_ATTENTION = "requires_attention"  # Precisa atenção
    SPAM = "spam"               # Spam/Irrelevante

class ConversationTag(enum.Enum):
    AGENDAMENTO_SUCESSO = "agendamento_sucesso"
    AGENDAMENTO_ERRO = "agendamento_erro"
    CANCELAMENTO = "cancelamento"
    LISTA_ESPERA = "lista_espera"
    DUVIDA = "duvida"
    RECLAMACAO = "reclamacao"
    NOVO_PACIENTE = "novo_paciente"
    URGENTE = "urgente"
    REAGENDAMENTO = "reagendamento"
    CONFIRMACAO = "confirmacao"

class ConversationDashboard(Base):
    __tablename__ = "conversation_dashboard"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"))
    phone = Column(String, nullable=False)
    patient_name = Column(String)
    patient_cpf = Column(String)
    
    # Status e classificação
    status = Column(Enum(ConversationStatus), default=ConversationStatus.PENDING)
    tags = Column(JSON, default=[])
    priority = Column(Integer, default=0)  # 0-baixa, 1-média, 2-alta, 3-urgente
    
    # Análise de sentimento
    sentiment_score = Column(Integer)  # -100 a 100
    ai_summary = Column(String)
    ai_suggested_action = Column(String)
    
    # Métricas
    message_count = Column(Integer, default=0)
    bot_resolution = Column(Boolean)
    human_intervention = Column(Boolean, default=False)
    resolution_time = Column(Integer)  # em minutos
    
    # Timestamps
    first_message_at = Column(DateTime)
    last_message_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    
    # Relacionamentos
    messages = relationship("ConversationMessage", back_populates="dashboard")
    notes = relationship("ConversationNote", back_populates="dashboard")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String, ForeignKey("conversation_dashboard.id"))
    
    sender = Column(String)  # "user" ou "bot"
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String)  # text, image, audio, etc
    
    dashboard = relationship("ConversationDashboard", back_populates="messages")

class ConversationNote(Base):
    __tablename__ = "conversation_notes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String, ForeignKey("conversation_dashboard.id"))
    
    note = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("ConversationDashboard", back_populates="notes") 