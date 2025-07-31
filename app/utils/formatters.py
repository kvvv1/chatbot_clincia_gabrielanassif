from datetime import datetime
from typing import List, Dict, Optional
import locale

# Tentar configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass

class FormatterUtils:
    """Utilidades para formatação de mensagens"""
    
    @staticmethod
    def formatar_saudacao() -> str:
        """Retorna saudação baseada no horário"""
        hora = datetime.now().hour
        
        if 6 <= hora < 12:
            return "🌅 Bom dia!"
        elif 12 <= hora < 18:
            return "☀️ Boa tarde!"
        else:
            return "🌙 Boa noite!"
    
    @staticmethod
    def formatar_data_brasil(data: datetime) -> str:
        """Formata data no padrão brasileiro"""
        dias_semana = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        dia_semana = dias_semana[data.weekday()]
        return f"{dia_semana}, {data.day} de {meses[data.month]} de {data.year}"
    
    @staticmethod
    def formatar_hora_brasil(data: datetime) -> str:
        """Formata hora no padrão brasileiro"""
        return data.strftime("%H:%M")
    
    @staticmethod
    def formatar_menu_principal() -> str:
        """Retorna menu principal formatado"""
        return """
*Digite o número da opção desejada:*

1️⃣ *Agendar consulta*
2️⃣ *Ver meus agendamentos*  
3️⃣ *Cancelar consulta*
4️⃣ *Lista de espera*
5️⃣ *Falar com atendente*

Digite *0* para sair
"""
    
    @staticmethod
    def formatar_lista_agendamentos(agendamentos: List[Dict]) -> str:
        """Formata lista de agendamentos"""
        if not agendamentos:
            return "📅 Você não possui agendamentos."
        
        mensagem = "📅 *Seus agendamentos:*\n\n"
        
        for i, ag in enumerate(agendamentos[:5], 1):
            try:
                # Tentar diferentes formatos de data
                data_str = ag.get('data_hora', ag.get('data', ''))
                
                if 'T' in data_str:
                    data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                elif ' ' in data_str:
                    data = datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")
                else:
                    data = datetime.strptime(data_str, "%Y-%m-%d")
                
                mensagem += f"*{i}.* {FormatterUtils.formatar_data_brasil(data)}\n"
                mensagem += f"   ⏰ {FormatterUtils.formatar_hora_brasil(data)}\n"
                mensagem += f"   👩‍⚕️ {ag.get('profissional', 'Dra. Gabriela Nassif')}\n"
                mensagem += f"   📋 {ag.get('tipo', 'Consulta médica')}\n"
                mensagem += f"   ✅ Status: {ag.get('status', 'Confirmado')}\n\n"
                
            except Exception as e:
                continue
        
        return mensagem
    
    @staticmethod
    def formatar_mensagem_agendamento(paciente: Dict, data_hora: datetime, 
                                    horario: str, profissional: str) -> str:
        """Formata mensagem de confirmação de agendamento"""
        return f"""
✅ *Agendamento confirmado com sucesso!*

📋 *Detalhes da consulta:*
👤 Paciente: {paciente.get('nome', 'Paciente')}
📅 Data: {FormatterUtils.formatar_data_brasil(data_hora)}
⏰ Horário: {horario}
👩‍⚕️ Profissional: {profissional}

📍 *Endereço:*
Clínica Gabriela Nassif
Rua Example, 123 - Savassi
Belo Horizonte - MG

💡 *Lembretes importantes:*
• Chegue com 15 minutos de antecedência
• Traga documento com foto e cartão do convênio (se houver)
• Em caso de sintomas gripais, use máscara
• Para cancelar ou reagendar, entre em contato com antecedência

📞 *Contato:*
Telefone: (31) 9999-9999
WhatsApp: (31) 99999-9999

Agradecemos a confiança! 😊
"""
    
    @staticmethod
    def formatar_erro_sistema() -> str:
        """Mensagem de erro do sistema"""
        return """
⚠️ *Ops! Algo deu errado*

Estamos com uma instabilidade temporária no sistema.

Por favor, tente novamente em alguns instantes ou entre em contato:

📞 Telefone: (31) 9999-9999
📧 Email: contato@clinica.com.br

Pedimos desculpas pelo transtorno! 🙏
"""
    
    @staticmethod
    def formatar_lista_espera_confirmacao() -> str:
        """Mensagem de confirmação de lista de espera"""
        return """
✅ *Você foi adicionado à lista de espera!*

📋 Assim que surgir uma vaga disponível, entraremos em contato pelo WhatsApp.

⏰ *Importante:*
• Mantenha seu WhatsApp ativo
• Responda rapidamente quando entrarmos em contato
• A vaga será oferecida por ordem de chegada

💡 *Dica:* Você também pode ligar para verificar se surgiram vagas:
📞 (31) 9999-9999

Obrigado pela paciência! 🙏
"""
    
    @staticmethod
    def formatar_cancelamento_confirmado() -> str:
        """Mensagem de cancelamento confirmado"""
        return """
✅ *Consulta cancelada com sucesso!*

Sua consulta foi cancelada conforme solicitado.

Caso deseje reagendar, estamos à disposição:
• Digite *1* para agendar nova consulta
• Digite *0* para sair

Esperamos vê-lo em breve! 😊
"""
    
    @staticmethod
    def truncar_texto(texto: str, max_chars: int = 50) -> str:
        """Trunca texto longo adicionando reticências"""
        if len(texto) <= max_chars:
            return texto
        return texto[:max_chars-3] + "..."
    
    @staticmethod
    def formatar_tempo_espera(minutos: int) -> str:
        """Formata tempo de espera em formato legível"""
        if minutos < 60:
            return f"{minutos} minutos"
        
        horas = minutos // 60
        mins = minutos % 60
        
        if mins == 0:
            return f"{horas} hora{'s' if horas > 1 else ''}"
        
        return f"{horas} hora{'s' if horas > 1 else ''} e {mins} minutos"