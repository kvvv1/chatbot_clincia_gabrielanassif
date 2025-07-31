import logging
import json
import hashlib
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass

from app.models.patient_transaction import (
    PatientTransaction, PatientCache, ContextHistory, DecisionLog, ValidationRule,
    TransactionStage, ValidationResult, DecisionType
)
from app.models.database import Conversation
from app.services.gestaods import GestaoDS
from app.utils.validators import ValidatorUtils
import time

logger = logging.getLogger(__name__)

@dataclass
class TransactionContext:
    """Contexto completo de uma transação"""
    phone: str
    conversation_id: str
    user_input: str
    current_stage: TransactionStage
    previous_stage: Optional[TransactionStage]
    loaded_context: Dict[str, Any]
    patient_data: Optional[Dict[str, Any]] = None
    api_response: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    decision_made: Optional[DecisionType] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class PatientTransactionService:
    """Serviço robusto para transações de pacientes com estados e auditoria"""
    
    def __init__(self):
        self.gestaods = GestaoDS()
        self.validator = ValidatorUtils()
        self.validation_rules = {}
        self._load_validation_rules()
    
    async def process_patient_transaction(
        self, 
        phone: str, 
        user_input: str, 
        conversation: Conversation,
        db: Session
    ) -> TransactionContext:
        """
        Processa uma transação completa de paciente com auditoria
        
        Args:
            phone: Número do telefone
            user_input: Input do usuário
            conversation: Objeto da conversa
            db: Sessão do banco
            
        Returns:
            TransactionContext com resultado completo
        """
        start_time = time.time()
        
        # 1. Preparar contexto
        context = TransactionContext(
            phone=phone,
            conversation_id=conversation.id,
            user_input=user_input,
            current_stage=self._determine_stage_from_input(user_input, conversation),
            previous_stage=self._get_previous_stage(conversation),
            loaded_context=conversation.context or {}
        )
        
        try:
            # 2. Carregar contexto existente
            await self._load_existing_context(context, db)
            
            # 3. Executar busca de paciente se necessário
            if self._needs_patient_search(context):
                await self._execute_patient_search(context, db)
            
            # 4. Validar dados e resposta
            self._validate_transaction_data(context)
            
            # 5. Tomar decisão inteligente
            self._make_intelligent_decision(context)
            
            # 6. Atualizar contexto
            self._update_context(context, conversation)
            
            # 7. Persistir transação completa
            await self._persist_transaction(context, db, start_time)
            
            logger.info(f"✅ Transação processada: {context.current_stage.value} -> {context.decision_made.value if context.decision_made else 'N/A'}")
            
        except Exception as e:
            context.errors.append(f"Erro no processamento: {str(e)}")
            context.current_stage = TransactionStage.ERRO
            logger.error(f"❌ Erro na transação: {str(e)}")
            
            # Persistir erro também
            await self._persist_transaction(context, db, start_time)
            
        return context
    
    def _determine_stage_from_input(self, user_input: str, conversation: Conversation) -> TransactionStage:
        """Determina o estágio baseado no input e contexto atual"""
        current_state = conversation.state or "inicio"
        context = conversation.context or {}
        
        # Se tem CPF no input, provavelmente é busca
        if self._is_cpf_input(user_input):
            return TransactionStage.INICIAL
        
        # Se já tem paciente no contexto, está verificado
        if context.get('paciente'):
            return TransactionStage.VERIFICADO
        
        # Baseado no estado atual da conversa
        stage_mapping = {
            "inicio": TransactionStage.INICIAL,
            "aguardando_cpf": TransactionStage.INICIAL,
            "escolhendo_data": TransactionStage.VERIFICADO,
            "confirmando_agendamento": TransactionStage.AGUARDANDO_CONFIRMACAO,
        }
        
        return stage_mapping.get(current_state, TransactionStage.INICIAL)
    
    def _get_previous_stage(self, conversation: Conversation) -> Optional[TransactionStage]:
        """Obtém o estágio anterior da conversa"""
        context = conversation.context or {}
        previous_stage_str = context.get('previous_stage')
        
        if previous_stage_str:
            try:
                return TransactionStage(previous_stage_str)
            except ValueError:
                pass
        
        return None
    
    async def _load_existing_context(self, context: TransactionContext, db: Session):
        """Carrega contexto existente e cache de paciente"""
        # Verificar se já temos dados de paciente em cache
        if context.loaded_context.get('paciente'):
            cpf = context.loaded_context['paciente'].get('cpf')
            if cpf:
                cached_patient = await self._get_cached_patient(cpf, context.phone, db)
                if cached_patient and not cached_patient.is_stale:
                    context.patient_data = cached_patient.patient_data
                    context.loaded_context['paciente'] = cached_patient.patient_data
                    logger.info(f"📋 Dados do paciente carregados do cache")
    
    def _needs_patient_search(self, context: TransactionContext) -> bool:
        """Determina se precisa fazer busca de paciente"""
        # Se já tem dados válidos, não precisa buscar
        if context.patient_data:
            return False
        
        # Se o input contém CPF e estamos no estágio inicial
        if (self._is_cpf_input(context.user_input) and 
            context.current_stage == TransactionStage.INICIAL):
            return True
        
        # Se estamos aguardando CPF e não temos paciente
        if (context.current_stage == TransactionStage.INICIAL and 
            not context.loaded_context.get('paciente')):
            return True
        
        return False
    
    async def _execute_patient_search(self, context: TransactionContext, db: Session):
        """Executa busca de paciente com cache inteligente"""
        cpf = self._extract_cpf_from_input(context.user_input)
        
        if not cpf:
            context.errors.append("CPF não encontrado no input")
            return
        
        if not self.validator.validar_cpf(cpf):
            context.errors.append("CPF inválido")
            return
        
        try:
            # Verificar cache primeiro
            cached_patient = await self._get_cached_patient(cpf, context.phone, db)
            
            if cached_patient and not cached_patient.is_stale:
                context.patient_data = cached_patient.patient_data
                context.api_response = {"source": "cache", "data": cached_patient.patient_data}
                context.current_stage = TransactionStage.VERIFICADO
                logger.info(f"📋 Paciente encontrado no cache")
                return
            
            # Buscar na API
            api_start = datetime.utcnow()
            patient_data = await self.gestaods.buscar_paciente_cpf(cpf)
            api_end = datetime.utcnow()
            
            context.api_response = {
                "endpoint": f"/api/paciente/{self.gestaods.token}/{cpf}/",
                "response": patient_data,
                "timestamp": api_start.isoformat(),
                "response_time_ms": int((api_end - api_start).total_seconds() * 1000)
            }
            
            if patient_data:
                context.patient_data = patient_data
                context.current_stage = TransactionStage.BUSCA_EXECUTADA
                
                # Atualizar cache
                await self._update_patient_cache(cpf, context.phone, patient_data, db)
                logger.info(f"✅ Paciente encontrado na API")
            else:
                context.errors.append("Paciente não encontrado")
                context.current_stage = TransactionStage.ERRO
                logger.warning(f"❌ Paciente não encontrado: {cpf}")
                
        except Exception as e:
            context.errors.append(f"Erro na busca: {str(e)}")
            context.current_stage = TransactionStage.ERRO
            logger.error(f"❌ Erro na busca de paciente: {str(e)}")
    
    def _validate_transaction_data(self, context: TransactionContext):
        """Valida dados da transação aplicando regras configuráveis"""
        validation_details = {
            "rules_applied": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }
        
        # Validar CPF se presente
        if self._is_cpf_input(context.user_input):
            cpf = self._extract_cpf_from_input(context.user_input)
            if self.validator.validar_cpf(cpf):
                validation_details["passed"].append("cpf_format_valid")
            else:
                validation_details["failed"].append("cpf_format_invalid")
                context.errors.append("Formato de CPF inválido")
        
        # Validar dados do paciente se presentes
        if context.patient_data:
            required_fields = ["nome", "cpf"]
            for field in required_fields:
                if field in context.patient_data and context.patient_data[field]:
                    validation_details["passed"].append(f"patient_{field}_present")
                else:
                    validation_details["failed"].append(f"patient_{field}_missing")
                    context.warnings.append(f"Campo {field} faltando nos dados do paciente")
        
        # Validar consistência com contexto anterior
        if context.loaded_context.get('paciente') and context.patient_data:
            previous_cpf = context.loaded_context['paciente'].get('cpf')
            current_cpf = context.patient_data.get('cpf')
            
            if previous_cpf and current_cpf and previous_cpf != current_cpf:
                validation_details["failed"].append("cpf_inconsistency")
                context.warnings.append("CPF inconsistente com contexto anterior")
        
        # Determinar resultado da validação
        if validation_details["failed"]:
            context.validation_results = ValidationResult.FALHOU
        elif validation_details["warnings"]:
            context.validation_results = ValidationResult.PARCIAL
        else:
            context.validation_results = ValidationResult.PASSOU
        
        context.loaded_context['validation_details'] = validation_details
        logger.info(f"🔍 Validação: {context.validation_results.value}")
    
    def _make_intelligent_decision(self, context: TransactionContext):
        """Toma decisão inteligente baseada no contexto e regras"""
        decision_factors = {
            "stage": context.current_stage.value,
            "has_patient_data": bool(context.patient_data),
            "has_errors": bool(context.errors),
            "validation_result": context.validation_results.value if context.validation_results else None,
            "previous_context": bool(context.loaded_context.get('paciente'))
        }
        
        # Regras de decisão
        if context.errors:
            context.decision_made = DecisionType.CORRIGIR
            context.loaded_context['suggested_action'] = "corrigir_erro"
            context.loaded_context['decision_reason'] = f"Erros encontrados: {', '.join(context.errors)}"
        
        elif context.current_stage == TransactionStage.BUSCA_EXECUTADA and context.patient_data:
            context.decision_made = DecisionType.CONFIRMAR
            context.current_stage = TransactionStage.VERIFICADO
            context.loaded_context['suggested_action'] = "confirmar_paciente"
            context.loaded_context['decision_reason'] = "Paciente encontrado, solicitar confirmação"
        
        elif context.current_stage == TransactionStage.VERIFICADO:
            # Decidir próxima ação baseada no contexto
            acao = context.loaded_context.get('acao')
            if acao == "agendar":
                context.decision_made = DecisionType.AGENDAR
                context.loaded_context['suggested_action'] = "iniciar_agendamento"
            elif acao == "visualizar":
                context.decision_made = DecisionType.VISUALIZAR
                context.loaded_context['suggested_action'] = "mostrar_agendamentos"
            else:
                context.decision_made = DecisionType.CONFIRMAR
                context.loaded_context['suggested_action'] = "confirmar_acao"
            
            context.loaded_context['decision_reason'] = f"Paciente verificado, executar ação: {acao}"
        
        else:
            context.decision_made = DecisionType.AVANÇAR
            context.loaded_context['suggested_action'] = "continuar_fluxo"
            context.loaded_context['decision_reason'] = "Continuar fluxo normal"
        
        # Log da decisão
        context.loaded_context['decision_factors'] = decision_factors
        logger.info(f"🎯 Decisão: {context.decision_made.value} - {context.loaded_context.get('decision_reason')}")
    
    def _update_context(self, context: TransactionContext, conversation: Conversation):
        """Atualiza contexto da conversa"""
        # Salvar estágio anterior
        if context.previous_stage:
            context.loaded_context['previous_stage'] = context.previous_stage.value
        
        # Atualizar dados do paciente
        if context.patient_data:
            context.loaded_context['paciente'] = context.patient_data
        
        # Salvar informações da transação
        context.loaded_context['last_transaction'] = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": context.current_stage.value,
            "decision": context.decision_made.value if context.decision_made else None,
            "validation_result": context.validation_results.value if context.validation_results else None
        }
        
        # Atualizar conversa
        conversation.context = context.loaded_context
        
        # Atualizar estado baseado no estágio
        stage_to_state_mapping = {
            TransactionStage.INICIAL: "aguardando_cpf",
            TransactionStage.VERIFICADO: "escolhendo_data",
            TransactionStage.AGUARDANDO_CONFIRMACAO: "confirmando_agendamento",
            TransactionStage.ERRO: "menu_principal"
        }
        
        new_state = stage_to_state_mapping.get(context.current_stage, conversation.state)
        conversation.state = new_state
    
    async def _persist_transaction(self, context: TransactionContext, db: Session, start_time: float):
        """Persiste transação completa no banco"""
        processing_time = int((time.time() - start_time) * 1000)
        
        # Criar registro da transação
        transaction = PatientTransaction(
            phone=context.phone,
            conversation_id=context.conversation_id,
            user_input=context.user_input,
            stage_previous=context.previous_stage,
            stage_current=context.current_stage,
            stage_reason=context.loaded_context.get('decision_reason'),
            validation_result=context.validation_results or ValidationResult.IGNORADO,
            validation_details=context.loaded_context.get('validation_details'),
            validation_reasons=context.errors + context.warnings,
            context_loaded=context.loaded_context,
            context_updated=context.loaded_context,
            decision_type=context.decision_made or DecisionType.AVANÇAR,
            decision_reason=context.loaded_context.get('decision_reason'),
            suggested_action=context.loaded_context.get('suggested_action'),
            operation_success=not bool(context.errors),
            errors=context.errors if context.errors else None,
            warnings=context.warnings if context.warnings else None,
            processing_time_ms=processing_time,
            is_retry=False,
            retry_count=0,
            needs_human_review=bool(context.errors)
        )
        
        # Adicionar dados da API se houve chamada
        if context.api_response:
            transaction.api_endpoint = context.api_response.get('endpoint')
            transaction.api_parameters = {"cpf": self._extract_cpf_from_input(context.user_input)}
            transaction.api_response = context.api_response
            transaction.api_timestamp = datetime.utcnow()
            transaction.api_success = bool(context.patient_data)
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"💾 Transação persistida: {transaction.id}")
    
    async def _get_cached_patient(self, cpf: str, phone: str, db: Session) -> Optional[PatientCache]:
        """Busca paciente no cache"""
        cache_entry = db.query(PatientCache).filter_by(
            cpf=cpf, 
            phone=phone
        ).first()
        
        if cache_entry:
            # Verificar se expirou
            if cache_entry.expires_at and datetime.utcnow() > cache_entry.expires_at:
                cache_entry.is_stale = True
                db.commit()
        
        return cache_entry
    
    async def _update_patient_cache(self, cpf: str, phone: str, patient_data: Dict, db: Session):
        """Atualiza cache de paciente"""
        data_hash = hashlib.md5(json.dumps(patient_data, sort_keys=True).encode()).hexdigest()
        
        cache_entry = await self._get_cached_patient(cpf, phone, db)
        
        if cache_entry:
            # Atualizar existente
            cache_entry.patient_data = patient_data
            cache_entry.data_hash = data_hash
            cache_entry.fetch_timestamp = datetime.utcnow()
            cache_entry.last_validated = datetime.utcnow()
            cache_entry.validation_count += 1
            cache_entry.is_stale = False
            cache_entry.expires_at = datetime.utcnow() + timedelta(seconds=cache_entry.ttl_seconds)
        else:
            # Criar novo
            cache_entry = PatientCache(
                cpf=cpf,
                phone=phone,
                patient_data=patient_data,
                data_hash=data_hash,
                expires_at=datetime.utcnow() + timedelta(seconds=300)  # 5 minutos
            )
            db.add(cache_entry)
        
        db.commit()
    
    def _is_cpf_input(self, text: str) -> bool:
        """Verifica se o input contém um CPF"""
        # Remove tudo que não é dígito
        digits_only = ''.join(filter(str.isdigit, text))
        return len(digits_only) == 11
    
    def _extract_cpf_from_input(self, text: str) -> Optional[str]:
        """Extrai CPF do input"""
        if self._is_cpf_input(text):
            return ''.join(filter(str.isdigit, text))
        return None
    
    def _load_validation_rules(self):
        """Carrega regras de validação (por enquanto hardcoded, depois do banco)"""
        self.validation_rules = {
            "cpf_required": {"active": True, "severity": "error"},
            "cpf_format": {"active": True, "severity": "error"},
            "patient_data_complete": {"active": True, "severity": "warning"},
            "context_consistency": {"active": True, "severity": "warning"}
        }
    
    async def get_transaction_history(self, phone: str, db: Session, limit: int = 10) -> List[PatientTransaction]:
        """Busca histórico de transações de um telefone"""
        return db.query(PatientTransaction).filter_by(
            phone=phone
        ).order_by(PatientTransaction.created_at.desc()).limit(limit).all()
    
    async def get_patient_from_cache(self, cpf: str, phone: str, db: Session) -> Optional[Dict]:
        """Busca paciente do cache se válido"""
        cache_entry = await self._get_cached_patient(cpf, phone, db)
        
        if cache_entry and not cache_entry.is_stale and cache_entry.is_valid:
            return cache_entry.patient_data
        
        return None