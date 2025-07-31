import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.models.patient_transaction import DecisionType, TransactionStage, ValidationResult

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Nível de confiança da decisão"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class DecisionFactor:
    """Fator que influencia uma decisão"""
    name: str
    value: Any
    weight: float  # 0.0 a 1.0
    confidence: ConfidenceLevel
    reason: str

@dataclass
class DecisionOption:
    """Opção de decisão avaliada"""
    decision_type: DecisionType
    confidence_score: float  # 0.0 a 1.0
    reasons: List[str]
    factors_supporting: List[DecisionFactor]
    factors_against: List[DecisionFactor]
    suggested_action: str
    expected_outcome: str
    risk_level: str  # low, medium, high

@dataclass
class DecisionResult:
    """Resultado final da análise de decisão"""
    chosen_decision: DecisionType
    confidence: float
    reason: str
    alternatives: List[DecisionOption]
    factors_used: List[DecisionFactor]
    decision_path: List[str]  # Passos da lógica de decisão
    suggested_action: str
    fallback_action: Optional[str] = None

class IntelligentDecisionEngine:
    """Motor de decisão inteligente para transações de pacientes"""
    
    def __init__(self):
        self.decision_rules = self._load_decision_rules()
        self.historical_patterns = {}
        
    def analyze_and_decide(
        self, 
        current_stage: TransactionStage,
        user_input: str,
        context: Dict[str, Any],
        patient_data: Optional[Dict[str, Any]] = None,
        validation_result: Optional[ValidationResult] = None,
        errors: List[str] = None,
        warnings: List[str] = None
    ) -> DecisionResult:
        """
        Analisa situação atual e toma decisão inteligente
        
        Args:
            current_stage: Estágio atual da transação
            user_input: Input do usuário
            context: Contexto atual da conversa
            patient_data: Dados do paciente (se disponível)
            validation_result: Resultado da validação
            errors: Lista de erros
            warnings: Lista de avisos
            
        Returns:
            DecisionResult com decisão recomendada
        """
        errors = errors or []
        warnings = warnings or []
        
        # 1. Coletar fatores de decisão
        factors = self._collect_decision_factors(
            current_stage, user_input, context, patient_data, 
            validation_result, errors, warnings
        )
        
        # 2. Gerar opções de decisão
        options = self._generate_decision_options(factors, current_stage, context)
        
        # 3. Avaliar cada opção
        evaluated_options = [self._evaluate_option(option, factors) for option in options]
        
        # 4. Escolher melhor opção
        best_option = self._choose_best_option(evaluated_options)
        
        # 5. Gerar resultado final
        decision_result = DecisionResult(
            chosen_decision=best_option.decision_type,
            confidence=best_option.confidence_score,
            reason=self._build_decision_reason(best_option, factors),
            alternatives=[opt for opt in evaluated_options if opt != best_option],
            factors_used=factors,
            decision_path=self._build_decision_path(factors, best_option),
            suggested_action=best_option.suggested_action,
            fallback_action=self._determine_fallback_action(best_option, evaluated_options)
        )
        
        logger.info(f"🎯 Decisão: {decision_result.chosen_decision.value} (confiança: {decision_result.confidence:.2f})")
        logger.info(f"📋 Razão: {decision_result.reason}")
        
        return decision_result
    
    def _collect_decision_factors(
        self,
        current_stage: TransactionStage,
        user_input: str,
        context: Dict[str, Any],
        patient_data: Optional[Dict[str, Any]],
        validation_result: Optional[ValidationResult],
        errors: List[str],
        warnings: List[str]
    ) -> List[DecisionFactor]:
        """Coleta todos os fatores relevantes para a decisão"""
        factors = []
        
        # Fator: Estágio atual
        factors.append(DecisionFactor(
            name="current_stage",
            value=current_stage.value,
            weight=0.9,
            confidence=ConfidenceLevel.VERY_HIGH,
            reason="Estágio atual determina ações possíveis"
        ))
        
        # Fator: Presença de erros
        if errors:
            factors.append(DecisionFactor(
                name="has_errors",
                value=True,
                weight=0.95,
                confidence=ConfidenceLevel.VERY_HIGH,
                reason=f"Erros encontrados: {', '.join(errors[:2])}"
            ))
        
        # Fator: Dados do paciente disponíveis
        if patient_data:
            completeness = self._calculate_data_completeness(patient_data)
            factors.append(DecisionFactor(
                name="patient_data_completeness",
                value=completeness,
                weight=0.8,
                confidence=ConfidenceLevel.HIGH,
                reason=f"Dados do paciente {completeness:.0%} completos"
            ))
        
        # Fator: Tipo de input do usuário
        input_type = self._classify_user_input(user_input)
        factors.append(DecisionFactor(
            name="user_input_type",
            value=input_type,
            weight=0.7,
            confidence=ConfidenceLevel.HIGH,
            reason=f"Input classificado como: {input_type}"
        ))
        
        # Fator: Contexto anterior existe
        has_previous_context = bool(context.get('paciente') or context.get('last_transaction'))
        factors.append(DecisionFactor(
            name="has_context",
            value=has_previous_context,
            weight=0.6,
            confidence=ConfidenceLevel.MEDIUM,
            reason="Contexto anterior disponível" if has_previous_context else "Sem contexto anterior"
        ))
        
        # Fator: Ação pretendida
        intended_action = context.get('acao')
        if intended_action:
            factors.append(DecisionFactor(
                name="intended_action",
                value=intended_action,
                weight=0.8,
                confidence=ConfidenceLevel.HIGH,
                reason=f"Usuário quer: {intended_action}"
            ))
        
        # Fator: Resultado da validação
        if validation_result:
            factors.append(DecisionFactor(
                name="validation_result",
                value=validation_result.value,
                weight=0.85,
                confidence=ConfidenceLevel.HIGH,
                reason=f"Validação: {validation_result.value}"
            ))
        
        # Fator: Avisos
        if warnings:
            factors.append(DecisionFactor(
                name="has_warnings",
                value=len(warnings),
                weight=0.5,
                confidence=ConfidenceLevel.MEDIUM,
                reason=f"{len(warnings)} avisos encontrados"
            ))
        
        return factors
    
    def _generate_decision_options(
        self, 
        factors: List[DecisionFactor], 
        current_stage: TransactionStage,
        context: Dict[str, Any]
    ) -> List[DecisionOption]:
        """Gera opções de decisão possíveis baseadas nos fatores"""
        options = []
        
        # Analisar fatores críticos
        has_errors = any(f.name == "has_errors" and f.value for f in factors)
        has_patient_data = any(f.name == "patient_data_completeness" and f.value > 0.5 for f in factors)
        validation_passed = any(f.name == "validation_result" and f.value == "passou" for f in factors)
        intended_action = next((f.value for f in factors if f.name == "intended_action"), None)
        
        # Opção: Corrigir erros
        if has_errors:
            options.append(DecisionOption(
                decision_type=DecisionType.CORRIGIR,
                confidence_score=0.9,
                reasons=["Erros detectados que precisam ser corrigidos"],
                factors_supporting=[f for f in factors if f.name == "has_errors"],
                factors_against=[],
                suggested_action="mostrar_erro_e_solicitar_correcao",
                expected_outcome="Usuário corrige o erro e continua",
                risk_level="low"
            ))
        
        # Opção: Confirmar dados
        if has_patient_data and validation_passed and current_stage in [TransactionStage.BUSCA_EXECUTADA, TransactionStage.VERIFICADO]:
            options.append(DecisionOption(
                decision_type=DecisionType.CONFIRMAR,
                confidence_score=0.85,
                reasons=["Dados do paciente encontrados e validados"],
                factors_supporting=[f for f in factors if f.name in ["patient_data_completeness", "validation_result"]],
                factors_against=[],
                suggested_action="solicitar_confirmacao_paciente",
                expected_outcome="Usuário confirma e escolhe próxima ação",
                risk_level="low"
            ))
        
        # Opção: Agendar
        if intended_action == "agendar" and has_patient_data:
            options.append(DecisionOption(
                decision_type=DecisionType.AGENDAR,
                confidence_score=0.8,
                reasons=["Usuário quer agendar e temos dados do paciente"],
                factors_supporting=[f for f in factors if f.name in ["intended_action", "patient_data_completeness"]],
                factors_against=[],
                suggested_action="iniciar_processo_agendamento",
                expected_outcome="Usuário escolhe data e horário",
                risk_level="medium"
            ))
        
        # Opção: Visualizar
        if intended_action == "visualizar" and has_patient_data:
            options.append(DecisionOption(
                decision_type=DecisionType.VISUALIZAR,
                confidence_score=0.8,
                reasons=["Usuário quer ver agendamentos e temos dados do paciente"],
                factors_supporting=[f for f in factors if f.name in ["intended_action", "patient_data_completeness"]],
                factors_against=[],
                suggested_action="mostrar_agendamentos_paciente",
                expected_outcome="Usuário vê seus agendamentos",
                risk_level="low"
            ))
        
        # Opção: Avançar no fluxo
        if not has_errors and current_stage != TransactionStage.ERRO:
            options.append(DecisionOption(
                decision_type=DecisionType.AVANÇAR,
                confidence_score=0.6,
                reasons=["Continuar fluxo normal sem erros"],
                factors_supporting=[f for f in factors if f.name == "current_stage"],
                factors_against=[],
                suggested_action="continuar_fluxo_atual",
                expected_outcome="Processo continua normalmente",
                risk_level="low"
            ))
        
        # Opção: Repetir (fallback)
        options.append(DecisionOption(
            decision_type=DecisionType.REPETIR,
            confidence_score=0.3,
            reasons=["Repetir última ação como fallback"],
            factors_supporting=[],
            factors_against=[],
            suggested_action="repetir_ultima_acao",
            expected_outcome="Usuário tem nova chance",
            risk_level="medium"
        ))
        
        return options
    
    def _evaluate_option(self, option: DecisionOption, factors: List[DecisionFactor]) -> DecisionOption:
        """Avalia uma opção de decisão baseada nos fatores"""
        # Calcular score baseado nos fatores que suportam
        support_score = 0.0
        total_weight = 0.0
        
        for factor in option.factors_supporting:
            weight = factor.weight * factor.confidence.value / 5.0
            support_score += weight
            total_weight += weight
        
        # Penalizar por fatores contra
        penalty = sum(f.weight * 0.2 for f in option.factors_against)
        
        # Score final normalizado
        if total_weight > 0:
            final_score = (support_score / total_weight) - penalty
        else:
            final_score = option.confidence_score - penalty
        
        # Aplicar bônus baseado no tipo de decisão e contexto
        final_score = self._apply_contextual_bonus(option, factors, final_score)
        
        option.confidence_score = max(0.0, min(1.0, final_score))
        return option
    
    def _apply_contextual_bonus(
        self, 
        option: DecisionOption, 
        factors: List[DecisionFactor], 
        base_score: float
    ) -> float:
        """Aplica bônus contextual baseado em regras específicas"""
        bonus = 0.0
        
        # Bônus para corrigir quando há erros
        if option.decision_type == DecisionType.CORRIGIR:
            has_errors = any(f.name == "has_errors" and f.value for f in factors)
            if has_errors:
                bonus += 0.2
        
        # Bônus para confirmar quando dados estão completos
        if option.decision_type == DecisionType.CONFIRMAR:
            completeness = next((f.value for f in factors if f.name == "patient_data_completeness"), 0)
            if completeness > 0.8:
                bonus += 0.15
        
        # Bônus para ação pretendida
        intended_action = next((f.value for f in factors if f.name == "intended_action"), None)
        if intended_action:
            if (intended_action == "agendar" and option.decision_type == DecisionType.AGENDAR):
                bonus += 0.1
            elif (intended_action == "visualizar" and option.decision_type == DecisionType.VISUALIZAR):
                bonus += 0.1
        
        return base_score + bonus
    
    def _choose_best_option(self, options: List[DecisionOption]) -> DecisionOption:
        """Escolhe a melhor opção baseada no score de confiança"""
        if not options:
            # Fallback para avançar
            return DecisionOption(
                decision_type=DecisionType.AVANÇAR,
                confidence_score=0.5,
                reasons=["Opção padrão de fallback"],
                factors_supporting=[],
                factors_against=[],
                suggested_action="continuar_fluxo",
                expected_outcome="Continuar processo",
                risk_level="medium"
            )
        
        # Ordenar por confiança e escolher o melhor
        sorted_options = sorted(options, key=lambda x: x.confidence_score, reverse=True)
        best_option = sorted_options[0]
        
        # Se a melhor opção tem confiança muito baixa, escolher uma mais segura
        if best_option.confidence_score < 0.4:
            safe_options = [opt for opt in sorted_options if opt.risk_level == "low"]
            if safe_options:
                best_option = safe_options[0]
        
        return best_option
    
    def _build_decision_reason(self, option: DecisionOption, factors: List[DecisionFactor]) -> str:
        """Constrói explicação da decisão"""
        main_reasons = option.reasons[:2]  # Principais razões
        
        supporting_factors = [f.reason for f in option.factors_supporting[:2]]
        
        reason_parts = main_reasons + supporting_factors
        return ". ".join(reason_parts)
    
    def _build_decision_path(self, factors: List[DecisionFactor], option: DecisionOption) -> List[str]:
        """Constrói caminho da lógica de decisão"""
        path = []
        
        # Estágio atual
        current_stage = next((f.value for f in factors if f.name == "current_stage"), "unknown")
        path.append(f"Estágio atual: {current_stage}")
        
        # Fatores críticos
        if any(f.name == "has_errors" and f.value for f in factors):
            path.append("Erros detectados → priorizar correção")
        
        if any(f.name == "patient_data_completeness" and f.value > 0.5 for f in factors):
            path.append("Dados do paciente disponíveis → permitir ações avançadas")
        
        intended_action = next((f.value for f in factors if f.name == "intended_action"), None)
        if intended_action:
            path.append(f"Ação pretendida: {intended_action} → alinhar decisão")
        
        # Decisão final
        path.append(f"Decisão: {option.decision_type.value}")
        
        return path
    
    def _determine_fallback_action(
        self, 
        chosen_option: DecisionOption, 
        all_options: List[DecisionOption]
    ) -> Optional[str]:
        """Determina ação de fallback se a principal falhar"""
        # Se a principal é de alto risco, escolher uma de baixo risco
        if chosen_option.risk_level == "high":
            safe_options = [opt for opt in all_options if opt.risk_level == "low" and opt != chosen_option]
            if safe_options:
                return safe_options[0].suggested_action
        
        # Fallback padrão
        if chosen_option.decision_type != DecisionType.REPETIR:
            return "repetir_ultima_acao"
        
        return "voltar_menu_principal"
    
    def _calculate_data_completeness(self, patient_data: Dict[str, Any]) -> float:
        """Calcula completude dos dados do paciente"""
        required_fields = ["nome", "cpf"]
        optional_fields = ["telefone", "email", "endereco", "data_nascimento"]
        
        required_present = sum(1 for field in required_fields if patient_data.get(field))
        optional_present = sum(1 for field in optional_fields if patient_data.get(field))
        
        required_score = required_present / len(required_fields) * 0.8  # 80% do peso
        optional_score = optional_present / len(optional_fields) * 0.2  # 20% do peso
        
        return required_score + optional_score
    
    def _classify_user_input(self, user_input: str) -> str:
        """Classifica o tipo de input do usuário"""
        if not user_input:
            return "empty"
        
        # CPF
        if len(''.join(filter(str.isdigit, user_input))) == 11:
            return "cpf"
        
        # Número (opção de menu)
        if user_input.strip().isdigit():
            return "menu_option"
        
        # Comando
        commands = ["sair", "menu", "ajuda", "cancelar", "sim", "não", "ok"]
        if user_input.strip().lower() in commands:
            return "command"
        
        # Texto livre
        if len(user_input.split()) > 3:
            return "free_text"
        
        return "short_text"
    
    def _load_decision_rules(self) -> Dict[str, Any]:
        """Carrega regras de decisão (por enquanto hardcoded)"""
        return {
            "error_priority": 0.95,  # Prioridade para correção de erros
            "data_completeness_threshold": 0.7,  # Threshold para considerar dados completos
            "confirmation_confidence_threshold": 0.8,  # Threshold para auto-confirmação
            "fallback_to_safe_option": True,  # Usar opção segura se confiança baixa
            "max_retries": 3,  # Máximo de repetições antes de escalar
        }
    
    def explain_decision(self, decision_result: DecisionResult) -> Dict[str, Any]:
        """Gera explicação detalhada da decisão para auditoria"""
        return {
            "decision": decision_result.chosen_decision.value,
            "confidence": decision_result.confidence,
            "reason": decision_result.reason,
            "decision_path": decision_result.decision_path,
            "factors_analyzed": [
                {
                    "name": f.name,
                    "value": str(f.value),
                    "weight": f.weight,
                    "confidence": f.confidence.name,
                    "reason": f.reason
                }
                for f in decision_result.factors_used
            ],
            "alternatives_considered": [
                {
                    "decision": alt.decision_type.value,
                    "confidence": alt.confidence_score,
                    "reasons": alt.reasons
                }
                for alt in decision_result.alternatives
            ],
            "suggested_action": decision_result.suggested_action,
            "fallback_action": decision_result.fallback_action,
            "timestamp": datetime.utcnow().isoformat()
        }