from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import enum
from typing import Dict, Any, Optional

Base = declarative_base()

class TransactionStage(enum.Enum):
    """Estágios da transação de paciente"""
    INICIAL = "inicial"
    BUSCA_EXECUTADA = "busca_executada"
    VERIFICADO = "verificado"
    AGUARDANDO_CONFIRMACAO = "aguardando_confirmacao"
    AGENDADO = "agendado"
    ERRO = "erro"
    COMPLETO = "completo"

class ValidationResult(enum.Enum):
    """Resultado da validação"""
    PASSOU = "passou"
    FALHOU = "falhou"
    PARCIAL = "parcial"
    IGNORADO = "ignorado"

class DecisionType(enum.Enum):
    """Tipo de decisão tomada"""
    CONFIRMAR = "confirmar"
    CORRIGIR = "corrigir" 
    AGENDAR = "agendar"
    VISUALIZAR = "visualizar"
    AVANÇAR = "avancar"
    REPETIR = "repetir"
    ESCALATE = "escalate"

class PatientTransaction(Base):
    """Registro completo de transação de paciente"""
    __tablename__ = "patient_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, nullable=False, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    
    # Input do usuário
    user_input = Column(Text, nullable=False)
    user_input_type = Column(String, default="text")  # text, cpf, command, etc.
    
    # Estágio
    stage_previous = Column(SQLEnum(TransactionStage), nullable=True)
    stage_current = Column(SQLEnum(TransactionStage), nullable=False)
    stage_reason = Column(Text)  # Por que mudou para este estágio
    
    # API Call (se houve)
    api_endpoint = Column(String)
    api_parameters = Column(JSON)
    api_response = Column(JSON)
    api_timestamp = Column(DateTime)
    api_success = Column(Boolean, default=False)
    
    # Validação
    validation_result = Column(SQLEnum(ValidationResult), nullable=False)
    validation_details = Column(JSON)  # Detalhes do que passou/falhou
    validation_reasons = Column(JSON)  # Lista de motivos
    
    # Contexto
    context_loaded = Column(JSON)  # Contexto que foi carregado
    context_updated = Column(JSON)  # Contexto após processamento
    
    # Decisão tomada
    decision_type = Column(SQLEnum(DecisionType), nullable=False)
    decision_reason = Column(Text)
    suggested_action = Column(Text)
    
    # Resultado da operação
    operation_success = Column(Boolean, default=False)
    operation_details = Column(JSON)
    
    # Erros e alertas
    errors = Column(JSON)  # Lista de erros
    warnings = Column(JSON)  # Lista de alertas
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer)  # Tempo de processamento em ms
    
    # Flags de controle
    is_retry = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    needs_human_review = Column(Boolean, default=False)

class PatientCache(Base):
    """Cache inteligente de dados de pacientes"""
    __tablename__ = "patient_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cpf = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    
    # Dados do paciente
    patient_data = Column(JSON, nullable=False)
    data_hash = Column(String, nullable=False)  # Hash dos dados para detectar mudanças
    
    # Cache info
    api_source = Column(String, default="gestaods")
    fetch_timestamp = Column(DateTime, default=datetime.utcnow)
    last_validated = Column(DateTime, default=datetime.utcnow)
    validation_count = Column(Integer, default=1)
    
    # Flags
    is_valid = Column(Boolean, default=True)
    is_stale = Column(Boolean, default=False)
    needs_refresh = Column(Boolean, default=False)
    
    # TTL personalizado
    ttl_seconds = Column(Integer, default=300)  # 5 minutos default
    expires_at = Column(DateTime)

class ContextHistory(Base):
    """Histórico de mudanças de contexto"""
    __tablename__ = "context_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, nullable=False, index=True)
    transaction_id = Column(String, nullable=False, index=True)
    
    # Mudança de contexto
    context_before = Column(JSON)
    context_after = Column(JSON)
    context_diff = Column(JSON)  # Apenas as diferenças
    
    # Metadados da mudança
    change_type = Column(String)  # add, update, remove, merge
    change_reason = Column(Text)
    triggered_by = Column(String)  # user_input, api_response, validation, etc.
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)

class DecisionLog(Base):
    """Log detalhado de decisões tomadas"""
    __tablename__ = "decision_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, nullable=False, index=True)
    
    # Decisão
    decision_type = Column(SQLEnum(DecisionType), nullable=False)
    decision_confidence = Column(Integer)  # 0-100
    decision_reason = Column(Text, nullable=False)
    
    # Base da decisão
    decision_factors = Column(JSON)  # Fatores que influenciaram
    context_used = Column(JSON)  # Contexto usado na decisão
    rules_applied = Column(JSON)  # Regras que foram aplicadas
    
    # Alternativas consideradas
    alternatives_considered = Column(JSON)
    why_not_alternatives = Column(JSON)
    
    # Resultado
    suggested_action = Column(Text)
    action_parameters = Column(JSON)
    expected_outcome = Column(Text)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, default="system")  # system, user, escalation

class ValidationRule(Base):
    """Regras de validação personalizáveis"""
    __tablename__ = "validation_rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    # Configuração da regra
    rule_type = Column(String, nullable=False)  # field_required, field_format, data_consistency, etc.
    rule_config = Column(JSON, nullable=False)
    
    # Aplicabilidade
    applies_to_stages = Column(JSON)  # Lista de estágios onde se aplica
    applies_to_actions = Column(JSON)  # Lista de ações onde se aplica
    
    # Comportamento
    is_active = Column(Boolean, default=True)
    severity = Column(String, default="error")  # error, warning, info
    can_override = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, default="system")