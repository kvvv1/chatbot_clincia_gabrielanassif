from typing import Dict, Optional, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Sistema robusto de gerenciamento de estados para conversas"""
    
    def __init__(self):
        # Estados válidos do sistema
        self.states = {
            "inicio": {
                "description": "Estado inicial da conversa",
                "allowed_transitions": ["menu_principal", "finalizada"],
                "required_context": [],
                "optional_context": []
            },
            "menu_principal": {
                "description": "Menu principal com opções",
                "allowed_transitions": ["aguardando_cpf", "inicio", "finalizada"],
                "required_context": [],
                "optional_context": []
            },
            "aguardando_cpf": {
                "description": "Aguardando CPF do usuário",
                "allowed_transitions": ["escolhendo_tipo_consulta", "visualizando_agendamentos", "cancelando_consulta", "lista_espera", "menu_principal", "inicio"],
                "required_context": ["acao"],
                "optional_context": ["paciente"]
            },
            "escolhendo_tipo_consulta": {
                "description": "Escolhendo tipo de consulta",
                "allowed_transitions": ["escolhendo_data", "menu_principal", "inicio"],
                "required_context": ["paciente"],
                "optional_context": ["tipo_consulta", "profissional"]
            },
            "escolhendo_data": {
                "description": "Escolhendo data da consulta",
                "allowed_transitions": ["escolhendo_horario", "menu_principal", "inicio"],
                "required_context": ["paciente", "tipo_consulta", "profissional"],
                "optional_context": ["data_escolhida", "datas_disponiveis"]
            },
            "escolhendo_horario": {
                "description": "Escolhendo horário da consulta",
                "allowed_transitions": ["confirmando_agendamento", "menu_principal", "inicio"],
                "required_context": ["paciente", "tipo_consulta", "profissional", "data_escolhida"],
                "optional_context": ["horario_escolhido", "horarios_disponiveis"]
            },
            "confirmando_agendamento": {
                "description": "Confirmando agendamento",
                "allowed_transitions": ["aguardando_observacoes", "inicio", "menu_principal"],
                "required_context": ["paciente", "tipo_consulta", "profissional", "data_escolhida", "horario_escolhido"],
                "optional_context": ["observacoes"]
            },
            "aguardando_observacoes": {
                "description": "Aguardando observações do paciente",
                "allowed_transitions": ["inicio", "menu_principal"],
                "required_context": ["paciente", "tipo_consulta", "profissional", "data_escolhida", "horario_escolhido"],
                "optional_context": ["observacoes"]
            },
            "visualizando_agendamentos": {
                "description": "Visualizando agendamentos",
                "allowed_transitions": ["aguardando_cpf", "menu_principal", "inicio"],
                "required_context": ["paciente"],
                "optional_context": ["agendamentos"]
            },
            "cancelando_consulta": {
                "description": "Cancelando consulta",
                "allowed_transitions": ["confirmando_cancelamento", "menu_principal", "inicio"],
                "required_context": ["paciente"],
                "optional_context": ["agendamentos_cancelar"]
            },
            "confirmando_cancelamento": {
                "description": "Confirmando cancelamento",
                "allowed_transitions": ["inicio", "menu_principal"],
                "required_context": ["paciente", "agendamento_cancelar"],
                "optional_context": []
            },
            "lista_espera": {
                "description": "Lista de espera",
                "allowed_transitions": ["inicio", "menu_principal"],
                "required_context": ["paciente"],
                "optional_context": []
            },
            "finalizada": {
                "description": "Conversa finalizada",
                "allowed_transitions": ["inicio"],
                "required_context": [],
                "optional_context": ["finalizada_em"]
            }
        }

    def can_transition_to(self, current_state: str, target_state: str) -> Tuple[bool, str]:
        """
        Verifica se a transição de estado é válida
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if current_state is None:
            current_state = "inicio"
        else:
            current_state = current_state.lower().strip() if current_state else "inicio"
            
        if target_state is None:
            target_state = "inicio"
        else:
            target_state = target_state.lower().strip() if target_state else "inicio"
        
        # Verificar se os estados existem (incluindo None e string vazia)
        if not current_state or current_state == "none" or current_state == "" or current_state not in self.states:
            return False, f"Estado atual inválido: {current_state}"
        
        if not target_state or target_state == "none" or target_state == "" or target_state not in self.states:
            return False, f"Estado de destino inválido: {target_state}"
        
        # Verificar se a transição é permitida
        allowed_transitions = self.states[current_state]["allowed_transitions"]
        if target_state not in allowed_transitions:
            return False, f"Transição não permitida de '{current_state}' para '{target_state}'. Transições permitidas: {allowed_transitions}"
        
        return True, ""

    def validate_context_for_state(self, state: str, context: Dict) -> Tuple[bool, str, List[str]]:
        """
        Valida se o contexto tem as informações necessárias para o estado
        
        Returns:
            Tuple[bool, str, List[str]]: (is_valid, error_message, missing_fields)
        """
        if state is None:
            state = "inicio"
        else:
            state = state.lower().strip() if state else "inicio"
        
        # Verificar se estado é válido (incluindo None e string vazia)
        if not state or state == "none" or state == "" or state not in self.states:
            return False, f"Estado inválido: {state}", []
        
        state_info = self.states[state]
        required_context = state_info.get("required_context", [])
        
        missing_fields = []
        for field in required_context:
            if field not in context or context[field] is None or context[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Contexto incompleto para estado '{state}'. Campos faltando: {missing_fields}", missing_fields
        
        return True, "", []

    def get_state_info(self, state: str) -> Dict:
        """Retorna informações sobre o estado"""
        if state is None:
            state = "inicio"
        else:
            state = state.lower().strip() if state else "inicio"
        
        # Verificar se estado é válido (incluindo None e string vazia)
        if not state or state == "none" or state == "" or state not in self.states:
            return {
                "valid": False,
                "error": f"Estado inválido: {state}"
            }
        
        return {
            "valid": True,
            "state": state,
            "description": self.states[state]["description"],
            "allowed_transitions": self.states[state]["allowed_transitions"],
            "required_context": self.states[state]["required_context"],
            "optional_context": self.states[state]["optional_context"]
        }

    def suggest_next_states(self, current_state: str, context: Dict) -> List[str]:
        """Sugere próximos estados possíveis baseado no estado atual e contexto"""
        current_state = current_state.lower().strip() if current_state else "inicio"
        
        if current_state not in self.states:
            return []
        
        allowed_transitions = self.states[current_state]["allowed_transitions"]
        
        # Filtrar transições baseado no contexto
        suggested_states = []
        for target_state in allowed_transitions:
            is_valid, _ = self.can_transition_to(current_state, target_state)
            if is_valid:
                suggested_states.append(target_state)
        
        return suggested_states

    def get_required_context_for_state(self, state: str) -> List[str]:
        """Retorna os campos de contexto obrigatórios para um estado"""
        state = state.lower().strip() if state else "inicio"
        
        if state not in self.states:
            return []
        
        return self.states[state].get("required_context", [])

    def get_optional_context_for_state(self, state: str) -> List[str]:
        """Retorna os campos de contexto opcionais para um estado"""
        state = state.lower().strip() if state else "inicio"
        
        if state not in self.states:
            return []
        
        return self.states[state].get("optional_context", [])

    def validate_state_transition(self, current_state: str, target_state: str, context: Dict) -> Tuple[bool, str, Dict]:
        """
        Validação completa de transição de estado
        
        Returns:
            Tuple[bool, str, Dict]: (is_valid, error_message, suggestions)
        """
        # Verificar se a transição é permitida
        can_transition, transition_error = self.can_transition_to(current_state, target_state)
        if not can_transition:
            return False, transition_error, {"action": "invalid_transition"}
        
        # Verificar se o contexto é válido para o estado de destino
        context_valid, context_error, missing_fields = self.validate_context_for_state(target_state, context)
        if not context_valid:
            suggestions = {
                "action": "incomplete_context",
                "missing_fields": missing_fields,
                "suggested_action": f"Preencher campos: {', '.join(missing_fields)}"
            }
            return False, context_error, suggestions
        
        return True, "", {"action": "valid_transition"}

    def get_state_flow(self, start_state: str = "inicio") -> Dict:
        """Retorna o fluxo completo de estados a partir de um estado inicial"""
        flow = {}
        visited = set()
        
        def build_flow(state: str, depth: int = 0):
            if depth > 10 or state in visited:  # Evitar loops infinitos
                return
            
            visited.add(state)
            flow[state] = {
                "description": self.states.get(state, {}).get("description", ""),
                "transitions": self.states.get(state, {}).get("allowed_transitions", []),
                "required_context": self.states.get(state, {}).get("required_context", []),
                "depth": depth
            }
            
            # Recursivamente construir fluxo para estados de transição
            for next_state in self.states.get(state, {}).get("allowed_transitions", []):
                if next_state not in visited:
                    build_flow(next_state, depth + 1)
        
        build_flow(start_state)
        return flow 