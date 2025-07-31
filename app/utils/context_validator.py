import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContextValidator:
    """Sistema robusto de validação de contexto para conversas"""
    
    def __init__(self):
        # Estados válidos do sistema
        self.valid_states = {
            "inicio",
            "menu_principal", 
            "aguardando_cpf",
            "escolhendo_tipo_consulta",
            "escolhendo_data",
            "escolhendo_horario",
            "confirmando_agendamento",
            "aguardando_observacoes",
            "visualizando_agendamentos",
            "cancelando_consulta",
            "confirmando_cancelamento",
            "lista_espera",
            "finalizada"
        }
        
        # Padrões de validação por estado
        self.state_validation_patterns = {
            "inicio": {
                "valid_inputs": ["oi", "olá", "ola", "hi", "hello", "1", "2", "3", "4", "5", "0"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "menu_principal": {
                "valid_inputs": ["1", "2", "3", "4", "5", "0"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "aguardando_cpf": {
                "valid_inputs": [],  # Qualquer CPF válido
                "cpf_allowed": True,
                "menu_options_allowed": False
            },
            "escolhendo_tipo_consulta": {
                "valid_inputs": ["1", "2", "3", "4", "5"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "escolhendo_data": {
                "valid_inputs": ["1", "2", "3", "4", "5", "6", "7"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "escolhendo_horario": {
                "valid_inputs": ["1", "2", "3", "4", "5", "6", "7", "8"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "confirmando_agendamento": {
                "valid_inputs": ["1", "2", "3"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "aguardando_observacoes": {
                "valid_inputs": [],  # Qualquer texto
                "cpf_allowed": False,
                "menu_options_allowed": False
            },
            "visualizando_agendamentos": {
                "valid_inputs": ["0", "1", "2", "3"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "cancelando_consulta": {
                "valid_inputs": ["0", "1", "2", "3", "4", "5"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "confirmando_cancelamento": {
                "valid_inputs": ["1", "2"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "lista_espera": {
                "valid_inputs": ["1"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            },
            "finalizada": {
                "valid_inputs": ["oi", "olá", "ola", "hi", "hello", "1"],
                "cpf_allowed": False,
                "menu_options_allowed": True
            }
        }

    def validate_message_for_state(self, message: str, state: str, context: Dict) -> Tuple[bool, str, Dict]:
        """
        Valida se a mensagem é apropriada para o estado atual
        
        Returns:
            Tuple[bool, str, Dict]: (is_valid, error_message, suggested_action)
        """
        logger.info(f"=== VALIDANDO MENSAGEM PARA ESTADO ===")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Estado: '{state}'")
        logger.info(f"Contexto: {context}")
        
        # Normalizar estado
        if state is None:
            state = "inicio"
        elif state == "":
            state = "inicio"
        else:
            state = state.lower().strip() if state else "inicio"
        
        # Verificar se estado é válido
        if state not in self.valid_states:
            logger.warning(f"Estado inválido: {state}")
            return False, f"Estado inválido: {state}", {"action": "reset_to_inicio"}
        
        # Obter padrões de validação para o estado
        validation_patterns = self.state_validation_patterns.get(state, {})
        
        # Normalizar mensagem
        message_normalized = message.strip().lower()
        
        # Verificar se é CPF
        is_cpf = self._is_cpf(message)
        logger.info(f"É CPF: {is_cpf}")
        
        # Verificar se é opção de menu
        is_menu_option = self._is_menu_option(message_normalized)
        logger.info(f"É opção de menu: {is_menu_option}")
        
        # Validação específica por estado
        if state == "aguardando_cpf":
            if is_cpf:
                logger.info("CPF válido detectado no estado aguardando_cpf")
                return True, "", {"action": "process_cpf", "cpf": self._clean_cpf(message)}
            else:
                logger.warning("CPF inválido no estado aguardando_cpf")
                return False, "Por favor, digite um CPF válido (apenas números).", {"action": "ask_for_cpf_again"}
        
        elif state == "menu_principal":
            if is_cpf:
                logger.warning("CPF detectado no menu principal - contexto incorreto")
                return False, "⚠️ Parece que você digitou um CPF!\n\nPara agendar uma consulta, primeiro selecione uma opção:\n\n1️⃣ *Agendar consulta*\n2️⃣ *Ver meus agendamentos*\n3️⃣ *Cancelar consulta*\n4️⃣ *Lista de espera*\n5️⃣ *Falar com atendente*\n\nDigite o número da opção desejada.", {"action": "show_menu_again"}
            elif is_menu_option:
                valid_options = validation_patterns.get("valid_inputs", [])
                if message_normalized in valid_options:
                    logger.info("Opção de menu válida")
                    return True, "", {"action": "process_menu_option", "option": message_normalized}
                else:
                    logger.warning("Opção de menu inválida")
                    return False, "Opção inválida! 😅\n\nPor favor, digite um número de *1 a 5*.\n\nOu digite *0* para sair.", {"action": "show_menu_again"}
            else:
                logger.warning("Entrada inválida no menu principal")
                return False, "Opção inválida! 😅\n\nPor favor, digite um número de *1 a 5*.\n\nOu digite *0* para sair.", {"action": "show_menu_again"}
        
        elif state in ["escolhendo_tipo_consulta", "escolhendo_profissional", "escolhendo_data", "escolhendo_horario"]:
            if is_cpf:
                logger.warning("CPF detectado em estado de escolha - contexto incorreto")
                return False, "⚠️ Parece que você digitou um CPF!\n\nPor favor, escolha uma das opções disponíveis.", {"action": "show_current_options"}
            elif is_menu_option:
                valid_options = validation_patterns.get("valid_inputs", [])
                if message_normalized in valid_options:
                    logger.info("Opção válida para estado de escolha")
                    return True, "", {"action": "process_choice", "choice": message_normalized}
                else:
                    logger.warning("Opção inválida para estado de escolha")
                    return False, "❌ Opção inválida!\n\nPor favor, escolha um número válido.", {"action": "show_current_options"}
            else:
                logger.warning("Entrada inválida em estado de escolha")
                return False, "❌ Por favor, digite apenas o número da opção desejada.", {"action": "show_current_options"}
        
        elif state == "confirmando_agendamento":
            if is_cpf:
                logger.warning("CPF detectado na confirmação - contexto incorreto")
                return False, "⚠️ Parece que você digitou um CPF!\n\nPor favor, confirme o agendamento:\n\n*1* - ✅ Sim, confirmar\n*2* - ❌ Não, cancelar\n*3* - 📝 Adicionar observações", {"action": "show_confirmation_options"}
            elif is_menu_option:
                valid_options = validation_patterns.get("valid_inputs", [])
                if message_normalized in valid_options:
                    logger.info("Opção válida para confirmação")
                    return True, "", {"action": "process_confirmation", "option": message_normalized}
                else:
                    logger.warning("Opção inválida para confirmação")
                    return False, "Por favor, digite:\n*1* para confirmar\n*2* para cancelar\n*3* para adicionar observações", {"action": "show_confirmation_options"}
            else:
                logger.warning("Entrada inválida na confirmação")
                return False, "Por favor, digite:\n*1* para confirmar\n*2* para cancelar\n*3* para adicionar observações", {"action": "show_confirmation_options"}
        
        elif state == "aguardando_observacoes":
            # Qualquer texto é válido, exceto comandos específicos
            if message_normalized in ["pular", "skip", "não", "nao"]:
                logger.info("Observações puladas")
                return True, "", {"action": "skip_observations"}
            else:
                logger.info("Observações fornecidas")
                return True, "", {"action": "save_observations", "observations": message}
        
        elif state == "inicio":
            # No início, aceitar saudações ou opções de menu
            if self._is_greeting(message_normalized):
                logger.info("Saudação detectada no início")
                return True, "", {"action": "show_welcome"}
            elif is_menu_option:
                logger.info("Opção de menu detectada no início")
                return True, "", {"action": "process_menu_option", "option": message_normalized}
            elif is_cpf:
                logger.warning("CPF detectado no estado início - contexto incorreto")
                return False, "⚠️ Parece que você digitou um CPF!\n\nPor favor, digite *oi* para começar ou selecione uma opção do menu.", {"action": "show_welcome"}
            else:
                logger.info("Entrada genérica no início")
                return True, "", {"action": "show_welcome"}
        
        else:
            # Para outros estados, verificar opções válidas
            valid_options = validation_patterns.get("valid_inputs", [])
            if message_normalized in valid_options:
                logger.info("Opção válida para estado genérico")
                return True, "", {"action": "process_option", "option": message_normalized}
            else:
                logger.warning("Opção inválida para estado genérico")
                return False, "Opção inválida! Por favor, escolha uma das opções disponíveis.", {"action": "show_current_options"}

    def _is_cpf(self, message: str) -> bool:
        """Verifica se a mensagem é um CPF válido"""
        # Limpar CPF
        cpf_clean = re.sub(r'[^0-9]', '', message)
        
        # Verificar se tem 11 dígitos
        if len(cpf_clean) != 11:
            return False
        
        # Verificar se são todos números
        if not cpf_clean.isdigit():
            return False
        
        # Validação básica de CPF (algoritmo)
        if len(set(cpf_clean)) == 1:  # Todos os dígitos iguais
            return False
        
        # Calcular dígitos verificadores
        soma = 0
        for i in range(9):
            soma += int(cpf_clean[i]) * (10 - i)
        
        resto = soma % 11
        if resto < 2:
            digito1 = 0
        else:
            digito1 = 11 - resto
        
        soma = 0
        for i in range(10):
            soma += int(cpf_clean[i]) * (11 - i)
        
        resto = soma % 11
        if resto < 2:
            digito2 = 0
        else:
            digito2 = 11 - resto
        
        return cpf_clean[9] == str(digito1) and cpf_clean[10] == str(digito2)

    def _clean_cpf(self, message: str) -> str:
        """Limpa CPF removendo caracteres especiais"""
        return re.sub(r'[^0-9]', '', message)

    def _is_menu_option(self, message: str) -> bool:
        """Verifica se a mensagem é uma opção de menu"""
        return message in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def _is_greeting(self, message: str) -> bool:
        """Verifica se a mensagem é uma saudação"""
        greetings = ["oi", "olá", "ola", "hi", "hello", "bom dia", "boa tarde", "boa noite"]
        return any(greeting in message for greeting in greetings)

    def get_state_info(self, state: str) -> Dict:
        """Retorna informações sobre o estado atual"""
        state = state.lower().strip() if state else "inicio"
        
        if state not in self.valid_states:
            return {
                "valid": False,
                "error": f"Estado inválido: {state}",
                "suggested_action": "reset_to_inicio"
            }
        
        validation_patterns = self.state_validation_patterns.get(state, {})
        
        return {
            "valid": True,
            "state": state,
            "valid_inputs": validation_patterns.get("valid_inputs", []),
            "cpf_allowed": validation_patterns.get("cpf_allowed", False),
            "menu_options_allowed": validation_patterns.get("menu_options_allowed", False)
        }

    def suggest_next_action(self, state: str, context: Dict) -> Dict:
        """Sugere a próxima ação baseada no estado e contexto"""
        state = state.lower().strip() if state else "inicio"
        
        suggestions = {
            "inicio": {
                "action": "show_welcome",
                "message": "Mostrar saudação e menu principal"
            },
            "menu_principal": {
                "action": "wait_for_menu_choice",
                "message": "Aguardar escolha do menu"
            },
            "aguardando_cpf": {
                "action": "wait_for_cpf",
                "message": "Aguardar CPF do usuário"
            },
            "escolhendo_tipo_consulta": {
                "action": "show_consultation_types",
                "message": "Mostrar tipos de consulta disponíveis"
            },
            "escolhendo_profissional": {
                "action": "show_professionals",
                "message": "Mostrar profissionais disponíveis"
            },
            "escolhendo_data": {
                "action": "show_available_dates",
                "message": "Mostrar datas disponíveis"
            },
            "escolhendo_horario": {
                "action": "show_available_times",
                "message": "Mostrar horários disponíveis"
            },
            "confirmando_agendamento": {
                "action": "show_confirmation",
                "message": "Mostrar confirmação do agendamento"
            },
            "aguardando_observacoes": {
                "action": "wait_for_observations",
                "message": "Aguardar observações do usuário"
            }
        }
        
        return suggestions.get(state, {
            "action": "unknown_state",
            "message": f"Estado desconhecido: {state}"
        }) 