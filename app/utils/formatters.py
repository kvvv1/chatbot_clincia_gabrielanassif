from datetime import datetime
from typing import List, Dict

class FormatterUtils:
    
    @staticmethod
    def formatar_data_brasil(data: datetime) -> str:
        """Formata data para padrão brasileiro"""
        return data.strftime("%d/%m/%Y")
    
    @staticmethod
    def formatar_hora_brasil(data: datetime) -> str:
        """Formata hora para padrão brasileiro"""
        return data.strftime("%H:%M")
    
    @staticmethod
    def formatar_data_hora_brasil(data: datetime) -> str:
        """Formata data e hora para padrão brasileiro"""
        return data.strftime("%d/%m/%Y às %H:%M")
    
    @staticmethod
    def get_dia_semana(data: datetime) -> str:
        """Retorna dia da semana em português"""
        dias = {
            0: "Segunda-feira",
            1: "Terça-feira", 
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        return dias[data.weekday()]
    
    @staticmethod
    def formatar_mensagem_agendamento(paciente: Dict, data: datetime, horario: str, profissional: str) -> str:
        """Formata mensagem de confirmação de agendamento"""
        return f"""
✅ *Consulta agendada com sucesso!*

📋 *Detalhes do agendamento:*
👤 Paciente: {paciente.get('nome', 'Paciente')}
📅 Data: {FormatterUtils.formatar_data_brasil(data)}
⏰ Horário: {horario}
👨‍⚕️ Profissional: {profissional}

📍 *Endereço:*
Clínica Gabriela Nassif
Rua Example, 123 - Savassi
Belo Horizonte - MG

💡 *Lembretes:*
• Chegue com 15 minutos de antecedência
• Traga documento com foto
• Traga carteira do convênio (se aplicável)

Você receberá um lembrete 24h antes da consulta.

Obrigado por escolher nossa clínica! 😊
"""
    
    @staticmethod
    def formatar_mensagem_lembrete(paciente: str, data: datetime, horario: str) -> str:
        """Formata mensagem de lembrete"""
        return f"""
📅 *Lembrete de Consulta*

Olá, {paciente}!

Este é um lembrete da sua consulta amanhã:

📆 Data: {FormatterUtils.formatar_data_brasil(data)}
⏰ Horário: {horario}
📍 Local: Clínica Gabriela Nassif

*Por favor, confirme sua presença:*

*1* - ✅ Confirmar presença
*2* - ❌ Não poderei comparecer
*3* - 📅 Reagendar

Digite a opção desejada.
"""
    
    @staticmethod
    def formatar_lista_agendamentos(agendamentos: List[Dict]) -> str:
        """Formata lista de agendamentos para exibição"""
        if not agendamentos:
            return "📅 Você não possui agendamentos futuros."
        
        mensagem = "📅 *Seus agendamentos:*\n\n"
        
        for i, ag in enumerate(agendamentos[:5], 1):  # Limitar a 5
            data = datetime.fromisoformat(ag['data_hora'])
            mensagem += (
                f"*{i}*\n"
                f"📆 {FormatterUtils.formatar_data_brasil(data)}\n"
                f"⏰ {FormatterUtils.formatar_hora_brasil(data)}\n"
                f"👨‍⚕️ {ag.get('profissional', 'Dr(a). Gabriela')}\n"
                f"📋 Status: {ag.get('status', 'Agendado')}\n\n"
            )
        
        return mensagem
    
    @staticmethod
    def formatar_menu_principal() -> str:
        """Formata menu principal"""
        return """
🏥 *Clínica Gabriela Nassif*

Como posso ajudar você hoje?

*1️⃣* - Agendar consulta
*2️⃣* - Ver meus agendamentos
*3️⃣* - Cancelar consulta
*4️⃣* - Lista de espera
*5️⃣* - Falar com atendente

Digite o número da opção desejada.
"""
    
    @staticmethod
    def formatar_saudacao() -> str:
        """Retorna saudação baseada no horário"""
        hora = datetime.now().hour
        
        if hora < 12:
            return "🌅 Bom dia!"
        elif hora < 18:
            return "☀️ Boa tarde!"
        else:
            return "🌙 Boa noite!" 