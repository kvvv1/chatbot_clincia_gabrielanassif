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
from app.utils.context_validator import ContextValidator
from app.services.state_manager import StateManager
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
        self.context_validator = ContextValidator()
        self.state_manager = StateManager()
        
        # Cache em memória para conversas ativas
        self.conversation_cache = {}

    async def processar_mensagem(self, phone: str, message: str,
                                message_id: str, db: Session):
        """Processa mensagem com sistema 100% sólido de gerenciamento de conversas"""
        
        start_time = time.time()
        logger.info(f"=== CONVERSATION MANAGER - INÍCIO ===")
        logger.info(f"Telefone: {phone}")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Message ID: {message_id}")

        try:
            # Analytics: Registrar recebimento da mensagem
            try:
                await self.analytics.track_message_received(phone, message, message_id)
            except Exception as e:
                logger.warning(f"Erro no analytics: {str(e)}")
            
            # NLU: Processar mensagem para entender intenção
            nlu_result = self.nlu.process_message(message)
            logger.info(f"NLU Result: {nlu_result}")

            # Marcar mensagem como lida
            try:
                await self.whatsapp.mark_as_read(phone, message_id)
                logger.info("Mensagem marcada como lida")
            except Exception as e:
                logger.warning(f"Erro ao marcar como lida: {str(e)}")

            # Buscar ou criar conversa com validação robusta
            logger.info("Buscando ou criando conversa...")
            conversa = self._get_or_create_conversation(phone, db)
            logger.info(f"Conversa encontrada/criada: ID {conversa.id}")
            
            # Validar e normalizar estado
            estado = self._ensure_valid_state(conversa, db)
            contexto = conversa.context or {}
            
            logger.info(f"Estado atual: '{estado}'")
            logger.info(f"Contexto: {contexto}")
            logger.info(f"Processando mensagem: '{message}' no estado: {estado}")

            # Verificar se é finalização de conversa
            if self._is_conversation_end_request(message, nlu_result):
                await self._finalize_conversation(phone, conversa, db)
                return

            # Analytics: Registrar início de conversa se for primeira mensagem
            if estado == "inicio":
                try:
                    await self.analytics.track_event(
                        EventType.CONVERSATION_START, 
                        {"initial_message": message}, 
                        phone
                    )
                except Exception as e:
                    logger.warning(f"Erro no analytics: {str(e)}")

            # SOLUÇÃO DEFINITIVA: Validar contexto antes de processar
            try:
                # Validar mensagem para o estado atual
                is_valid, error_message, suggested_action = self.context_validator.validate_message_for_state(
                    message, estado, contexto
                )
                
                if not is_valid:
                    logger.warning(f"Validação de contexto falhou: {error_message}")
                    await self.whatsapp.send_message(phone, error_message)
                    return
                
                # Processar com sistema robusto de estados
                await self._process_message_by_state(phone, message, conversa, db, nlu_result, estado, contexto, suggested_action)
            except Exception as e:
                logger.error(f"Erro durante processamento: {str(e)}")
                await self._handle_processing_error(phone, conversa, db, e, estado, message)

        except Exception as e:
            logger.error(f"Erro crítico no processamento: {str(e)}")
            await self._handle_critical_error(phone, message, message_id, e)

        finally:
            # Analytics: Registrar tempo de resposta
            try:
                response_time = time.time() - start_time
                await self.analytics.track_message_sent(phone, "response_sent", response_time)
            except Exception as e:
                logger.warning(f"Erro no analytics: {str(e)}")
            
            logger.info(f"=== CONVERSATION MANAGER - FIM (Tempo: {time.time() - start_time:.2f}s) ===")

    def _is_conversation_end_request(self, message: str, nlu_result: Dict) -> bool:
        """Verifica se é uma solicitação para finalizar a conversa"""
        message_lower = message.lower().strip()
        end_indicators = ['sair', 'tchau', 'bye', '0', 'encerrar', 'finalizar', 'adeus']
        return message_lower in end_indicators or nlu_result.get('is_farewell', False)

    async def _finalize_conversation(self, phone: str, conversa: Conversation, db: Session):
        """Finaliza a conversa adequadamente"""
        logger.info("=== FINALIZANDO CONVERSA ===")
        
        # Salvar estado final
        conversa.state = "finalizada"
        conversa.context = {"finalizada_em": datetime.utcnow().isoformat()}
        self._save_conversation_state(conversa, db)
        
        # Enviar mensagem de despedida
        await self.whatsapp.send_message(phone, """
👋 *Obrigado por usar nossos serviços!*

Tenha um ótimo dia! 😊

Para iniciar uma nova conversa, digite *oi* ou *1*.
""")
        
        # Limpar cache
        if phone in self.conversation_cache:
            del self.conversation_cache[phone]
        
        logger.info("Conversa finalizada com sucesso")

    async def _process_message_by_state(self, phone: str, message: str, conversa: Conversation, 
                                      db: Session, nlu_result: Dict, estado: str, contexto: Dict, suggested_action: Dict):
        """Processa mensagem baseado no estado atual com validação de contexto"""
        
        logger.info(f"=== PROCESSANDO POR ESTADO: {estado} ===")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Estado atual: '{estado}'")
        logger.info(f"Contexto: {contexto}")
        
        # SOLUÇÃO DEFINITIVA: Processar baseado no estado ATUAL, não na mensagem
        if estado == "inicio":
            await self._handle_inicio_advanced(phone, message, conversa, db, nlu_result)
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
        elif estado == "confirmando_cancelamento":
            await self._handle_confirmar_cancelamento(phone, message, conversa, db)
        elif estado == "lista_espera":
            await self._handle_lista_espera(phone, message, conversa, db)
        elif estado == "escolhendo_tipo_consulta":
            await self._handle_escolha_tipo_consulta(phone, message, conversa, db)

        elif estado == "aguardando_observacoes":
            await self._handle_observacoes(phone, message, conversa, db)
        elif estado == "finalizada":
            # Reativar conversa se necessário
            conversa.state = "inicio"
            self._save_conversation_state(conversa, db)
            await self._handle_inicio_advanced(phone, message, conversa, db, nlu_result)
        else:
            logger.error(f"Estado desconhecido: {estado}")
            await self._reset_to_inicio(phone, conversa, db)

    async def _handle_processing_error(self, phone: str, conversa: Conversation, db: Session, 
                                     error: Exception, estado: str, message: str):
        """Trata erros durante o processamento"""
        logger.error(f"Erro durante processamento: {str(error)}")
        
        try:
            await self.analytics.track_error(phone, "processing_error", str(error), {
                "state": estado,
                "message": message
            })
        except Exception as e:
            logger.warning(f"Erro no analytics: {str(e)}")
        
        # Recuperação de erro
        try:
            error_response, error_context = await self.error_recovery.handle_api_error(
                ErrorType.UNKNOWN_ERROR, 
                {"error": str(error), "state": estado}, 
                phone, 
                estado
            )
            await self.whatsapp.send_message(phone, error_response)
        except Exception as e:
            logger.error(f"Erro na recuperação: {str(e)}")
            await self.whatsapp.send_message(phone, """
⚠️ *Erro no sistema*

Estamos enfrentando dificuldades técnicas no momento.

Digite *1* para voltar ao menu principal ou *0* para sair.
""")
        
        # Se erro persistir, oferecer suporte humano
        if self.error_recovery.should_offer_human_support(phone):
            await self._offer_human_support(phone, conversa, db)

    async def _handle_critical_error(self, phone: str, message: str, message_id: str, error: Exception):
        """Trata erros críticos"""
        logger.error(f"Erro crítico no processamento: {str(error)}")
        
        try:
            await self.analytics.track_error(phone, "critical_error", str(error), {
                "message": message,
                "message_id": message_id
            })
        except Exception as e:
            logger.warning(f"Erro no analytics: {str(e)}")
        
        # Enviar mensagem de erro genérica
        try:
            error_message = """
⚠️ *Erro no sistema*

Estamos enfrentando dificuldades técnicas no momento.

📞 *Atendimento humano:*
Digite *0* para falar com um atendente que pode te ajudar.

🔄 *Tente novamente em alguns minutos*
"""
            await self.whatsapp.send_message(phone, error_message)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {str(e)}")

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
        """Handler avançado do estado inicial com NLU - VERSÃO ROBUSTA"""
        
        logger.info(f"=== _handle_inicio_advanced DEBUG ===")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Estado atual: {conversa.state}")
        logger.info(f"NLU Result: {nlu_result}")
        
        # Verificar se é saudação
        if nlu_result.get("is_greeting") or nlu_result.get("intent") == "saudacao":
            logger.info("→ Saudação detectada")
            await self._handle_inicio(phone, message, conversa, db)
            return
        
        # Verificar intenções específicas
        intent = nlu_result.get("intent", "")
        if intent == "agendar":
            logger.info("→ Intenção direta: agendar")
            await self.whatsapp.send_message(phone, "Vamos agendar sua consulta! 📅\n\nPor favor, digite seu *CPF* (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "agendar"}
            self._save_conversation_state(conversa, db)
            return
            
        elif intent == "visualizar":
            logger.info("→ Intenção direta: visualizar")
            await self.whatsapp.send_message(phone, "Para ver seus agendamentos, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "visualizar"}
            self._save_conversation_state(conversa, db)
            return
            
        elif intent == "cancelar":
            logger.info("→ Intenção direta: cancelar")
            await self.whatsapp.send_message(phone, "Para cancelar uma consulta, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):")
            conversa.state = "aguardando_cpf"
            conversa.context = {"acao": "cancelar"}
            self._save_conversation_state(conversa, db)
            return
            
        elif intent == "ajuda":
            logger.info("→ Intenção direta: ajuda")
            await self.whatsapp.send_message(phone, f"""
💡 *Como posso te ajudar?*

Sou o assistente virtual da {settings.clinic_name} e posso te ajudar com:

📅 *Agendamentos:* Marcar, ver ou cancelar consultas
👥 *Lista de espera:* Entrar na fila quando não há vagas
📞 *Atendimento:* Falar com um humano quando precisar

{FormatterUtils.formatar_menu_principal()}
""")
            conversa.state = "menu_principal"
            self._save_conversation_state(conversa, db)
            return
        
        # FALLBACK: Mostrar menu principal
        logger.info("→ Fallback: Mostrando menu principal")
        await self._handle_inicio(phone, message, conversa, db)
        
        logger.info("=== FIM _handle_inicio_advanced ===")

    async def _handle_inicio(self, phone: str, message: str,
                           conversa: Conversation, db: Session):
        """Handler do estado inicial"""

        logger.info(f"=== _handle_inicio DEBUG ===")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Estado atual: {conversa.state}")

        # Verificar se é primeira vez ou retorno
        if message.strip().lower() in ['oi', 'olá', 'ola', 'hi', 'hello']:
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
        """Handler do menu principal - VERSÃO ROBUSTA"""

        logger.info(f"=== _handle_menu_principal DEBUG ===")
        logger.info(f"Mensagem: '{message}'")
        logger.info(f"Estado atual: {conversa.state}")
        
        opcao = message.strip()
        logger.info(f"Opção processada: '{opcao}'")
        
        # Garantir que estamos no estado correto
        logger.info(f"Estado antes da correção: {conversa.state}")
        if conversa.state != "menu_principal":
            conversa.state = "menu_principal"
            self._save_conversation_state(conversa, db)
            logger.info("Estado corrigido para menu_principal")
        else:
            logger.info("Estado já estava correto (menu_principal)")

        # VALIDAÇÃO ROBUSTA: Verificar se é realmente uma opção de menu válida
        if opcao == "1":
            logger.info("→ Opção 1 selecionada: Agendar consulta")
            await self.whatsapp.send_text(
                phone,
                "Vamos agendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):"
            )
            self._transition_to_state(conversa, "aguardando_cpf", {"acao": "agendar"}, db)

        elif opcao == "2":
            logger.info("→ Opção 2 selecionada: Ver agendamentos")
            await self.whatsapp.send_text(
                phone,
                "Para ver seus agendamentos, preciso do seu *CPF*.\n\n"
                "Digite seu CPF (apenas números):"
            )
            self._transition_to_state(conversa, "aguardando_cpf", {"acao": "visualizar"}, db)

        elif opcao == "3":
            logger.info("→ Opção 3 selecionada: Cancelar consulta")
            await self.whatsapp.send_text(
                phone,
                "Para cancelar uma consulta, preciso do seu *CPF*.\n\n"
                "Digite seu CPF (apenas números):"
            )
            self._transition_to_state(conversa, "aguardando_cpf", {"acao": "cancelar"}, db)

        elif opcao == "4":
            logger.info("→ Opção 4 selecionada: Lista de espera")
            await self.whatsapp.send_text(
                phone,
                "Vou adicionar você na lista de espera! 📝\n\n"
                "Digite seu *CPF* (apenas números):"
            )
            self._transition_to_state(conversa, "aguardando_cpf", {"acao": "lista_espera"}, db)

        elif opcao == "5":
            logger.info("→ Opção 5 selecionada: Falar com atendente")
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
            self._transition_to_state(conversa, "inicio", {}, db)

        elif opcao.lower() in ['sair', 'tchau', 'bye', '0']:
            logger.info("→ Solicitação de saída detectada")
            await self.whatsapp.send_text(
                phone,
                "Obrigado por usar nossos serviços! 😊\n\n"
                "Tenha um ótimo dia!\n\n"
                "Para voltar, digite *1*."
            )
            self._transition_to_state(conversa, "inicio", {}, db)

        else:
            # VALIDAÇÃO: Verificar se não é um CPF (números longos)
            if len(opcao) >= 10 and opcao.isdigit():
                logger.warning(f"CPF detectado no menu principal: {opcao}")
                await self.whatsapp.send_text(
                    phone,
                    "⚠️ Parece que você digitou um CPF!\n\n"
                    "Para agendar uma consulta, primeiro selecione uma opção:\n\n"
                    "1️⃣ *Agendar consulta*\n"
                    "2️⃣ *Ver meus agendamentos*\n"
                    "3️⃣ *Cancelar consulta*\n"
                    "4️⃣ *Lista de espera*\n"
                    "5️⃣ *Falar com atendente*\n\n"
                    "Digite o número da opção desejada."
                )
            else:
                logger.info(f"Opção inválida: {opcao}")
                await self.whatsapp.send_text(
                    phone,
                    "Opção inválida! 😅\n\n"
                    "Por favor, digite um número de *1 a 5*.\n\n"
                    "Ou digite *0* para sair."
                )

        logger.info(f"Estado final: {conversa.state}")
        logger.info(f"Contexto final: {conversa.context}")
        logger.info("=== FIM _handle_menu_principal DEBUG ===")

    async def _handle_cpf(self, phone: str, message: str,
                         conversa: Conversation, db: Session):
        """Handler para validação de CPF - VERSÃO ROBUSTA"""
        
        logger.info(f"=== _handle_cpf DEBUG ===")
        logger.info(f"CPF recebido: '{message}'")
        logger.info(f"Estado atual: {conversa.state}")
        logger.info(f"Contexto atual: {conversa.context}")

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
                "Exemplo: 12345678901\n\n"
                "Ou digite *0* para voltar ao menu principal."
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
            self._save_conversation_state(conversa, db)
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
        logger.info(f"Contexto final após _handle_cpf: {conversa.context}")
        self._save_conversation_state(conversa, db)
        logger.info("=== FIM _handle_cpf DEBUG ===")

    async def _iniciar_agendamento(self, phone: str, paciente: Dict,
                                  conversa: Conversation, db: Session):
        """Inicia processo de agendamento"""

        nome = paciente.get('nome', 'Paciente')

        # Mostrar tipos de consulta disponíveis
        mensagem = f"""
Olá, *{nome}*! 😊

Vamos agendar sua consulta com a *Dra. Gabriela Nassif*.

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
            contexto['profissional'] = "Dra. Gabriela Nassif"  # Única profissional
            conversa.context = contexto

            # Mostrar confirmação do profissional (único disponível)
            mensagem = f"""
✅ Tipo selecionado: *{tipo_escolhido}*

👩‍⚕️ *Profissional:* Dra. Gabriela Nassif (Clínico Geral)

Agora vamos escolher a data da consulta.
            """

            await self.whatsapp.send_text(phone, mensagem)
            
            # Ir direto para escolha de data (pular escolha de profissional)
            await self._handle_escolha_profissional(phone, "1", conversa, db)

        else:
            await self.whatsapp.send_text(
                phone,
                "❌ Opção inválida!\n\n"
                "Por favor, digite um número de *1 a 5*."
            )

        db.commit()

    async def _handle_escolha_profissional(self, phone: str, message: str,
                                          conversa: Conversation, db: Session):
        """Handler para escolha do profissional (agora apenas confirma Dra. Gabriela)"""

        # Como só há uma profissional, sempre confirmar Dra. Gabriela
        profissional_escolhido = "Dra. Gabriela Nassif"
        
        # Salvar profissional no contexto
        contexto = conversa.context
        contexto['profissional'] = profissional_escolhido
        conversa.context = contexto

        # Gerar opções de datas (próximos 7 dias úteis)
        datas_disponiveis = self._gerar_datas_disponiveis()

        mensagem = f"""
✅ Profissional: *{profissional_escolhido}*

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

    def _save_conversation_state(self, conversa: Conversation, db: Session) -> bool:
        """Salva o estado da conversa de forma robusta"""
        try:
            db.commit()
            logger.info(f"Estado salvo com sucesso: {conversa.state}")
            
            # Atualizar cache
            self.conversation_cache[conversa.phone] = conversa
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {str(e)}")
            # Tentar salvar no cache como fallback
            self.conversation_cache[conversa.phone] = conversa
            logger.info("Estado salvo no cache como fallback")
            return False

    def _transition_to_state(self, conversa: Conversation, new_state: str, context_updates: Dict = None, db: Session = None) -> bool:
        """Transição segura para um novo estado com validação"""
        logger.info(f"=== TRANSIÇÃO DE ESTADO ===")
        logger.info(f"Estado atual: {conversa.state}")
        logger.info(f"Novo estado: {new_state}")
        logger.info(f"Contexto atual: {conversa.context}")
        
        # Validar transição
        is_valid, error_message, suggestions = self.state_manager.validate_state_transition(
            conversa.state, new_state, conversa.context or {}
        )
        
        if not is_valid:
            logger.error(f"Transição inválida: {error_message}")
            return False
        
        # Atualizar contexto se fornecido
        if context_updates:
            current_context = conversa.context or {}
            current_context.update(context_updates)
            conversa.context = current_context
            logger.info(f"Contexto atualizado: {conversa.context}")
        
        # Fazer transição
        old_state = conversa.state
        conversa.state = new_state
        
        # Salvar no banco se disponível
        if db:
            self._save_conversation_state(conversa, db)
        
        logger.info(f"Transição realizada: {old_state} → {new_state}")
        return True

    def _ensure_valid_state(self, conversa: Conversation, db: Session) -> str:
        """Garante que o estado da conversa seja válido"""
        if not conversa.state:
            conversa.state = "inicio"
            logger.warning("Estado None detectado - corrigindo para 'inicio'")
        elif conversa.state.strip() == "":
            conversa.state = "inicio"
            logger.warning("Estado vazio detectado - corrigindo para 'inicio'")
        else:
            # Normalizar estado
            conversa.state = conversa.state.strip().lower()
        
        # Salvar estado corrigido
        self._save_conversation_state(conversa, db)
        return conversa.state

    def _get_or_create_conversation(self, phone: str, db: Session) -> Conversation:
        """Busca ou cria uma conversa - VERSÃO ROBUSTA"""
        logger.info(f"=== _get_or_create_conversation DEBUG ===")
        logger.info(f"Telefone: {phone}")
        logger.info(f"DB type: {type(db)}")
        logger.info(f"DB has query: {hasattr(db, 'query')}")
        
        try:
            # Verificar se o db tem o método query
            if not hasattr(db, 'query'):
                logger.warning("Database não tem método query - usando cache")
                # Usar cache se disponível
                if phone in self.conversation_cache:
                    logger.info("Usando conversa do cache")
                    return self.conversation_cache[phone]
                
                # Criar nova conversa
                conversa = Conversation(phone=phone)
                self.conversation_cache[phone] = conversa
                logger.info(f"Conversa criada no cache - Estado: {conversa.state}")
                return conversa
            
            # Tentar usar filter_by primeiro
            if hasattr(db.query(Conversation), 'filter_by'):
                conversa = db.query(Conversation).filter_by(phone=phone).first()
                logger.info(f"Usando filter_by - Conversa encontrada: {conversa is not None}")
            else:
                # Fallback para filter se filter_by não estiver disponível
                logger.warning("filter_by não disponível - usando filter")
                conversa = db.query(Conversation).filter(Conversation.phone == phone).first()
                logger.info(f"Usando filter - Conversa encontrada: {conversa is not None}")

            if not conversa:
                logger.info("Conversa não encontrada - criando nova")
                conversa = Conversation(phone=phone)
                if hasattr(db, 'add'):
                    db.add(conversa)
                    if hasattr(db, 'commit'):
                        try:
                            db.commit()
                            logger.info("Nova conversa salva no banco")
                        except Exception as e:
                            logger.error(f"Erro ao salvar no banco: {str(e)}")
                            # Salvar no cache como fallback
                            self.conversation_cache[phone] = conversa
                            logger.info("Conversa salva no cache como fallback")
            else:
                logger.info(f"Conversa existente encontrada - Estado: {conversa.state}")
                # Atualizar cache
                self.conversation_cache[phone] = conversa

            return conversa
            
        except Exception as e:
            logger.error(f"Erro ao buscar/criar conversa: {str(e)}")
            # Usar cache se disponível
            if phone in self.conversation_cache:
                logger.info("Usando conversa do cache após erro")
                return self.conversation_cache[phone]
            
            # Criar conversa mock em caso de erro
            conversa = Conversation(phone=phone)
            self.conversation_cache[phone] = conversa
            logger.info("Conversa mock criada após erro")
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