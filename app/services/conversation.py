from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Conversation, Appointment, WaitingList, get_db
from app.services.whatsapp import WhatsAppService
from app.services.gestaods import GestaoDS
from app.utils.validators import ValidatorUtils
from app.utils.formatters import FormatterUtils
from app.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.gestaods = GestaoDS()
        self.validator = ValidatorUtils()

    async def processar_mensagem(self, phone: str, message: str,
                                message_id: str, db: Session):
        """Processa mensagem e retorna resposta apropriada"""

        # Marcar mensagem como lida
        await self.whatsapp.mark_as_read(phone, message_id)

        # Buscar ou criar conversa
        conversa = self._get_or_create_conversation(phone, db)

        # Processar baseado no estado atual
        estado = conversa.state
        contexto = conversa.context or {}

        # Log para debug
        logger.info(f"Estado atual: {estado}, Mensagem: {message}")

        # Máquina de estados
        if estado == "inicio":
            await self._handle_inicio(phone, message, conversa, db)

        elif estado == "menu_principal":
            await self._handle_menu_principal(phone, message, conversa, db)

        elif estado == "aguardando_cpf":
            await self._handle_cpf(phone, message, conversa, db)

        elif estado == "escolhendo_data":
            await self._handle_escolha_data(phone, message, conversa, db)

        elif estado == "escolhendo_horario":
            await self._handle_escolha_horario(phone, message, conversa, db)

        elif estado == "confirmando_agendamento":
            await self._handle_confirmacao(phone, message, conversa, db)

        elif estado == "visualizando_agendamentos":
            await self._handle_visualizar_agendamentos(phone, message, conversa, db)

        elif estado == "cancelando_consulta":
            await self._handle_cancelamento(phone, message, conversa, db)

        elif estado == "lista_espera":
            await self._handle_lista_espera(phone, message, conversa, db)

        else:
            # Estado desconhecido, reiniciar
            conversa.state = "inicio"
            db.commit()
            await self._handle_inicio(phone, message, conversa, db)

    async def _handle_inicio(self, phone: str, message: str,
                           conversa: Conversation, db: Session):
        """Handler do estado inicial"""

        # Enviar saudação e menu
        saudacao = FormatterUtils.formatar_saudacao()
        menu_text = f"""
{saudacao} Bem-vindo(a) à *{settings.clinic_name}*! 🏥

Sou seu assistente virtual e estou aqui para ajudar com seus agendamentos.

{FormatterUtils.formatar_menu_principal()}
        """

        await self.whatsapp.send_text(phone, menu_text)

        # Atualizar estado
        conversa.state = "menu_principal"
        db.commit()

    async def _handle_menu_principal(self, phone: str, message: str,
                                   conversa: Conversation, db: Session):
        """Handler do menu principal"""

        opcao = message.strip()

        if opcao == "1":
            await self.whatsapp.send_text(
                phone,
                "Vamos agendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "agendar"}

        elif opcao == "2":
            await self.whatsapp.send_text(
                phone,
                "Para ver seus agendamentos, preciso do seu *CPF*.\n\n"
                "Digite seu CPF (apenas números):"
            )
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "visualizar"}

        elif opcao == "3":
            await self.whatsapp.send_text(
                phone,
                "Para cancelar uma consulta, preciso do seu *CPF*.\n\n"
                "Digite seu CPF (apenas números):"
            )
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "cancelar"}

        elif opcao == "4":
            await self.whatsapp.send_text(
                phone,
                "Vou adicionar você na lista de espera! 📝\n\n"
                "Digite seu *CPF* (apenas números):"
            )
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "lista_espera"}

        elif opcao == "5":
            await self.whatsapp.send_text(
                phone,
                "Vou transferir você para um atendente! 👨‍⚕️\n\n"
                "Em breve alguém da nossa equipe entrará em contato.\n\n"
                "Horário de atendimento:\n"
                "📅 Segunda a Sexta: 8h às 18h\n"
                "📅 Sábado: 8h às 12h"
            )
            conversa.state = "inicio"

        else:
            await self.whatsapp.send_text(
                phone,
                "Opção inválida! 😅\n\n"
                "Por favor, digite um número de *1 a 5*."
            )

        db.commit()

    async def _handle_cpf(self, phone: str, message: str,
                         conversa: Conversation, db: Session):
        """Handler para validação de CPF"""

        # Limpar CPF
        cpf = re.sub(r'[^0-9]', '', message)

        # Validar CPF
        if not self.validator.validar_cpf(cpf):
            await self.whatsapp.send_text(
                phone,
                "❌ CPF inválido!\n\n"
                "Por favor, digite um CPF válido (apenas números):"
            )
            return

        # Buscar paciente na API
        paciente = await self.gestaods.buscar_paciente_cpf(cpf)

        if not paciente:
            await self.whatsapp.send_text(
                phone,
                "❌ CPF não encontrado em nosso sistema.\n\n"
                "Por favor, verifique o número e tente novamente.\n\n"
                "Se você é um novo paciente, entre em contato "
                "pelo telefone para realizar seu cadastro.\n\n"
                "📞 (31) 9999-9999"
            )
            conversa.state = "inicio"
            db.commit()
            return

        # Salvar dados do paciente no contexto
        contexto = conversa.context or {}
        contexto['paciente'] = {
            'id': paciente.get('id'),
            'nome': paciente.get('nome'),
            'cpf': cpf,
            'telefone': paciente.get('telefone', phone)
        }
        conversa.context = contexto

        # Continuar fluxo baseado na ação
        acao = contexto.get('acao')

        if acao == "agendar":
            await self._iniciar_agendamento(phone, paciente, conversa, db)
        elif acao == "visualizar":
            await self._mostrar_agendamentos(phone, paciente, conversa, db)
        elif acao == "cancelar":
            await self._iniciar_cancelamento(phone, paciente, conversa, db)
        elif acao == "lista_espera":
            await self._adicionar_lista_espera(phone, paciente, conversa, db)

        db.commit()

    async def _iniciar_agendamento(self, phone: str, paciente: Dict,
                                  conversa: Conversation, db: Session):
        """Inicia processo de agendamento"""

        nome = paciente.get('nome', 'Paciente')

        # Gerar opções de datas (próximos 7 dias úteis)
        datas_disponiveis = self._gerar_datas_disponiveis()

        mensagem = f"""
Olá, *{nome}*! 😊

Vamos agendar sua consulta.

📅 *Escolha uma data:*
"""

        # Adicionar opções de data
        for i, data in enumerate(datas_disponiveis, 1):
            mensagem += f"\n*{i}* - {data['formatado']}"

        mensagem += "\n\nDigite o número da data desejada:"

        await self.whatsapp.send_text(phone, mensagem)

        # Salvar datas no contexto
        contexto = conversa.context
        contexto['datas_disponiveis'] = datas_disponiveis
        conversa.context = contexto
        conversa.state = "escolhendo_data"

    async def _handle_escolha_data(self, phone: str, message: str,
                                  conversa: Conversation, db: Session):
        """Handler para escolha de data"""

        try:
            opcao = int(message.strip())
            contexto = conversa.context
            datas = contexto.get('datas_disponiveis', [])

            if 1 <= opcao <= len(datas):
                data_escolhida = datas[opcao - 1]
                contexto['data_escolhida'] = data_escolhida

                # Buscar horários disponíveis para a data
                data_inicio = datetime.strptime(data_escolhida['data'], '%Y-%m-%d')
                data_fim = data_inicio + timedelta(days=1)

                horarios = await self.gestaods.listar_horarios_disponiveis(
                    data_inicio, data_fim
                )

                if not horarios:
                    await self.whatsapp.send_text(
                        phone,
                        "😔 Não há horários disponíveis para esta data.\n\n"
                        "Por favor, escolha outra data:"
                    )
                    return

                # Mostrar horários disponíveis
                mensagem = f"""
📅 Data: *{data_escolhida['formatado']}*

⏰ *Horários disponíveis:*
"""

                for i, horario in enumerate(horarios[:8], 1):  # Limitar a 8 opções
                    mensagem += f"\n*{i}* - {horario['hora']}"

                mensagem += "\n\nDigite o número do horário desejado:"

                await self.whatsapp.send_text(phone, mensagem)

                contexto['horarios_disponiveis'] = horarios
                conversa.context = contexto
                conversa.state = "escolhendo_horario"

            else:
                await self.whatsapp.send_text(
                    phone,
                    "❌ Opção inválida!\n\n"
                    "Por favor, escolha um número válido."
                )

        except ValueError:
            await self.whatsapp.send_text(
                phone,
                "❌ Por favor, digite apenas o número da opção desejada."
            )

        db.commit()

    async def _handle_escolha_horario(self, phone: str, message: str,
                                     conversa: Conversation, db: Session):
        """Handler para escolha de horário"""

        try:
            opcao = int(message.strip())
            contexto = conversa.context
            horarios = contexto.get('horarios_disponiveis', [])

            if 1 <= opcao <= len(horarios):
                horario_escolhido = horarios[opcao - 1]
                contexto['horario_escolhido'] = horario_escolhido

                # Mostrar resumo para confirmação
                paciente = contexto.get('paciente', {})
                data = contexto.get('data_escolhida', {})

                mensagem = f"""
✅ *Confirmar agendamento:*

👤 Paciente: *{paciente.get('nome')}*
📅 Data: *{data.get('formatado')}*
⏰ Horário: *{horario_escolhido.get('hora')}*
👨‍⚕️ Profissional: *{horario_escolhido.get('profissional')}*

*Confirma o agendamento?*

*1* - ✅ Sim, confirmar
*2* - ❌ Não, cancelar
"""

                await self.whatsapp.send_text(phone, mensagem)

                conversa.context = contexto
                conversa.state = "confirmando_agendamento"

            else:
                await self.whatsapp.send_text(
                    phone,
                    "❌ Opção inválida!\n\n"
                    "Por favor, escolha um número válido."
                )

        except ValueError:
            await self.whatsapp.send_text(
                phone,
                "❌ Por favor, digite apenas o número da opção desejada."
            )

        db.commit()

    async def _handle_confirmacao(self, phone: str, message: str,
                                 conversa: Conversation, db: Session):
        """Handler para confirmação de agendamento"""

        opcao = message.strip()

        if opcao == "1":
            contexto = conversa.context
            paciente = contexto.get('paciente', {})
            data = contexto.get('data_escolhida', {})
            horario = contexto.get('horario_escolhido', {})

            # Construir data/hora completa
            data_hora_str = f"{data['data']} {horario['hora']}"
            data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")

            # Criar agendamento na API
            agendamento = await self.gestaods.criar_agendamento(
                paciente_id=paciente['id'],
                data_hora=data_hora,
                tipo="consulta",
                observacoes="Agendado via WhatsApp"
            )

            if agendamento:
                # Salvar no banco local para lembretes
                novo_agendamento = Appointment(
                    patient_id=str(paciente['id']),
                    patient_name=paciente['nome'],
                    patient_phone=phone,
                    appointment_date=data_hora,
                    appointment_type="consulta",
                    status="scheduled"
                )
                db.add(novo_agendamento)
                db.commit()

                # Enviar confirmação
                mensagem = FormatterUtils.formatar_mensagem_agendamento(
                    paciente, data_hora, horario['hora'], horario['profissional']
                )

                await self.whatsapp.send_text(phone, mensagem)

                # Verificar se há alguém na lista de espera para notificar
                await self._verificar_lista_espera_para_outras_datas(db)

            else:
                await self.whatsapp.send_text(
                    phone,
                    "❌ Erro ao agendar consulta.\n\n"
                    "Por favor, tente novamente ou entre em contato."
                )

            # Resetar conversa
            conversa.state = "inicio"
            conversa.context = {}

        elif opcao == "2":
            await self.whatsapp.send_text(
                phone,
                "❌ Agendamento cancelado.\n\n"
                "Se desejar, podemos tentar outro horário.\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"
            conversa.context = {}

        else:
            await self.whatsapp.send_text(
                phone,
                "Por favor, digite:\n"
                "*1* para confirmar\n"
                "*2* para cancelar"
            )

        db.commit()

    async def _mostrar_agendamentos(self, phone: str, paciente: Dict,
                                   conversa: Conversation, db: Session):
        """Mostra agendamentos do paciente"""

        agendamentos = await self.gestaods.listar_agendamentos_paciente(
            paciente['id']
        )

        if not agendamentos:
            await self.whatsapp.send_text(
                phone,
                "📅 Você não possui agendamentos futuros.\n\n"
                "Digite *1* para agendar uma consulta\n"
                "Digite *0* para voltar ao menu"
            )
        else:
            mensagem = FormatterUtils.formatar_lista_agendamentos(agendamentos)
            mensagem += "\n\nDigite *0* para voltar ao menu"

            await self.whatsapp.send_text(phone, mensagem)

        conversa.state = "visualizando_agendamentos"
        db.commit()

    async def _handle_visualizar_agendamentos(self, phone: str, message: str,
                                             conversa: Conversation, db: Session):
        """Handler para visualização de agendamentos"""

        opcao = message.strip()

        if opcao == "0":
            await self._handle_inicio(phone, message, conversa, db)
        elif opcao == "1":
            conversa.context = {"acao": "agendar"}
            conversa.state = "aguardando_cpf"
            await self.whatsapp.send_text(
                phone,
                "Vamos agendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
        else:
            await self.whatsapp.send_text(
                phone,
                "Opção inválida! Digite *0* para voltar ao menu ou *1* para agendar."
            )

        db.commit()

    async def _iniciar_cancelamento(self, phone: str, paciente: Dict,
                                   conversa: Conversation, db: Session):
        """Inicia processo de cancelamento"""
        # Implementação futura
        await self.whatsapp.send_text(
            phone,
            "Funcionalidade de cancelamento será implementada em breve."
        )
        conversa.state = "inicio"
        conversa.context = {}

    async def _adicionar_lista_espera(self, phone: str, paciente: Dict,
                                     conversa: Conversation, db: Session):
        """Adiciona paciente à lista de espera"""
        # Implementação futura
        await self.whatsapp.send_text(
            phone,
            "Funcionalidade de lista de espera será implementada em breve."
        )
        conversa.state = "inicio"
        conversa.context = {}

    def _get_or_create_conversation(self, phone: str, db: Session) -> Conversation:
        """Busca ou cria uma conversa"""
        conversa = db.query(Conversation).filter_by(phone=phone).first()

        if not conversa:
            conversa = Conversation(phone=phone)
            db.add(conversa)
            db.commit()

        return conversa

    def _gerar_datas_disponiveis(self, dias: int = 7) -> List[Dict]:
        """Gera lista de datas disponíveis (dias úteis)"""
        datas = []
        data_atual = datetime.now()

        while len(datas) < dias:
            data_atual += timedelta(days=1)

            # Pular fins de semana
            if data_atual.weekday() < 5:  # 0-4 = Seg-Sex
                datas.append({
                    'data': data_atual.strftime('%Y-%m-%d'),
                    'formatado': data_atual.strftime('%d/%m/%Y - %A').replace(
                        'Monday', 'Segunda').replace(
                        'Tuesday', 'Terça').replace(
                        'Wednesday', 'Quarta').replace(
                        'Thursday', 'Quinta').replace(
                        'Friday', 'Sexta')
                })

        return datas

    async def _verificar_lista_espera_para_outras_datas(self, db: Session):
        """Verifica se há pessoas na lista de espera para notificar"""
        # Implementação futura
        pass 