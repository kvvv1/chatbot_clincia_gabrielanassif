from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Conversation, Appointment, WaitingList, get_db
from app.services.whatsapp import WhatsAppService
from app.services.gestaods import GestaoDS
from app.utils.validators import ValidatorUtils
from app.utils.formatters import FormatterUtils
from app.utils.nlu_processor import NLUProcessor
from app.utils.error_recovery import ErrorRecoveryManager, ErrorType
from app.utils.cache_manager import CacheManager, CacheType
from app.utils.analytics import AnalyticsManager, EventType
from app.config import settings
import logging
import re
import time

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.gestaods = GestaoDS()
        self.validator = ValidatorUtils()
        self.nlu = NLUProcessor()
        self.error_recovery = ErrorRecoveryManager()
        self.cache = CacheManager()
        self.analytics = AnalyticsManager()

    async def processar_mensagem(self, phone: str, message: str,
                                message_id: str, db: Session):
        """Processa mensagem e retorna resposta apropriada com sistemas avançados"""
        
        start_time = time.time()
        logger.info(f"=== CONVERSATION MANAGER - INÍCIO ===")
        logger.info(f"Telefone: {phone}")
        logger.info(f"Mensagem: {message}")
        logger.info(f"Message ID: {message_id}")

        try:
            # Analytics: Registrar recebimento da mensagem
            await self.analytics.track_message_received(phone, message, message_id)
            
            # NLU: Processar mensagem para entender intenção
            nlu_result = self.nlu.process_message(message)
            logger.info(f"NLU Result: {nlu_result}")

            # Marcar mensagem como lida
            logger.info("Marcando mensagem como lida...")
            await self.whatsapp.mark_as_read(phone, message_id)
            logger.info("Mensagem marcada como lida")

            # Buscar ou criar conversa
            logger.info("Buscando ou criando conversa...")
            conversa = self._get_or_create_conversation(phone, db)
            logger.info(f"Conversa encontrada/criada: ID {conversa.id}")

            # Processar baseado no estado atual
            estado = conversa.state
            contexto = conversa.context or {}

            logger.info(f"Estado atual: {estado}")
            logger.info(f"Contexto: {contexto}")
            logger.info(f"Processando mensagem: '{message}' no estado: {estado}")

            # Analytics: Registrar início de conversa se for primeira mensagem
            if estado == "inicio":
                await self.analytics.track_event(
                    EventType.CONVERSATION_START, 
                    {"initial_message": message}, 
                    phone
                )

            # Processar com recuperação de erros inteligente
            try:
                # Máquina de estados completa com NLU
                if estado == "inicio":
                    logger.info("Executando handler de início...")
                    await self._handle_inicio_advanced(phone, message, conversa, db, nlu_result)

                elif estado == "menu_principal":
                    logger.info("Executando handler do menu principal...")
                    await self._handle_menu_principal(phone, message, conversa, db)

                elif estado == "aguardando_cpf":
                    logger.info("Executando handler de CPF...")
                    logger.info(f"Mensagem recebida no estado aguardando_cpf: {message}")
                    logger.info(f"Chamando _handle_cpf com estado atual: {conversa.state}")
                    await self._handle_cpf(phone, message, conversa, db)
                    logger.info(f"Estado após _handle_cpf: {conversa.state}")
                    logger.info(f"Contexto após _handle_cpf: {conversa.context}")

                elif estado == "escolhendo_data":
                    logger.info("Executando handler de escolha de data...")
                    await self._handle_escolha_data(phone, message, conversa, db)

                elif estado == "escolhendo_horario":
                    logger.info("Executando handler de escolha de horário...")
                    await self._handle_escolha_horario(phone, message, conversa, db)

                elif estado == "confirmando_agendamento":
                    logger.info("Executando handler de confirmação...")
                    await self._handle_confirmacao(phone, message, conversa, db)

                elif estado == "visualizando_agendamentos":
                    logger.info("Executando handler de visualização de agendamentos...")
                    await self._handle_visualizar_agendamentos(phone, message, conversa, db)

                elif estado == "cancelando_consulta":
                    logger.info("Executando handler de cancelamento...")
                    await self._handle_cancelamento(phone, message, conversa, db)

                elif estado == "confirmando_cancelamento":
                    logger.info("Executando handler de confirmação de cancelamento...")
                    await self._handle_confirmar_cancelamento(phone, message, conversa, db)

                elif estado == "lista_espera":
                    logger.info("Executando handler de lista de espera...")
                    await self._handle_lista_espera(phone, message, conversa, db)

                elif estado == "escolhendo_tipo_consulta":
                    logger.info("Executando handler de escolha de tipo de consulta...")
                    await self._handle_escolha_tipo_consulta(phone, message, conversa, db)

                elif estado == "escolhendo_profissional":
                    logger.info("Executando handler de escolha de profissional...")
                    await self._handle_escolha_profissional(phone, message, conversa, db)

                elif estado == "aguardando_observacoes":
                    logger.info("Executando handler de observações...")
                    await self._handle_observacoes(phone, message, conversa, db)

                else:
                    # Estado desconhecido - resetar para início
                    logger.warning(f"Estado desconhecido: {estado}. Resetando para início.")
                    await self._reset_to_inicio(phone, conversa, db)

            except Exception as e:
                logger.error(f"Erro durante processamento: {str(e)}")
                
                # Analytics: Registrar erro
                await self.analytics.track_error(phone, "processing_error", str(e), {
                    "state": estado,
                    "message": message
                })
                
                # Recuperação de erro
                error_response, error_context = await self.error_recovery.handle_api_error(
                    ErrorType.UNKNOWN_ERROR, 
                    {"error": str(e), "state": estado}, 
                    phone, 
                    estado
                )
                
                await self.whatsapp.send_message(phone, error_response)
                
                # Se erro persistir, oferecer suporte humano
                if self.error_recovery.should_offer_human_support(phone):
                    await self._offer_human_support(phone, conversa, db)

        except Exception as e:
            logger.error(f"Erro crítico no processamento: {str(e)}")
            
            # Analytics: Registrar erro crítico
            await self.analytics.track_error(phone, "critical_error", str(e), {
                "message": message,
                "message_id": message_id
            })
            
            # Enviar mensagem de erro genérica
            error_message = """
⚠️ *Erro no sistema*

Estamos enfrentando dificuldades técnicas no momento.

📞 *Atendimento humano:*
Digite *0* para falar com um atendente que pode te ajudar.

🔄 *Tente novamente em alguns minutos*
"""
            await self.whatsapp.send_message(phone, error_message)

        finally:
            # Analytics: Registrar tempo de resposta
            response_time = time.time() - start_time
            await self.analytics.track_message_sent(phone, "response_sent", response_time)
            
            logger.info(f"=== CONVERSATION MANAGER - FIM (Tempo: {response_time:.2f}s) ===")

    async def _reset_to_inicio(self, phone: str, conversa: Conversation, db: Session):
        """Reseta conversa para o estado inicial"""
        conversa.state = "inicio"
        conversa.context = {}
        db.commit()
        
        # Executar as funções de formatação
        saudacao = FormatterUtils.formatar_saudacao()
        menu_principal = FormatterUtils.formatar_menu_principal()
        
        await self.whatsapp.send_message(phone, f"""
🔄 *Conversa reiniciada*

Vamos começar novamente! 

{saudacao}

{menu_principal}
""")

    async def _offer_human_support(self, phone: str, conversa: Conversation, db: Session):
        """Oferece suporte humano"""
        await self.whatsapp.send_message(phone, """
📞 *Atendimento Humano*

Identificamos que você pode precisar de ajuda especializada.

🔄 *Transferindo para um atendente...*

⏳ *Tempo de espera estimado:* 2-5 minutos

Enquanto isso, você pode:
• Aguardar a conexão
• Tentar novamente em alguns minutos
• Verificar sua conexão com a internet

Obrigado pela paciência! 🙏
""")
        
        # Aqui você pode integrar com sistema de tickets ou fila de atendimento
        await self.analytics.track_user_action(phone, "human_support_requested")

    async def _handle_inicio_advanced(self, phone: str, message: str, conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler avançado do estado inicial com NLU"""
        
        # Analytics: Registrar ação do usuário
        await self.analytics.track_user_action(phone, "initial_message", {
            "intent": nlu_result.get("intent"),
            "confidence": nlu_result.get("confidence")
        })
        
        # Verificar se é saudação ou intenção direta
        if nlu_result.get("is_greeting") or nlu_result.get("intent") == "saudacao":
            await self._handle_inicio(phone, message, conversa, db)
        elif nlu_result.get("intent") == "agendar":
            # Usuário quer agendar diretamente
            await self.whatsapp.send_message(phone, "Vamos agendar sua consulta! 📅\n\nPor favor, digite seu *CPF* (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "agendar"}
            db.commit()
        elif nlu_result.get("intent") == "visualizar":
            # Usuário quer ver agendamentos
            await self.whatsapp.send_message(phone, "Para ver seus agendamentos, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "visualizar"}
            db.commit()
        elif nlu_result.get("intent") == "cancelar":
            # Usuário quer cancelar
            await self.whatsapp.send_message(phone, "Para cancelar uma consulta, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "cancelar"}
            db.commit()
        elif nlu_result.get("intent") == "ajuda":
            # Usuário pede ajuda
            await self.whatsapp.send_message(phone, f"""
💡 *Como posso te ajudar?*

Sou o assistente virtual da {settings.clinic_name} e posso te ajudar com:

📅 *Agendamentos:* Marcar, ver ou cancelar consultas
👥 *Lista de espera:* Entrar na fila quando não há vagas
📞 *Atendimento:* Falar com um humano quando precisar

{FormatterUtils.formatar_menu_principal()}
""")
            conversa.state = "menu_principal"
            db.commit()
        else:
            # Se não for uma intenção específica, verificar se é um número (opção do menu)
            opcao = message.strip()
            if opcao in ['1', '2', '3', '4', '5']:
                # Tratar como opção do menu
                await self._handle_menu_principal(phone, message, conversa, db)
            else:
                # Fallback para o handler original
                await self._handle_inicio(phone, message, conversa, db)

    async def _handle_inicio(self, phone: str, message: str,
                           conversa: Conversation, db: Session):
        """Handler do estado inicial"""

        # Verificar se é primeira vez ou retorno
        if message.strip().lower() in ['oi', 'olá', 'ola', 'hi', 'hello', '1']:
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
        else:
            # Se não for uma saudação, tratar como opção do menu
            await self._handle_menu_principal(phone, message, conversa, db)

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
                "📅 Sábado: 8h às 12h\n\n"
                "📞 (31) 9999-9999\n"
                "📧 contato@clinicagabrielanassif.com.br\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"

        elif opcao.lower() in ['sair', 'tchau', 'bye', '0']:
            await self.whatsapp.send_text(
                phone,
                "Obrigado por usar nossos serviços! 😊\n\n"
                "Tenha um ótimo dia!\n\n"
                "Para voltar, digite *1*."
            )
            conversa.state = "inicio"

        else:
            await self.whatsapp.send_text(
                phone,
                "Opção inválida! 😅\n\n"
                "Por favor, digite um número de *1 a 5*.\n\n"
                "Ou digite *0* para sair."
            )

        db.commit()

    async def _handle_cpf(self, phone: str, message: str,
                         conversa: Conversation, db: Session):
        """Handler para validação de CPF"""
        
        logger.info(f"_handle_cpf iniciado - CPF recebido: {message}")

        # Limpar CPF
        cpf = re.sub(r'[^0-9]', '', message)
        logger.info(f"CPF limpo: {cpf}")

        # Validar CPF
        if not self.validator.validar_cpf(cpf):
            logger.info("CPF inválido detectado")
            await self.whatsapp.send_text(
                phone,
                "❌ CPF inválido!\n\n"
                "Por favor, digite um CPF válido (apenas números):\n\n"
                "Exemplo: 12345678901"
            )
            return

        # Buscar paciente na API
        logger.info("Buscando paciente na API...")
        paciente = await self.gestaods.buscar_paciente_cpf(cpf)
        logger.info(f"Paciente encontrado: {paciente is not None}")

        if not paciente:
            logger.info("Paciente não encontrado na API")
            await self.whatsapp.send_text(
                phone,
                "❌ CPF não encontrado em nosso sistema.\n\n"
                "Por favor, verifique o número e tente novamente.\n\n"
                "Se você é um novo paciente, entre em contato "
                "pelo telefone para realizar seu cadastro.\n\n"
                "📞 (31) 9999-9999\n"
                "📧 contato@clinicagabrielanassif.com.br\n\n"
                "Digite *1* para voltar ao menu principal."
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
        logger.info(f"Ação a ser executada: {acao}")

        if acao == "agendar":
            logger.info("Executando _iniciar_agendamento")
            await self._iniciar_agendamento(phone, paciente, conversa, db)
        elif acao == "visualizar":
            logger.info("Executando _mostrar_agendamentos")
            await self._mostrar_agendamentos(phone, paciente, conversa, db)
        elif acao == "cancelar":
            logger.info("Executando _iniciar_cancelamento")
            await self._iniciar_cancelamento(phone, paciente, conversa, db)
        elif acao == "lista_espera":
            logger.info("Executando _adicionar_lista_espera")
            await self._adicionar_lista_espera(phone, paciente, conversa, db)

        logger.info(f"Estado final após _handle_cpf: {conversa.state}")
        db.commit()

    async def _iniciar_agendamento(self, phone: str, paciente: Dict,
                                  conversa: Conversation, db: Session):
        """Inicia processo de agendamento"""

        nome = paciente.get('nome', 'Paciente')

        # Mostrar tipos de consulta disponíveis
        mensagem = f"""
Olá, *{nome}*! 😊

Vamos agendar sua consulta.

🏥 *Tipos de consulta disponíveis:*

*1* - Consulta médica geral
*2* - Consulta especializada
*3* - Exame de rotina
*4* - Retorno médico
*5* - Avaliação inicial

Digite o número do tipo de consulta desejada:
        """

        await self.whatsapp.send_text(phone, mensagem)
        conversa.state = "escolhendo_tipo_consulta"

    async def _handle_escolha_tipo_consulta(self, phone: str, message: str,
                                           conversa: Conversation, db: Session):
        """Handler para escolha do tipo de consulta"""

        opcao = message.strip()
        tipos_consulta = {
            "1": "Consulta médica geral",
            "2": "Consulta especializada", 
            "3": "Exame de rotina",
            "4": "Retorno médico",
            "5": "Avaliação inicial"
        }

        if opcao in tipos_consulta:
            tipo_escolhido = tipos_consulta[opcao]
            
            # Salvar tipo no contexto
            contexto = conversa.context
            contexto['tipo_consulta'] = tipo_escolhido
            conversa.context = contexto

            # Mostrar profissionais disponíveis
            mensagem = f"""
✅ Tipo selecionado: *{tipo_escolhido}*

👨‍⚕️ *Profissionais disponíveis:*

*1* - Dr(a). Gabriela Nassif (Clínico Geral)
*2* - Dr(a). Maria Silva (Cardiologia)
*3* - Dr(a). João Santos (Dermatologia)
*4* - Dr(a). Ana Costa (Ginecologia)
*5* - Dr(a). Pedro Oliveira (Ortopedia)

Digite o número do profissional desejado:
            """

            await self.whatsapp.send_text(phone, mensagem)
            conversa.state = "escolhendo_profissional"

        else:
            await self.whatsapp.send_text(
                phone,
                "❌ Opção inválida!\n\n"
                "Por favor, digite um número de *1 a 5*."
            )

        db.commit()

    async def _handle_escolha_profissional(self, phone: str, message: str,
                                          conversa: Conversation, db: Session):
        """Handler para escolha do profissional"""

        opcao = message.strip()
        profissionais = {
            "1": "Dr(a). Gabriela Nassif",
            "2": "Dr(a). Maria Silva",
            "3": "Dr(a). João Santos", 
            "4": "Dr(a). Ana Costa",
            "5": "Dr(a). Pedro Oliveira"
        }

        if opcao in profissionais:
            profissional_escolhido = profissionais[opcao]
            
            # Salvar profissional no contexto
            contexto = conversa.context
            contexto['profissional'] = profissional_escolhido
            conversa.context = contexto

            # Gerar opções de datas (próximos 7 dias úteis)
            datas_disponiveis = self._gerar_datas_disponiveis()

            mensagem = f"""
✅ Profissional selecionado: *{profissional_escolhido}*

📅 *Escolha uma data:*
            """

            # Adicionar opções de data
            for i, data in enumerate(datas_disponiveis, 1):
                mensagem += f"\n*{i}* - {data['formatado']}"

            mensagem += "\n\nDigite o número da data desejada:"

            await self.whatsapp.send_text(phone, mensagem)

            # Salvar datas no contexto
            contexto['datas_disponiveis'] = datas_disponiveis
            conversa.context = contexto
            conversa.state = "escolhendo_data"

        else:
            await self.whatsapp.send_text(
                phone,
                "❌ Opção inválida!\n\n"
                "Por favor, digite um número de *1 a 5*."
            )

        db.commit()

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
                data_formatada = self.gestaods.formatar_data(data_escolhida['data'])
                
                horarios = await self.gestaods.buscar_horarios_disponiveis(data_formatada)

                if not horarios:
                    await self.whatsapp.send_text(
                        phone,
                        "😔 Não há horários disponíveis para esta data.\n\n"
                        "Por favor, escolha outra data:\n\n"
                        "Digite *0* para voltar e escolher outra data."
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
                    "Por favor, escolha um número válido.\n\n"
                    "Digite *0* para voltar."
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
                tipo = contexto.get('tipo_consulta', 'Consulta')
                profissional = contexto.get('profissional', 'Dr(a). Gabriela Nassif')

                mensagem = f"""
✅ *Confirmar agendamento:*

👤 Paciente: *{paciente.get('nome')}*
🏥 Tipo: *{tipo}*
👨‍⚕️ Profissional: *{profissional}*
📅 Data: *{data.get('formatado')}*
⏰ Horário: *{horario_escolhido.get('hora')}*

*Confirma o agendamento?*

*1* - ✅ Sim, confirmar
*2* - ❌ Não, cancelar
*3* - 📝 Adicionar observações
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
            tipo = contexto.get('tipo_consulta', 'Consulta')
            profissional = contexto.get('profissional', 'Dr(a). Gabriela Nassif')

            # Construir data/hora completa
            data_hora_str = f"{data['data']} {horario['hora']}"
            data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")

            # Criar agendamento na API
            data_agendamento = self.gestaods.formatar_data_hora(f"{data['data']} {horario['hora']}:00")
            data_fim_agendamento = self.gestaods.formatar_data_hora(f"{data['data']} {horario['hora']}:30")  # 30 min de consulta
            
            agendamento = await self.gestaods.criar_agendamento(
                cpf=paciente['cpf'],
                data_agendamento=data_agendamento,
                data_fim_agendamento=data_fim_agendamento,
                primeiro_atendimento=True
            )

            if agendamento:
                # Salvar no banco local para lembretes
                novo_agendamento = Appointment(
                    patient_id=str(paciente['id']),
                    patient_name=paciente['nome'],
                    patient_phone=phone,
                    appointment_date=data_hora,
                    appointment_type=tipo,
                    status="scheduled"
                )
                db.add(novo_agendamento)
                db.commit()

                # Enviar confirmação
                mensagem = FormatterUtils.formatar_mensagem_agendamento(
                    paciente, data_hora, horario['hora'], profissional
                )

                await self.whatsapp.send_text(phone, mensagem)

                # Verificar se há alguém na lista de espera para notificar
                await self._verificar_lista_espera_para_outras_datas(db)

            else:
                await self.whatsapp.send_text(
                    phone,
                    "❌ Erro ao agendar consulta.\n\n"
                    "Por favor, tente novamente ou entre em contato:\n"
                    "📞 (31) 9999-9999"
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

        elif opcao == "3":
            await self.whatsapp.send_text(
                phone,
                "📝 Digite suas observações ou sintomas:\n\n"
                "Exemplo: Dor de cabeça há 3 dias, febre, etc.\n\n"
                "Ou digite *pular* para não adicionar observações."
            )
            conversa.state = "aguardando_observacoes"

        else:
            await self.whatsapp.send_text(
                phone,
                "Por favor, digite:\n"
                "*1* para confirmar\n"
                "*2* para cancelar\n"
                "*3* para adicionar observações"
            )

        db.commit()

    async def _handle_observacoes(self, phone: str, message: str,
                                 conversa: Conversation, db: Session):
        """Handler para observações do paciente"""

        if message.strip().lower() == 'pular':
            # Pular observações e confirmar
            await self._handle_confirmacao(phone, "1", conversa, db)
        else:
            # Salvar observações e confirmar
            contexto = conversa.context
            contexto['observacoes'] = message.strip()
            conversa.context = contexto
            
            await self._handle_confirmacao(phone, "1", conversa, db)

    async def _mostrar_agendamentos(self, phone: str, paciente: Dict,
                                   conversa: Conversation, db: Session):
        """Mostra agendamentos do paciente"""

        # Buscar agendamentos do paciente usando período
        agendamentos = await self.gestaods.listar_agendamentos_periodo(
            data_inicial=(datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"),
            data_final=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")
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
            mensagem += "\n\n*Opções:*\n"
            mensagem += "*1* - Agendar nova consulta\n"
            mensagem += "*2* - Cancelar consulta\n"
            mensagem += "*3* - Reagendar consulta\n"
            mensagem += "*0* - Voltar ao menu"

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
        elif opcao == "2":
            conversa.context = {"acao": "cancelar"}
            conversa.state = "aguardando_cpf"
            await self.whatsapp.send_text(
                phone,
                "Vamos cancelar sua consulta! ❌\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
        elif opcao == "3":
            conversa.context = {"acao": "reagendar"}
            conversa.state = "aguardando_cpf"
            await self.whatsapp.send_text(
                phone,
                "Vamos reagendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
        else:
            await self.whatsapp.send_text(
                phone,
                "Opção inválida! Digite:\n"
                "*0* para voltar ao menu\n"
                "*1* para agendar\n"
                "*2* para cancelar\n"
                "*3* para reagendar"
            )

        db.commit()

    async def _iniciar_cancelamento(self, phone: str, paciente: Dict,
                                   conversa: Conversation, db: Session):
        """Inicia processo de cancelamento"""
        
        # Buscar agendamentos do paciente usando período
        agendamentos = await self.gestaods.listar_agendamentos_periodo(
            data_inicial=(datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"),
            data_final=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")
        )

        if not agendamentos:
            await self.whatsapp.send_text(
                phone,
                "📅 Você não possui agendamentos para cancelar.\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"
            conversa.context = {}
        else:
            # Mostrar agendamentos para cancelamento
            mensagem = "❌ *Selecione o agendamento para cancelar:*\n\n"
            
            for i, ag in enumerate(agendamentos[:5], 1):
                data = datetime.fromisoformat(ag['data_hora'])
                mensagem += (
                    f"*{i}* - {FormatterUtils.formatar_data_brasil(data)} "
                    f"às {FormatterUtils.formatar_hora_brasil(data)}\n"
                )
            
            mensagem += "\nDigite o número do agendamento ou *0* para voltar:"
            
            await self.whatsapp.send_text(phone, mensagem)
            
            # Salvar agendamentos no contexto
            contexto = conversa.context
            contexto['agendamentos_cancelar'] = agendamentos
            conversa.context = contexto
            conversa.state = "cancelando_consulta"

        db.commit()

    async def _handle_cancelamento(self, phone: str, message: str,
                                  conversa: Conversation, db: Session):
        """Handler para cancelamento de consulta"""

        try:
            opcao = int(message.strip())
            
            if opcao == 0:
                await self._handle_inicio(phone, message, conversa, db)
                return
                
            contexto = conversa.context
            agendamentos = contexto.get('agendamentos_cancelar', [])
            
            if 1 <= opcao <= len(agendamentos):
                agendamento = agendamentos[opcao - 1]
                contexto['agendamento_cancelar'] = agendamento
                
                data = datetime.fromisoformat(agendamento['data_hora'])
                
                mensagem = f"""
❌ *Confirmar cancelamento:*

📅 Data: {FormatterUtils.formatar_data_brasil(data)}
⏰ Horário: {FormatterUtils.formatar_hora_brasil(data)}
👨‍⚕️ Profissional: {agendamento.get('profissional', 'Dr(a). Gabriela Nassif')}

*Tem certeza que deseja cancelar?*

*1* - ✅ Sim, cancelar
*2* - ❌ Não, manter agendamento
                """
                
                await self.whatsapp.send_text(phone, mensagem)
                conversa.context = contexto
                conversa.state = "confirmando_cancelamento"
                
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

    async def _handle_confirmar_cancelamento(self, phone: str, message: str,
                                            conversa: Conversation, db: Session):
        """Handler para confirmação de cancelamento"""

        opcao = message.strip()

        if opcao == "1":
            contexto = conversa.context
            agendamento = contexto.get('agendamento_cancelar', {})
            
            # Cancelar na API - usando reagendamento com data passada para cancelar
            data_atual = datetime.now()
            data_passada = (data_atual - timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S")
            
            sucesso = await self.gestaods.reagendar_agendamento(
                agendamento_id=agendamento['id'],
                data_agendamento=data_passada,
                data_fim_agendamento=data_passada
            )
            
            if sucesso:
                await self.whatsapp.send_text(
                    phone,
                    "✅ *Agendamento cancelado com sucesso!*\n\n"
                    "Se precisar reagendar, entre em contato conosco.\n\n"
                    "Digite *1* para voltar ao menu principal."
                )
            else:
                await self.whatsapp.send_text(
                    phone,
                    "❌ Erro ao cancelar agendamento.\n\n"
                    "Por favor, entre em contato:\n"
                    "📞 (31) 9999-9999"
                )
            
            conversa.state = "inicio"
            conversa.context = {}
            
        elif opcao == "2":
            await self.whatsapp.send_text(
                phone,
                "✅ Agendamento mantido!\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"
            conversa.context = {}
            
        else:
            await self.whatsapp.send_text(
                phone,
                "Por favor, digite:\n"
                "*1* para confirmar cancelamento\n"
                "*2* para manter agendamento"
            )

        db.commit()

    async def _adicionar_lista_espera(self, phone: str, paciente: Dict,
                                     conversa: Conversation, db: Session):
        """Adiciona paciente à lista de espera"""
        
        # Verificar se já está na lista
        lista_existente = db.query(WaitingList).filter_by(
            patient_id=str(paciente['id'])
        ).first()
        
        if lista_existente:
            await self.whatsapp.send_text(
                phone,
                "📝 Você já está na lista de espera!\n\n"
                "Assim que houver uma vaga, entraremos em contato.\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"
            conversa.context = {}
        else:
            # Adicionar à lista de espera
            nova_entrada = WaitingList(
                patient_id=str(paciente['id']),
                patient_name=paciente['nome'],
                patient_phone=phone,
                priority=0,
                notified=False
            )
            db.add(nova_entrada)
            db.commit()
            
            await self.whatsapp.send_text(
                phone,
                "✅ *Adicionado à lista de espera com sucesso!*\n\n"
                "Assim que houver uma vaga disponível, "
                "entraremos em contato com você.\n\n"
                "Digite *1* para voltar ao menu principal."
            )
            conversa.state = "inicio"
            conversa.context = {}

    async def _handle_lista_espera(self, phone: str, message: str,
                                  conversa: Conversation, db: Session):
        """Handler para lista de espera"""
        
        opcao = message.strip()
        
        if opcao == "1":
            await self._handle_inicio(phone, message, conversa, db)
        else:
            await self.whatsapp.send_text(
                phone,
                "Opção inválida! Digite *1* para voltar ao menu principal."
            )
        
        db.commit()

    async def _handle_reagendamento(self, phone: str, message: str,
                                   conversa: Conversation, db: Session):
        """Handler para reagendamento"""
        # Implementação similar ao agendamento
        await self.whatsapp.send_text(
            phone,
            "Funcionalidade de reagendamento será implementada em breve."
        )
        conversa.state = "inicio"
        conversa.context = {}

    async def _handle_confirmar_lembrete(self, phone: str, message: str,
                                        conversa: Conversation, db: Session):
        """Handler para confirmação de lembrete"""
        
        opcao = message.strip()
        
        if opcao == "1":
            await self.whatsapp.send_text(
                phone,
                "✅ Presença confirmada!\n\n"
                "Aguardamos você amanhã!\n\n"
                "📍 Clínica Gabriela Nassif\n"
                "Rua Example, 123 - Savassi\n"
                "Belo Horizonte - MG"
            )
        elif opcao == "2":
            await self.whatsapp.send_text(
                phone,
                "❌ Entendido que não poderá comparecer.\n\n"
                "Para reagendar, digite *1* para voltar ao menu principal."
            )
        elif opcao == "3":
            conversa.context = {"acao": "reagendar"}
            conversa.state = "aguardando_cpf"
            await self.whatsapp.send_text(
                phone,
                "Vamos reagendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
        else:
            await self.whatsapp.send_text(
                phone,
                "Por favor, digite:\n"
                "*1* para confirmar presença\n"
                "*2* para não comparecer\n"
                "*3* para reagendar"
            )
        
        conversa.state = "inicio"
        db.commit()

    def _get_or_create_conversation(self, phone: str, db: Session) -> Conversation:
        """Busca ou cria uma conversa"""
        try:
            # Verificar se o db tem o método query
            if not hasattr(db, 'query'):
                logger.warning("Database não tem método query - criando conversa mock")
                conversa = Conversation(phone=phone)
                return conversa
            
            # Tentar usar filter_by primeiro
            if hasattr(db.query(Conversation), 'filter_by'):
                conversa = db.query(Conversation).filter_by(phone=phone).first()
            else:
                # Fallback para filter se filter_by não estiver disponível
                logger.warning("filter_by não disponível - usando filter")
                conversa = db.query(Conversation).filter(Conversation.phone == phone).first()

            if not conversa:
                conversa = Conversation(phone=phone)
                if hasattr(db, 'add'):
                    db.add(conversa)
                    if hasattr(db, 'commit'):
                        db.commit()

            return conversa
            
        except Exception as e:
            logger.error(f"Erro ao buscar/criar conversa: {str(e)}")
            # Criar conversa mock em caso de erro
            conversa = Conversation(phone=phone)
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