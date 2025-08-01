from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Conversation, Appointment, WaitingList, get_db
from app.services.whatsapp import WhatsAppService
from app.services.gestaods import GestaoDS
from app.utils.validators import ValidatorUtils
from app.utils.formatters import FormatterUtils
from app.utils.nlu_processor import NLUProcessor
from app.services.state_manager import StateManager
from app.config import settings
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.gestaods = GestaoDS()
        self.validator = ValidatorUtils()
        self.nlu = NLUProcessor()
        self.state_manager = StateManager()
        self.conversation_cache = {}
        
    async def processar_mensagem(self, phone: str, message: str, message_id: str, db: Session):
        """Processa mensagem com sistema robusto de gerenciamento"""
        try:
            # 🔧 CORREÇÃO: Logs esperados para diagnóstico rápido
            logger.info(f"🎯 ===== INICIANDO PROCESSAMENTO =====")
            logger.info(f"📱 User ID/Telefone: {phone}")
            logger.info(f"💬 Mensagem recebida: '{message}'")
            logger.info(f"🆔 Message ID: {message_id}")
            
            # Marcar como lida
            try:
                await self.whatsapp.mark_as_read(phone, message_id)
            except:
                pass
            
            # Buscar ou criar conversa
            conversa = self._get_or_create_conversation(phone, db)
            estado = conversa.state or "inicio"
            # 🔧 CORREÇÃO: Rastrear último estado para comandos globais
            self._last_state = estado
            contexto = conversa.context or {}
            
            logger.info(f"🔄 Estado ANTES: {estado}")
            logger.info(f"📋 Contexto ANTES: {contexto}")
            
            # Processar NLU
            nlu_result = self.nlu.process_message(message)
            
            # 🔧 CORREÇÃO: Remover validação que bloqueia o fluxo normal
            # Os números 1-5 são válidos em muitos contextos (confirmações, escolhas, etc)
            # A validação de contexto deve ser feita nos handlers individuais
            message_clean = message.strip()
            logger.info(f"🖺 Mensagem limpa: '{message_clean}'")
            
            # Verificar comandos globais
            if self._is_global_command(message):
                logger.info(f"🌐 Comando global detectado: '{message}'")
                await self._handle_global_command(phone, message, conversa, db)
                return
            
            # Processar por estado
            await self._process_by_state(phone, message, conversa, db, nlu_result)
            
            # 🔧 CORREÇÃO: Logs pós-processamento
            db.refresh(conversa)  # Garantir que temos dados atualizados
            estado_depois = conversa.state
            contexto_depois = conversa.context.copy() if conversa.context else {}
            
            logger.info(f"🔄 Estado DEPOIS: {estado_depois}")
            logger.info(f"📋 Contexto DEPOIS: {contexto_depois}")
            
            # 🔧 CORREÇÃO: Log explicando por que mudou
            if estado != estado_depois:
                logger.info(f"🔍 Mudança de estado: {estado} → {estado_depois}")
                logger.info(f"📝 Razão: Processamento da mensagem '{message}' resultou em nova fase")
            
            logger.info(f"🎯 ===== PROCESSAMENTO CONCLUÍDO =====")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento da mensagem: {str(e)}")
            logger.exception("Stack trace completo:")
            
            # Em caso de erro crítico, tentar handle de erro
            try:
                conversa = self._get_or_create_conversation(phone, db)
                await self._handle_error(phone, conversa, db)
            except Exception as error_handling_error:
                logger.error(f"❌ Erro crítico no handling de erro: {str(error_handling_error)}")
                logger.error("Sistema em estado crítico - não enviando mensagem de erro para evitar loops")
    
    def _is_global_command(self, message: str) -> bool:
        """Verifica se é um comando global - VERSÃO SUPER RESTRITIVA"""
        # 🔧 CORREÇÃO RADICAL: Apenas comandos textuais explícitos
        explicit_commands = ['sair', 'menu', 'ajuda', 'cancelar']
        message_clean = message.strip().lower()
        
        # Log para debug
        logger.info(f"🔍 Verificando comando global: '{message_clean}'")
        
        # ✅ CORREÇÃO RADICAL: Remover completamente o "0" dos comandos globais
        # O "0" só funcionará quando explicitamente no handler do menu
        is_global = message_clean in explicit_commands
        
        logger.info(f"   - É comando global? {is_global}")
        logger.info(f"   - Comandos aceitos: {explicit_commands}")
        
        return is_global
    
    def _get_status_message(self, state: str, context: dict) -> str:
        """Retorna mensagem descritiva do estado atual"""
        acao = context.get('acao', '')
        
        status_map = {
            'aguardando_cpf': f"Aguardando seu CPF para {acao or 'continuar'}",
            'confirmando_paciente': "Aguardando confirmação dos seus dados",
            'paciente_nao_encontrado': "Aguardando nova tentativa de CPF ou escolha de opção",
            'escolhendo_data': "Aguardando escolha da data do agendamento",
            'escolhendo_horario': "Aguardando escolha do horário",
            'confirmando_agendamento': "Aguardando confirmação final do agendamento",
            'visualizando_agendamentos': "Mostrando seus agendamentos",
            'lista_espera': "Processando lista de espera",
            'inicio': "Início da conversa",
            'menu_principal': "No menu principal"
        }
        
        return status_map.get(state, f"Estado: {state}")
    
    async def _handle_global_command(self, phone: str, message: str, conversa: Conversation, db: Session):
        """Trata comandos globais"""
        cmd = message.strip().lower()
        
        logger.info(f"🌐 Processando comando global: '{cmd}'")
        logger.info(f"   - Estado atual antes: {conversa.state}")
        
        if cmd in ['sair', '0']:
            # 🔧 CORREÇÃO: Lógica do '0' corrigida
            if cmd == '0' and conversa.state in ['escolhendo_data', 'escolhendo_horario']:
                # Em estados de escolha numérica, '0' pode ser uma opção válida (voltar)
                logger.info(f"   🔙 '0' em estado de escolha, processando como opção válida")
                return
            # Para 'sair' ou '0' no menu principal, sempre finalizar
            await self._finalizar_conversa(phone, conversa, db)
        elif cmd in ['menu', 'ajuda']:
            await self._mostrar_menu_principal(phone, conversa, db)
        elif cmd == 'cancelar':
            await self._cancelar_operacao_atual(phone, conversa, db)
    
    async def _process_by_state(self, phone: str, message: str, conversa: Conversation, 
                               db: Session, nlu_result: Dict):
        """Processa mensagem baseado no estado atual"""
        estado = conversa.state or "inicio"
        # 🔧 CORREÇÃO: Rastrear último estado para comandos globais
        self._last_state = estado
        
        logger.info(f"🎯 PROCESSANDO POR ESTADO")
        logger.info(f"   - Estado detectado: '{estado}'")
        logger.info(f"   - Mensagem: '{message}'")
        
        handlers = {
            "inicio": self._handle_inicio,
            "menu_principal": self._handle_menu_principal,
            "aguardando_cpf": self._handle_cpf,
            "confirmando_paciente": self._handle_confirmacao_paciente,
            "paciente_nao_encontrado": self._handle_paciente_nao_encontrado_opcoes,
            "escolhendo_data": self._handle_escolha_data,
            "escolhendo_horario": self._handle_escolha_horario,
            "confirmando_agendamento": self._handle_confirmacao,
            "visualizando_agendamentos": self._handle_visualizar_agendamentos,
            "lista_espera": self._handle_lista_espera,
            "agendamento_sem_dias": self._handle_agendamento_sem_dias,
            "data_sem_horarios": self._handle_data_sem_horarios,
            "finalizada": self._handle_conversa_finalizada  # 🔧 CORREÇÃO: Estado finalizada
        }
        
        handler = handlers.get(estado, self._handle_estado_desconhecido)
        handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
        logger.info(f"🔧 Handler selecionado: {handler_name}")
        
        # 🔧 CORREÇÃO: Dispatcher resiliente com try/catch
        try:
            await handler(phone, message, conversa, db, nlu_result)
        except Exception as e:
            logger.exception(f"❌ Erro dentro do handler de estado '{estado}': {str(e)}")
            logger.error(f"Handler: {handler_name}, Telefone: {phone}, Mensagem: {message}")
            await self._handle_error(phone, conversa, db)
    
    async def _handle_inicio(self, phone: str, message: str, conversa: Conversation, 
                           db: Session, nlu_result: Dict):
        """Handler do estado inicial"""
        # Enviar saudação e menu
        await self._mostrar_menu_principal(phone, conversa, db)
    
    async def _mostrar_menu_principal(self, phone: str, conversa: Conversation, db: Session):
        """Mostra menu principal"""
        saudacao = FormatterUtils.formatar_saudacao()
        menu = f"""
{saudacao} Bem-vindo(a) à *{settings.clinic_name}*! 🏥

Sou seu assistente virtual. Como posso ajudar?

*Digite o número da opção desejada:*

1️⃣ *Agendar consulta*
2️⃣ *Ver meus agendamentos*
3️⃣ *Cancelar consulta*
4️⃣ *Lista de espera*
5️⃣ *Falar com atendente*

Digite *0* para sair
"""
        await self.whatsapp.send_text(phone, menu)
        
        conversa.state = "menu_principal"
        conversa.context = {"expecting": "menu_option"}  # 🔧 CORREÇÃO: Flag expecting
        
        # 🔧 CORREÇÃO: Persistir estado imediatamente
        db.commit()
        logger.info(f"💾 Estado 'menu_principal' salvo, expecting: menu_option")
    
    async def _handle_menu_principal(self, phone: str, message: str, conversa: Conversation,
                                   db: Session, nlu_result: Dict):
        """Handler do menu principal - Versão normalizada e resiliente"""
        # 🔧 CORREÇÃO: Validar expecting apenas se existir e for diferente de menu_option
        # Não bloquear se expecting não estiver definido (compatibilidade)
        expecting = conversa.context.get("expecting")
        if not self._is_global_command(message) and expecting and expecting not in ["menu_option", None]:
            logger.warning(f"❌ Opção de menu fora de contexto - expecting: {expecting}")
            await self.whatsapp.send_text(phone, "Vou mostrar o menu principal novamente:")
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        opcao = message.strip().lower()
        
        logger.info(f"🎯 MENU PRINCIPAL - Processando opção: '{opcao}'")
        logger.info(f"📱 Telefone: {phone}")
        logger.info(f"🔄 Estado atual: {conversa.state}")
        logger.info(f"📋 Contexto atual: {conversa.context}")
        
        # 🔧 CORREÇÃO: Menu principal unificado com expecting flag
        opcoes = {
            "1": ("agendar", "aguardando_cpf", "Vamos agendar sua consulta! 📅\n\nPor favor, digite seu *CPF* (apenas números):"),
            "2": ("visualizar", "aguardando_cpf", "Para ver seus agendamentos, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):"),
            "3": ("cancelar", "aguardando_cpf", "Para cancelar uma consulta, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):"),
            "4": ("lista_espera", "aguardando_cpf", "Vou adicionar você na lista de espera! 📝\n\nDigite seu *CPF* (apenas números):"),
            "5": ("atendente", "menu_principal", self._mostrar_contato_atendente)
        }
        
        if opcao in opcoes:
            acao, novo_estado, mensagem = opcoes[opcao]
            
            logger.info(f"✅ Opção '{opcao}' encontrada!")
            logger.info(f"   - Ação: {acao}")
            logger.info(f"   - Novo estado: {novo_estado}")
            
            if callable(mensagem):
                await mensagem(phone)
                # Manter estado menu_principal para atendente
                conversa.state = "menu_principal"
                conversa.context = {}
                logger.info(f"🔧 Função chamada - Estado: {conversa.state}")
            else:
                await self.whatsapp.send_text(phone, mensagem)
                conversa.state = novo_estado or "menu_principal"
                # 🔧 CORREÇÃO: Adicionar flag expecting no contexto
                conversa.context = {"acao": acao, "expecting": "cpf"} if acao else {}
                logger.info(f"📝 Mensagem enviada - Estado: {conversa.state}")
                logger.info(f"📋 Contexto atualizado: {conversa.context}")
            
            # 🔧 CORREÇÃO: Persistir estado imediatamente
            db.commit()
            logger.info(f"💾 Estado salvo no banco: {conversa.state}")
        else:
            logger.warning(f"❌ Opção inválida: '{opcao}'")
            logger.warning(f"   - Tipo: {type(opcao)}")
            logger.warning(f"   - Opções válidas: {list(opcoes.keys())}")
            await self.whatsapp.send_text(phone, 
                "❌ Opção inválida! Por favor, digite um número de *1 a 5*.")
            # Manter estado atual após opção inválida
            logger.info(f"🔄 Mantendo estado atual: {conversa.state}")
            db.commit()
    
    async def _handle_cpf(self, phone: str, message: str, conversa: Conversation, 
                         db: Session, nlu_result: Dict):
        """Handler para validação de CPF com fallback robusto"""
        # 🔧 CORREÇÃO: Validar expecting apenas se existir e for claramente errado
        # Não bloquear se expecting não estiver definido (compatibilidade)
        expecting = conversa.context.get("expecting")
        if expecting and expecting not in ["cpf", None] and expecting != "menu_option":
            logger.warning(f"❌ CPF fora de contexto - expecting: {expecting}")
            await self.whatsapp.send_text(phone, "Desculpe, não entendi. Voltando ao menu principal.")
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        cpf = re.sub(r'[^0-9]', '', message)
        
        logger.info(f"🔍 Processando CPF: {cpf}")
        
        # Validar CPF
        if not self.validator.validar_cpf(cpf):
            logger.warning(f"❌ CPF inválido: {cpf}")
            await self.whatsapp.send_text(phone,
                "❌ CPF inválido!\n\nPor favor, digite um CPF válido (11 dígitos).\n\nExemplo: 12345678901")
            return
        
        logger.info(f"✅ CPF válido, buscando paciente...")
        
        # 🔧 CORREÇÃO: Verificar ação antes de buscar paciente
        contexto = conversa.context or {}
        acao = contexto.get("acao")
        
        if not acao:
            logger.error(f"❌ Ação não encontrada no contexto: {contexto}")
            await self.whatsapp.send_text(phone, "Desculpe, não entendi o que você queria fazer. Voltando ao menu principal.")
            conversa.state = "menu_principal"
            conversa.context = {}
            db.commit()
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        logger.info(f"🎯 Ação identificada: {acao}")
        
        # Buscar paciente
        paciente = await self.gestaods.buscar_paciente_cpf(cpf)
        
        logger.info(f"📋 Resultado da busca: {paciente}")
        
        if not paciente:
            logger.warning(f"❌ Paciente não encontrado para CPF: {cpf}")
            await self._handle_paciente_nao_encontrado(phone, cpf, conversa, db)
            return
        
        logger.info(f"✅ Paciente encontrado: {paciente.get('nome', 'N/A')}")
        
        # ✅ MOSTRAR CONFIRMAÇÃO DE PACIENTE (como nos exemplos)
        logger.info(f"🔄 Chamando _mostrar_confirmacao_paciente...")
        await self._mostrar_confirmacao_paciente(phone, paciente, conversa, db)
    
    async def _handle_paciente_nao_encontrado(self, phone: str, cpf: str, 
                                            conversa: Conversation, db: Session):
        """Trata quando paciente não é encontrado"""
        mensagem = """
❌ *CPF não encontrado em nosso sistema*

Você pode ser um novo paciente! 

*O que deseja fazer?*

1️⃣ Tentar outro CPF
2️⃣ Realizar cadastro
3️⃣ Falar com atendente
0️⃣ Voltar ao menu

Digite o número da opção:
"""
        await self.whatsapp.send_text(phone, mensagem)
        
        contexto = conversa.context or {}
        contexto['cpf_tentativa'] = cpf
        conversa.context = contexto
        conversa.state = "paciente_nao_encontrado"
        db.commit()
    
    async def _handle_paciente_nao_encontrado_opcoes(self, phone: str, message: str,
                                                    conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para quando paciente não é encontrado"""
        opcao = message.strip()
        
        if opcao == "1":
            # Tentar outro CPF
            await self.whatsapp.send_text(phone, "Por favor, digite seu CPF novamente:")
            conversa.state = "aguardando_cpf"
            db.commit()
        elif opcao == "2":
            # Realizar cadastro
            await self.whatsapp.send_text(phone, 
                "📋 *Para realizar seu cadastro:*\n\n"
                f"Entre em contato conosco:\n"
                f"📞 Telefone: {settings.clinic_phone}\n"
                f"📧 Email: {settings.clinic_email}\n\n"
                "Nosso atendimento fará seu cadastro e agendamento.\n\n"
                "Digite *1* para voltar ao menu principal.")
            conversa.state = "menu_principal"
            db.commit()
        elif opcao == "3":
            # Falar com atendente
            await self._mostrar_contato_atendente(phone)
            conversa.state = "menu_principal"
            db.commit()
        elif opcao == "0":
            # Voltar ao menu
            await self._mostrar_menu_principal(phone, conversa, db)
        else:
            await self.whatsapp.send_text(phone,
                "❌ Opção inválida!\n\n"
                "Digite:\n"
                "*1* - Tentar outro CPF\n"
                "*2* - Realizar cadastro\n"
                "*3* - Falar com atendente\n"
                "*0* - Voltar ao menu")
    
    async def _iniciar_agendamento(self, phone: str, paciente: Dict, 
                                  conversa: Conversation, db: Session):
        """Inicia processo de agendamento"""
        nome = paciente.get('nome', 'Paciente')
        
        # Buscar dias disponíveis
        dias = await self.gestaods.buscar_dias_disponiveis()
        
        if not dias:
            # ✅ PRESERVAR contexto mesmo quando API falha
            await self.whatsapp.send_text(phone,
                f"😔 Olá {nome}!\n\n"
                "No momento não encontrei dias disponíveis para agendamento.\n\n"
                "*O que deseja fazer?*\n\n"
                "1️⃣ Tentar novamente\n"
                "2️⃣ Entrar na lista de espera\n"
                "3️⃣ Falar com atendente\n"
                "0️⃣ Voltar ao menu")
            
            # ✅ Manter contexto mas mudar para estado de fallback
            contexto = conversa.context or {}
            contexto['expecting'] = 'agendamento_sem_dias'  # 🔧 CORREÇÃO: Flag expecting
            conversa.context = contexto
            conversa.state = "agendamento_sem_dias"
            
            # 🔧 CORREÇÃO: Persistir estado imediatamente
            db.commit()
            logger.info(f"💾 Estado 'agendamento_sem_dias' salvo, expecting: agendamento_sem_dias")
            return
        
        # Formatar mensagem com dias disponíveis
        mensagem = f"Olá, *{nome}*! 😊\n\n📅 *Escolha uma data:*\n\n"
        
        for i, dia in enumerate(dias[:7], 1):  # Limitar a 7 dias
            data = datetime.fromisoformat(dia['data'])
            data_formatada = data.strftime('%d/%m/%Y - %A').replace(
                'Monday', 'Segunda').replace('Tuesday', 'Terça').replace(
                'Wednesday', 'Quarta').replace('Thursday', 'Quinta').replace(
                'Friday', 'Sexta').replace('Saturday', 'Sábado').replace(
                'Sunday', 'Domingo')
            mensagem += f"*{i}* - {data_formatada}\n"
        
        mensagem += "\nDigite o número da data desejada:"
        
        await self.whatsapp.send_text(phone, mensagem)
        
        contexto = conversa.context or {}
        contexto['dias_disponiveis'] = dias[:7]
        contexto['expecting'] = 'escolha_data'  # 🔧 CORREÇÃO: Flag expecting
        conversa.context = contexto
        conversa.state = "escolhendo_data"
        
        # 🔧 CORREÇÃO: Persistir estado imediatamente
        db.commit()
        logger.info(f"💾 Estado 'escolhendo_data' salvo, expecting: escolha_data")
    
    async def _handle_escolha_data(self, phone: str, message: str, conversa: Conversation,
                                  db: Session, nlu_result: Dict):
        """Handler para escolha de data com validação expecting"""
        # 🔧 CORREÇÃO: Validar expecting apenas se claramente errado
        expecting = conversa.context.get("expecting")
        if expecting and expecting not in ["escolha_data", None] and conversa.state == "escolhendo_data":
            logger.warning(f"❌ Escolha de data fora de contexto - expecting: {expecting}")
            await self.whatsapp.send_text(phone, "Desculpe, não entendi. Voltando ao menu principal.")
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        try:
            opcao = int(message.strip())
            contexto = conversa.context or {}
            dias = contexto.get('dias_disponiveis', [])
            
            if 1 <= opcao <= len(dias):
                dia_escolhido = dias[opcao - 1]
                contexto['data_escolhida'] = dia_escolhido
                contexto['expecting'] = 'escolha_horario'  # 🔧 CORREÇÃO: Flag expecting
                
                # Buscar horários disponíveis
                horarios = await self.gestaods.buscar_horarios_disponiveis(dia_escolhido['data'])
                
                if not horarios:
                    await self.whatsapp.send_text(phone,
                        "😔 Não há horários disponíveis para esta data.\n\n"
                        "*O que deseja fazer?*\n\n"
                        "1️⃣ Escolher outra data\n"
                        "2️⃣ Lista de espera\n"
                        "0️⃣ Voltar ao menu")
                    
                    # ✅ PRESERVAR estado e contexto!
                    conversa.state = "data_sem_horarios"
                    db.commit()  # ✅ SEMPRE FAZER COMMIT!
                    return
                
                # Mostrar horários
                data = datetime.fromisoformat(dia_escolhido['data'])
                mensagem = f"📅 Data: *{data.strftime('%d/%m/%Y')}*\n\n⏰ *Horários disponíveis:*\n\n"
                
                for i, horario in enumerate(horarios[:8], 1):  # Limitar a 8 horários
                    mensagem += f"*{i}* - {horario['horario']}\n"
                
                mensagem += "\nDigite o número do horário desejado:"
                
                await self.whatsapp.send_text(phone, mensagem)
                
                contexto['horarios_disponiveis'] = horarios[:8]
                conversa.context = contexto
                conversa.state = "escolhendo_horario"
                
                # 🔧 CORREÇÃO: Persistir estado imediatamente
                db.commit()
                logger.info(f"💾 Estado 'escolhendo_horario' salvo, expecting: escolha_horario")
                
            else:
                await self.whatsapp.send_text(phone,
                    "❌ Opção inválida!\n\nPor favor, escolha um número válido.")
                
        except ValueError:
            await self.whatsapp.send_text(phone,
                "❌ Por favor, digite apenas o número da opção desejada.")
    
    async def _handle_escolha_horario(self, phone: str, message: str, conversa: Conversation,
                                     db: Session, nlu_result: Dict):
        """Handler para escolha de horário com validação expecting"""
        # 🔧 CORREÇÃO: Validar expecting apenas se claramente errado
        expecting = conversa.context.get("expecting")
        if expecting and expecting not in ["escolha_horario", None] and conversa.state == "escolhendo_horario":
            logger.warning(f"❌ Escolha de horário fora de contexto - expecting: {expecting}")
            await self.whatsapp.send_text(phone, "Desculpe, não entendi. Voltando ao menu principal.")
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        try:
            opcao = int(message.strip())
            contexto = conversa.context or {}
            horarios = contexto.get('horarios_disponiveis', [])
            
            if 1 <= opcao <= len(horarios):
                horario_escolhido = horarios[opcao - 1]
                contexto['horario_escolhido'] = horario_escolhido
                
                # Mostrar resumo para confirmação
                paciente = contexto.get('paciente', {})
                data = datetime.fromisoformat(contexto['data_escolhida']['data'])
                
                mensagem = f"""
✅ *Confirmar agendamento:*

👤 Paciente: *{paciente.get('nome')}*
📅 Data: *{data.strftime('%d/%m/%Y')}*
⏰ Horário: *{horario_escolhido['horario']}*
👩‍⚕️ Profissional: *Dra. Gabriela Nassif*

*Confirma o agendamento?*

*1* - ✅ Sim, confirmar
*2* - ❌ Não, cancelar
"""
                await self.whatsapp.send_text(phone, mensagem)
                
                contexto['expecting'] = 'confirmacao_agendamento'  # 🔧 CORREÇÃO: Flag expecting
                conversa.context = contexto
                conversa.state = "confirmando_agendamento"
                
                # 🔧 CORREÇÃO: Persistir estado imediatamente
                db.commit()
                logger.info(f"💾 Estado 'confirmando_agendamento' salvo, expecting: confirmacao_agendamento")
                
            else:
                await self.whatsapp.send_text(phone,
                    "❌ Opção inválida!\n\nPor favor, escolha um número válido.")
                
        except ValueError:
            await self.whatsapp.send_text(phone,
                "❌ Por favor, digite apenas o número da opção desejada.")
    
    async def _handle_confirmacao(self, phone: str, message: str, conversa: Conversation,
                                 db: Session, nlu_result: Dict):
        """Handler para confirmação de agendamento com validação expecting"""
        # 🔧 CORREÇÃO: Validar expecting apenas se claramente errado
        expecting = conversa.context.get("expecting")
        if expecting and expecting not in ["confirmacao_agendamento", None] and conversa.state == "confirmando_agendamento":
            logger.warning(f"❌ Confirmação fora de contexto - expecting: {expecting}")
            await self.whatsapp.send_text(phone, "Desculpe, não entendi. Voltando ao menu principal.")
            await self._mostrar_menu_principal(phone, conversa, db)
            return
        
        opcao = message.strip()
        
        if opcao == "1":
            contexto = conversa.context
            paciente = contexto['paciente']
            data_escolhida = contexto['data_escolhida']['data']
            horario = contexto['horario_escolhido']['horario']
            
            # Formatar datas para API usando método correto
            # Criar datetime objects
            dt_inicio = datetime.fromisoformat(f"{data_escolhida} {horario}:00")
            dt_fim = dt_inicio + timedelta(minutes=30)  # 30 min de consulta
            
            # Converter para formato da API usando método do GestãoDS (dd/mm/yyyy hh:mm:ss)
            data_inicio_api = self.gestaods.converter_datetime_para_api(dt_inicio)
            data_fim_api = self.gestaods.converter_datetime_para_api(dt_fim)
            
            # Criar agendamento
            resultado = await self.gestaods.criar_agendamento(
                cpf=paciente['cpf'],
                data_agendamento=data_inicio_api,
                data_fim_agendamento=data_fim_api,
                primeiro_atendimento=True
            )
            
            if resultado:
                # Salvar no banco local
                novo_agendamento = Appointment(
                    patient_id=str(paciente.get('id', '')),
                    patient_name=paciente['nome'],
                    patient_phone=phone,
                    appointment_date=dt_inicio,
                    appointment_type="Consulta médica",
                    status="scheduled"
                )
                db.add(novo_agendamento)
                db.commit()
                
                # Enviar confirmação
                mensagem = f"""
✅ *Agendamento confirmado com sucesso!*

📋 *Detalhes da consulta:*
👤 Paciente: {paciente['nome']}
📅 Data: {dt_inicio.strftime('%d/%m/%Y')}
⏰ Horário: {horario}
👩‍⚕️ Profissional: Dra. Gabriela Nassif

📍 *Endereço:*
{settings.clinic_address}

💡 *Lembretes:*
• Chegue com 15 minutos de antecedência
• Traga documentos e exames anteriores
• Em caso de atraso, entre em contato

Obrigado pela confiança! 😊

Digite *1* para voltar ao menu principal.
"""
                await self.whatsapp.send_text(phone, mensagem)
                
            else:
                await self.whatsapp.send_text(phone,
                    "❌ Erro ao confirmar agendamento.\n\n"
                    "Por favor, tente novamente ou entre em contato:\n"
                    f"📞 {settings.clinic_phone}")
            
            conversa.state = "menu_principal"
            conversa.context = {}
            db.commit()
            
        elif opcao == "2":
            await self.whatsapp.send_text(phone,
                "❌ Agendamento cancelado.\n\n"
                "Digite *1* para voltar ao menu principal.")
            conversa.state = "menu_principal"
            conversa.context = {}
            db.commit()
        else:
            await self.whatsapp.send_text(phone,
                "Por favor, digite:\n*1* para confirmar\n*2* para cancelar")
    
    async def _mostrar_agendamentos(self, phone: str, paciente: Dict, 
                                   conversa: Conversation, db: Session):
        """Mostra agendamentos do paciente"""
        # Buscar agendamentos
        data_inicial = datetime.now().strftime("%d/%m/%Y")
        data_final = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")
        
        agendamentos = await self.gestaods.listar_agendamentos_periodo(data_inicial, data_final)
        
        # Filtrar agendamentos do paciente
        agendamentos_paciente = [
            ag for ag in agendamentos 
            if ag.get('cpf') == paciente['cpf']
        ]
        
        if not agendamentos_paciente:
            await self.whatsapp.send_text(phone,
                "📅 Você não possui agendamentos futuros.\n\n"
                "Digite *1* para agendar uma consulta\n"
                "Digite *0* para voltar ao menu")
        else:
            mensagem = f"📅 *Seus agendamentos:*\n\n"
            
            for i, ag in enumerate(agendamentos_paciente[:5], 1):
                try:
                    dt = datetime.fromisoformat(ag['data_hora'])
                    mensagem += f"*{i}.* {dt.strftime('%d/%m/%Y às %H:%M')}\n"
                    mensagem += f"   👩‍⚕️ Dra. Gabriela Nassif\n"
                    mensagem += f"   📋 Status: {ag.get('status', 'Agendado')}\n\n"
                except:
                    pass
            
            mensagem += "*Opções:*\n"
            mensagem += "*1* - Agendar nova consulta\n"
            mensagem += "*3* - Cancelar consulta\n"
            mensagem += "*0* - Voltar ao menu"
            
            await self.whatsapp.send_text(phone, mensagem)
        
        conversa.state = "visualizando_agendamentos"
        db.commit()
    
    async def _handle_visualizar_agendamentos(self, phone: str, message: str,
                                             conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para visualização de agendamentos"""
        opcao = message.strip()
        
        if opcao == "0":
            await self._mostrar_menu_principal(phone, conversa, db)
        elif opcao == "1":
            conversa.context = {"acao": "agendar"}
            conversa.state = "aguardando_cpf"
            await self.whatsapp.send_text(phone,
                "Vamos agendar sua consulta! 📅\n\n"
                "Por favor, digite seu *CPF* (apenas números):")
            db.commit()
        elif opcao == "3":
            await self._mostrar_contato_cancelamento(phone)
            conversa.state = "menu_principal"
            db.commit()
        else:
            await self.whatsapp.send_text(phone,
                "Opção inválida! Digite:\n"
                "*0* para menu\n*1* para agendar\n*3* para cancelar")
    
    async def _iniciar_cancelamento(self, phone: str, paciente: Dict,
                                   conversa: Conversation, db: Session):
        """Inicia processo de cancelamento"""
        await self._mostrar_contato_cancelamento(phone)
        conversa.state = "menu_principal"
        db.commit()
    
    async def _mostrar_contato_cancelamento(self, phone: str):
        """Mostra contato para cancelamento"""
        await self.whatsapp.send_text(phone, f"""
📞 *Para cancelar seu agendamento:*

Entre em contato conosco:
📞 Telefone: {settings.clinic_phone}
📧 Email: {settings.clinic_email}

⏰ *Horário de atendimento:*
Segunda a Sexta: 8h às 18h
Sábado: 8h às 12h

Digite *1* para voltar ao menu principal.
""")
    
    async def _adicionar_lista_espera(self, phone: str, paciente: Dict,
                                     conversa: Conversation, db: Session):
        """Adiciona paciente à lista de espera"""
        # Verificar se já está na lista
        lista_existente = db.query(WaitingList).filter_by(
            patient_id=str(paciente.get('id', ''))
        ).first()
        
        if lista_existente:
            await self.whatsapp.send_text(phone,
                "📝 Você já está na lista de espera!\n\n"
                "Assim que houver uma vaga, entraremos em contato.\n\n"
                "Digite *1* para voltar ao menu principal.")
        else:
            # Adicionar à lista
            nova_entrada = WaitingList(
                patient_id=str(paciente.get('id', '')),
                patient_name=paciente['nome'],
                patient_phone=phone,
                priority=0,
                notified=False
            )
            db.add(nova_entrada)
            db.commit()
            
            await self.whatsapp.send_text(phone,
                "✅ *Adicionado à lista de espera com sucesso!*\n\n"
                "Assim que houver uma vaga disponível, "
                "entraremos em contato com você.\n\n"
                "Digite *1* para voltar ao menu principal.")
        
        conversa.state = "menu_principal"
        db.commit()
    
    async def _handle_lista_espera(self, phone: str, message: str, conversa: Conversation,
                                  db: Session, nlu_result: Dict):
        """Handler para lista de espera"""
        if message.strip() == "1":
            await self._mostrar_menu_principal(phone, conversa, db)
        else:
            await self.whatsapp.send_text(phone,
                "Digite *1* para voltar ao menu principal.")
    
    async def _mostrar_contato_atendente(self, phone: str):
        """Mostra informações de contato do atendente"""
        await self.whatsapp.send_text(phone, f"""
👨‍⚕️ *Atendimento Humano*

Entre em contato conosco:

📞 Telefone: {settings.clinic_phone}
📧 Email: {settings.clinic_email}

⏰ *Horário de atendimento:*
Segunda a Sexta: 8h às 18h
Sábado: 8h às 12h

Digite *1* para voltar ao menu principal.
""")
    
    async def _finalizar_conversa(self, phone: str, conversa: Conversation, db: Session):
        """Finaliza a conversa"""
        await self.whatsapp.send_text(phone,
            "👋 *Obrigado por usar nossos serviços!*\n\n"
            "Tenha um ótimo dia! 😊\n\n"
            "Para iniciar uma nova conversa, digite *oi*.")
        
        conversa.state = "finalizada"
        conversa.context = {"finalizada_em": datetime.utcnow().isoformat()}
        db.commit()
        
        # Limpar cache
        if phone in self.conversation_cache:
            del self.conversation_cache[phone]
    
    async def _cancelar_operacao_atual(self, phone: str, conversa: Conversation, db: Session):
        """Cancela operação atual e volta ao menu"""
        await self.whatsapp.send_text(phone,
            "❌ Operação cancelada.\n\n"
            "Voltando ao menu principal...")
        
        await asyncio.sleep(1)
        await self._mostrar_menu_principal(phone, conversa, db)
    
    async def _handle_estado_desconhecido(self, phone: str, message: str, 
                                        conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para estados desconhecidos com recuperação inteligente"""
        logger.warning(f"⚠️ Estado desconhecido: {conversa.state}")
        
        # Tentar recuperar do contexto
        contexto = conversa.context or {}
        acao = contexto.get('acao')
        
        if acao:
            logger.info(f"🔄 Tentando recuperar do contexto: ação={acao}")
            # Tentar continuar baseado na ação
            if acao in ['agendar', 'visualizar', 'cancelar', 'lista_espera']:
                conversa.state = 'aguardando_cpf'
                await self.whatsapp.send_text(phone, 
                    "Parece que houve um problema. Vamos continuar! 💪\n\n"
                    "Por favor, digite seu CPF (apenas números):")
                db.commit()
                return
        
        # Só volta ao menu se não conseguir recuperar
        logger.info("   🔄 Não foi possível recuperar contexto, voltando ao menu")
        await self._mostrar_menu_principal(phone, conversa, db)
    
    async def _handle_error(self, phone: str, conversa: Conversation, db: Session):
        """Handler de erro mais robusto - NÃO reseta estado automaticamente"""
        logger.error(f"🚨 ERRO durante processamento para {phone}")
        logger.error(f"   Estado atual: {conversa.state}")
        logger.error(f"   Contexto: {conversa.context}")
        
        # 🔧 CORREÇÃO: Não resetar estado automaticamente!
        # Apenas informar erro ao usuário
        await self.whatsapp.send_text(phone, 
            "😔 Ops! Houve um problema temporário.\n\n"
            "💡 Você pode continuar de onde parou ou digitar *menu* para recomeçar.")
        
        # Manter estado atual - NÃO resetar!
        logger.info("   ✅ Estado preservado após erro")


    async def _handle_agendamento_sem_dias(self, phone: str, message: str, 
                                          conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para quando não há dias disponíveis"""
        opcao = message.strip()
        
        if opcao == "1":
            # Tentar novamente
            contexto = conversa.context or {}
            paciente = contexto.get('paciente')
            if paciente:
                await self._iniciar_agendamento(phone, paciente, conversa, db)
            else:
                # Se não tem paciente no contexto, volta para CPF
                conversa.state = "aguardando_cpf"
                await self.whatsapp.send_text(phone, 
                    "Vamos tentar novamente! Digite seu CPF:")
                db.commit()
        elif opcao == "2":
            # Lista de espera
            contexto = conversa.context or {}
            paciente = contexto.get('paciente')
            if paciente:
                await self._adicionar_lista_espera(phone, paciente, conversa, db)
            else:
                conversa.state = "aguardando_cpf"
                contexto['acao'] = 'lista_espera'
                conversa.context = contexto
                await self.whatsapp.send_text(phone, 
                    "Para entrar na lista de espera, digite seu CPF:")
                db.commit()
        elif opcao == "3":
            # Falar com atendente
            await self._mostrar_contato_atendente(phone)
            conversa.state = "menu_principal"
            db.commit()
        elif opcao == "0":
            # Voltar ao menu
            await self._mostrar_menu_principal(phone, conversa, db)
        else:
            await self.whatsapp.send_text(phone,
                "❌ Opção inválida!\n\nDigite:\n"
                "*1* - Tentar novamente\n"
                "*2* - Lista de espera\n"
                "*3* - Falar com atendente\n"
                "*0* - Voltar ao menu")
            db.commit()
    
    async def _handle_data_sem_horarios(self, phone: str, message: str, 
                                       conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para quando data não tem horários"""
        opcao = message.strip()
        
        if opcao == "1":
            # Escolher outra data
            conversa.state = "escolhendo_data"
            await self.whatsapp.send_text(phone, 
                "📅 Escolha outra data das opções disponíveis:")
            db.commit()
        elif opcao == "2":
            # Lista de espera
            contexto = conversa.context or {}
            paciente = contexto.get('paciente')
            if paciente:
                await self._adicionar_lista_espera(phone, paciente, conversa, db)
            else:
                await self.whatsapp.send_text(phone, 
                    "Para entrar na lista de espera, digite seu CPF:")
                conversa.state = "aguardando_cpf"
                contexto['acao'] = 'lista_espera'
                conversa.context = contexto
                db.commit()
        elif opcao == "0":
            # Voltar ao menu
            await self._mostrar_menu_principal(phone, conversa, db)
        else:
            await self.whatsapp.send_text(phone,
                "❌ Opção inválida!\n\nDigite:\n"
                "*1* - Escolher outra data\n"
                "*2* - Lista de espera\n"
                "*0* - Voltar ao menu")
            db.commit()

    async def _mostrar_confirmacao_paciente(self, phone: str, paciente: Dict, 
                                           conversa: Conversation, db: Session):
        """Mostra dados do paciente para confirmação"""
        nome = paciente.get('nome', 'Paciente')
        cpf = paciente.get('cpf', '')
        cpf_formatado = self._formatar_cpf_display(cpf)
        
        mensagem = f"""
✅ *Paciente encontrado!*

👤 *Nome:* {nome}
🆔 *CPF:* {cpf_formatado}

*Confirma que é você?*

*1* - ✅ Sim, é meu cadastro
*2* - ❌ Não, digite outro CPF
*0* - 🏠 Voltar ao menu

Digite o número da opção:
"""
        await self.whatsapp.send_text(phone, mensagem)
        
        # Salvar paciente temporariamente
        contexto = conversa.context or {}
        contexto['paciente_temp'] = paciente
        contexto['expecting'] = 'confirmacao_paciente'  # 🔧 CORREÇÃO: Flag expecting
        conversa.context = contexto
        conversa.state = "confirmando_paciente"
        
        # 🔧 CORREÇÃO: Persistir estado imediatamente
        db.commit()
        logger.info(f"💾 Estado 'confirmando_paciente' salvo, expecting: confirmacao_paciente")

    async def _handle_confirmacao_paciente(self, phone: str, message: str, 
                                         conversa: Conversation, db: Session, nlu_result: Dict):
        """Handler para confirmação de paciente"""
        opcao = message.strip()
        contexto = conversa.context or {}
        
        logger.info(f"🔍 Confirmação de paciente - Opção: '{opcao}'")
        
        if opcao == "1":
            # Confirmar paciente
            paciente = contexto.get('paciente_temp')
            if paciente:
                contexto['paciente'] = paciente
                contexto.pop('paciente_temp', None)
                conversa.context = contexto
                
                logger.info(f"✅ Paciente confirmado: {paciente.get('nome')}")
                
                # 🔧 CORREÇÃO: Fallback robusto quando ação estiver ausente
                acao = contexto.get('acao')
                logger.info(f"🎯 Processando ação após confirmação: {acao}")
                
                if acao == "agendar":
                    await self._iniciar_agendamento(phone, paciente, conversa, db)
                elif acao == "visualizar":
                    await self._mostrar_agendamentos(phone, paciente, conversa, db)
                elif acao == "cancelar":
                    await self._iniciar_cancelamento(phone, paciente, conversa, db)
                elif acao == "lista_espera":
                    await self._adicionar_lista_espera(phone, paciente, conversa, db)
                else:
                    logger.warning(f"❌ Ação não reconhecida: {acao}")
                    await self.whatsapp.send_text(phone, "Desculpe, não entendi o que você queria fazer. Voltando ao menu principal.")
                    conversa.state = "menu_principal"
                    conversa.context = {}
                    db.commit()
                    await self._mostrar_menu_principal(phone, conversa, db)
            else:
                logger.error("❌ Paciente temporário não encontrado no contexto")
                await self._mostrar_menu_principal(phone, conversa, db)
        
        elif opcao == "2":
            # Tentar outro CPF
            await self.whatsapp.send_text(phone, "Por favor, digite o CPF correto:")
            conversa.state = "aguardando_cpf"
            contexto.pop('paciente_temp', None)
            contexto['expecting'] = 'cpf'  # 🔧 CORREÇÃO: Flag expecting
            conversa.context = contexto
            # 🔧 CORREÇÃO: Persistir estado imediatamente
            db.commit()
            logger.info(f"💾 Estado 'aguardando_cpf' salvo, expecting: cpf")
            
        elif opcao == "0":
            # Voltar ao menu
            contexto.pop('paciente_temp', None)
            conversa.context = contexto
            await self._mostrar_menu_principal(phone, conversa, db)
            
        else:
            await self.whatsapp.send_text(phone,
                "❌ Opção inválida!\n\n"
                "Digite:\n*1* - Sim, é meu cadastro\n*2* - Não, outro CPF\n*0* - Voltar ao menu")
            db.commit()

    def _formatar_cpf_display(self, cpf: str) -> str:
        """Formata CPF para exibição: 123.456.789-01"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf

    def _get_or_create_conversation(self, phone: str, db: Session) -> Conversation:
        """Busca ou cria conversa"""
        conversa = db.query(Conversation).filter_by(phone=phone).first()
        
        if not conversa:
            conversa = Conversation(
                phone=phone,
                state="inicio",
                context={}
            )
            db.add(conversa)
            db.commit()
        
        return conversa
    
    async def _handle_conversa_finalizada(self, phone: str, message: str, conversa: Conversation,
                                          db: Session, nlu_result: Dict):
        """Handler para conversa finalizada - reinicia automaticamente"""
        logger.info(f"🔄 Conversa finalizada recebeu mensagem: '{message}'")
        logger.info("Reiniciando conversa automaticamente...")
        
        # Reiniciar conversa - tratar como nova saudação
        conversa.state = "inicio"
        conversa.context = {}
        db.commit()
        
        # Processar como saudação inicial
        await self._handle_inicio(phone, message, conversa, db, nlu_result)