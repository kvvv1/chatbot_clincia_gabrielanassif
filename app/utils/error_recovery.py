from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Tipos de erro que podem ocorrer"""
    API_TIMEOUT = "api_timeout"
    API_UNAVAILABLE = "api_unavailable"
    INVALID_DATA = "invalid_data"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorRecoveryManager:
    """Gerenciador de recuperação de erros para o chatbot"""
    
    def __init__(self):
        self.retry_attempts = {}
        self.error_history = {}
        self.max_retries = 3
        self.retry_delays = [1, 3, 5]  # Delays em segundos
        
    async def handle_api_error(self, 
                             error_type: ErrorType, 
                             context: Dict, 
                             phone: str,
                             current_state: str) -> Tuple[str, Dict]:
        """Manipula erros de API e retorna resposta apropriada"""
        
        logger.warning(f"Erro de API detectado: {error_type.value} para {phone}")
        
        # Registrar erro no histórico
        self._record_error(phone, error_type, context)
        
        # Verificar se já tentamos muitas vezes
        if self._get_retry_count(phone) >= self.max_retries:
            return await self._handle_max_retries_exceeded(phone, current_state)
        
        # Incrementar contador de tentativas
        self._increment_retry_count(phone)
        
        # Gerar resposta baseada no tipo de erro e estado atual
        if error_type == ErrorType.API_TIMEOUT:
            return await self._handle_timeout_error(phone, current_state, context)
        elif error_type == ErrorType.API_UNAVAILABLE:
            return await self._handle_unavailable_error(phone, current_state, context)
        elif error_type == ErrorType.INVALID_DATA:
            return await self._handle_invalid_data_error(phone, current_state, context)
        elif error_type == ErrorType.NETWORK_ERROR:
            return await self._handle_network_error(phone, current_state, context)
        else:
            return await self._handle_generic_error(phone, current_state, context)

    async def _handle_timeout_error(self, phone: str, current_state: str, context: Dict) -> Tuple[str, Dict]:
        """Manipula erros de timeout"""
        retry_count = self._get_retry_count(phone)
        delay = self.retry_delays[min(retry_count - 1, len(self.retry_delays) - 1)]
        
        if current_state == "aguardando_cpf":
            message = f"""
⏰ *Sistema temporariamente lento*

Estamos verificando seus dados, mas o sistema está respondendo mais lentamente que o normal.

🔄 Tentativa {retry_count} de {self.max_retries}
⏳ Aguarde {delay} segundos...

Se o problema persistir, você pode:
• Tentar novamente em alguns minutos
• Falar com um atendente (digite *0*)
• Verificar sua conexão com a internet
"""
        elif current_state in ["escolhendo_data", "escolhendo_horario"]:
            message = f"""
⏰ *Verificando disponibilidade...*

Estamos consultando os horários disponíveis, mas o sistema está respondendo mais lentamente.

🔄 Tentativa {retry_count} de {self.max_retries}
⏳ Aguarde {delay} segundos...

Você pode:
• Aguardar mais alguns segundos
• Tentar novamente
• Escolher outra data
"""
        else:
            message = f"""
⏰ *Sistema temporariamente lento*

Estamos processando sua solicitação, mas o sistema está respondendo mais lentamente.

🔄 Tentativa {retry_count} de {self.max_retries}
⏳ Aguarde {delay} segundos...

Tentaremos novamente automaticamente.
"""
        
        return message, {"retry_after": delay, "should_retry": True}

    async def _handle_unavailable_error(self, phone: str, current_state: str, context: Dict) -> Tuple[str, Dict]:
        """Manipula erros de serviço indisponível"""
        
        if current_state == "aguardando_cpf":
            message = """
🔧 *Sistema de verificação temporariamente indisponível*

No momento, não conseguimos verificar seus dados automaticamente.

💡 *Alternativas:*
• Tente novamente em alguns minutos
• Fale com um atendente (digite *0*)
• Verifique se o CPF está correto

📞 *Atendimento humano:*
Se precisar de ajuda imediata, um atendente pode te ajudar.
"""
        elif current_state in ["escolhendo_data", "escolhendo_horario"]:
            message = """
🔧 *Sistema de agendamento temporariamente indisponível*

No momento, não conseguimos verificar os horários disponíveis.

💡 *Alternativas:*
• Tente novamente em alguns minutos
• Fale com um atendente para agendamento manual
• Entre em nossa lista de espera

📞 *Atendimento humano:*
Um atendente pode te ajudar com o agendamento.
"""
        else:
            message = """
🔧 *Sistema temporariamente indisponível*

Estamos enfrentando dificuldades técnicas no momento.

💡 *O que você pode fazer:*
• Tente novamente em alguns minutos
• Fale com um atendente (digite *0*)
• Verifique sua conexão com a internet

📞 *Atendimento humano disponível:*
Digite *0* para falar com um atendente.
"""
        
        return message, {"should_retry": False, "offer_human_support": True}

    async def _handle_invalid_data_error(self, phone: str, current_state: str, context: Dict) -> Tuple[str, Dict]:
        """Manipula erros de dados inválidos"""
        
        if current_state == "aguardando_cpf":
            message = """
❌ *CPF não encontrado ou inválido*

Não conseguimos encontrar um paciente com este CPF em nosso sistema.

💡 *Verifique:*
• Se o CPF está correto
• Se você já é paciente da clínica
• Se há espaços ou caracteres extras

🔄 *Tente novamente:*
Digite apenas os números do CPF (exemplo: 12345678901)

📞 *Precisa de ajuda?*
Digite *0* para falar com um atendente.
"""
        elif current_state in ["escolhendo_data", "escolhendo_horario"]:
            message = """
❌ *Data ou horário inválido*

A data ou horário selecionado não está disponível.

💡 *Tente:*
• Escolher outra data
• Escolher outro horário
• Verificar se a data não é no passado

🔄 *Opções:*
• Digite *1* para escolher outra data
• Digite *0* para falar com atendente
"""
        else:
            message = """
❌ *Dados inválidos*

Os dados fornecidos não puderam ser processados.

💡 *Verifique:*
• Se os dados estão corretos
• Se não há caracteres especiais desnecessários

🔄 *Tente novamente ou:*
• Digite *0* para falar com atendente
"""
        
        return message, {"should_retry": False, "invalid_data": True}

    async def _handle_network_error(self, phone: str, current_state: str, context: Dict) -> Tuple[str, Dict]:
        """Manipula erros de rede"""
        
        message = """
🌐 *Problema de conexão*

Estamos enfrentando problemas de conectividade.

💡 *Verifique:*
• Sua conexão com a internet
• Se o WhatsApp está funcionando normalmente

🔄 *Tente:*
• Aguardar alguns segundos e tentar novamente
• Verificar sua conexão
• Fechar e abrir o WhatsApp

📞 *Se o problema persistir:*
Digite *0* para falar com um atendente.
"""
        
        return message, {"should_retry": True, "retry_after": 5}

    async def _handle_generic_error(self, phone: str, current_state: str, context: Dict) -> Tuple[str, Dict]:
        """Manipula erros genéricos"""
        
        message = """
⚠️ *Erro inesperado*

Ocorreu um erro inesperado no sistema.

💡 *Tente:*
• Aguardar alguns segundos e tentar novamente
• Verificar se sua mensagem está clara

🔄 *Opções:*
• Digite *1* para tentar novamente
• Digite *0* para falar com atendente
• Digite *menu* para voltar ao menu principal
"""
        
        return message, {"should_retry": True, "retry_after": 3}

    async def _handle_max_retries_exceeded(self, phone: str, current_state: str) -> Tuple[str, Dict]:
        """Manipula quando o número máximo de tentativas foi excedido"""
        
        message = """
🔄 *Muitas tentativas*

Identificamos muitas tentativas consecutivas com problemas.

💡 *Recomendamos:*
• Aguardar alguns minutos antes de tentar novamente
• Verificar sua conexão com a internet
• Falar com um atendente para resolver o problema

📞 *Atendimento humano:*
Digite *0* para falar com um atendente que pode te ajudar.

🕐 *Tempo de espera estimado:* 2-5 minutos
"""
        
        # Resetar contador de tentativas após um tempo
        asyncio.create_task(self._reset_retry_count_after_delay(phone, 300))  # 5 minutos
        
        return message, {"should_retry": False, "max_retries_exceeded": True}

    def _record_error(self, phone: str, error_type: ErrorType, context: Dict):
        """Registra erro no histórico"""
        if phone not in self.error_history:
            self.error_history[phone] = []
        
        self.error_history[phone].append({
            "timestamp": datetime.now(),
            "error_type": error_type.value,
            "context": context
        })
        
        # Manter apenas os últimos 10 erros
        if len(self.error_history[phone]) > 10:
            self.error_history[phone] = self.error_history[phone][-10:]

    def _get_retry_count(self, phone: str) -> int:
        """Obtém o número de tentativas para um telefone"""
        return self.retry_attempts.get(phone, 0)

    def _increment_retry_count(self, phone: str):
        """Incrementa o contador de tentativas"""
        self.retry_attempts[phone] = self._get_retry_count(phone) + 1

    def reset_retry_count(self, phone: str):
        """Reseta o contador de tentativas"""
        if phone in self.retry_attempts:
            del self.retry_attempts[phone]

    async def _reset_retry_count_after_delay(self, phone: str, delay_seconds: int):
        """Reseta o contador de tentativas após um delay"""
        await asyncio.sleep(delay_seconds)
        self.reset_retry_count(phone)

    def get_error_summary(self, phone: str) -> Dict:
        """Obtém resumo dos erros para um telefone"""
        if phone not in self.error_history:
            return {"total_errors": 0, "recent_errors": []}
        
        errors = self.error_history[phone]
        recent_errors = [e for e in errors if (datetime.now() - e["timestamp"]).seconds < 3600]  # Última hora
        
        return {
            "total_errors": len(errors),
            "recent_errors": len(recent_errors),
            "last_error": errors[-1] if errors else None
        }

    def should_offer_human_support(self, phone: str) -> bool:
        """Determina se deve oferecer suporte humano baseado no histórico de erros"""
        summary = self.get_error_summary(phone)
        return summary["recent_errors"] >= 3 or summary["total_errors"] >= 5 