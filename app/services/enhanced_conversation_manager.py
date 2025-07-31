import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import Conversation
from app.services.patient_transaction_service import PatientTransactionService, TransactionContext
from app.services.decision_engine import IntelligentDecisionEngine
from app.services.whatsapp import WhatsAppService
from app.utils.formatters import FormatterUtils
from app.config import settings
from app.models.patient_transaction import DecisionType, TransactionStage

logger = logging.getLogger(__name__)

class EnhancedConversationManager:
    """
    Gerenciador de conversas aprimorado com sistema robusto de transações
    
    Este manager integra:
    - Sistema de transações auditáveis
    - Motor de decisão inteligente  
    - Cache inteligente de pacientes
    - Logs detalhados para auditoria
    - Recuperação automática de erros
    """
    
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.transaction_service = PatientTransactionService()
        self.decision_engine = IntelligentDecisionEngine()
        
    async def processar_mensagem_robusta(
        self, 
        phone: str, 
        message: str, 
        message_id: str, 
        db: Session
    ):
        """
        Processa mensagem com sistema robusto completo
        
        Fluxo:
        1. Carrega/cria conversa
        2. Executa transação de paciente com auditoria
        3. Usa motor de decisão inteligente
        4. Executa ação recomendada
        5. Salva tudo com logs auditáveis
        """
        try:
            logger.info(f"🚀 PROCESSAMENTO ROBUSTO INICIADO")
            logger.info(f"📞 Telefone: {phone}")
            logger.info(f"💬 Mensagem: '{message}'")
            
            # Marcar como lida
            await self._mark_as_read_safe(phone, message_id)
            
            # 1. Buscar ou criar conversa
            conversa = self._get_or_create_conversation(phone, db)
            logger.info(f"📋 Conversa ID: {conversa.id}, Estado: {conversa.state}")
            
            # 2. Processar transação completa
            transaction_context = await self.transaction_service.process_patient_transaction(
                phone=phone,
                user_input=message,
                conversation=conversa,
                db=db
            )
            
            logger.info(f"⚙️ Transação processada: {transaction_context.current_stage.value}")
            
            # 3. Usar motor de decisão inteligente
            decision_result = self.decision_engine.analyze_and_decide(
                current_stage=transaction_context.current_stage,
                user_input=message,
                context=transaction_context.loaded_context,
                patient_data=transaction_context.patient_data,
                validation_result=transaction_context.validation_results,
                errors=transaction_context.errors,
                warnings=transaction_context.warnings
            )
            
            logger.info(f"🎯 Decisão: {decision_result.chosen_decision.value} (confiança: {decision_result.confidence:.2f})")
            
            # 4. Executar ação baseada na decisão
            await self._execute_decision_action(
                phone=phone,
                decision_result=decision_result,
                transaction_context=transaction_context,
                conversa=conversa,
                db=db
            )
            
            # 5. Salvar estado final
            db.commit()
            
            logger.info(f"✅ Processamento concluído com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento robusto: {str(e)}")
            await self._handle_critical_error(phone, conversa if 'conversa' in locals() else None, db, str(e))
    
    async def _execute_decision_action(
        self,
        phone: str,
        decision_result,
        transaction_context: TransactionContext,
        conversa: Conversation,
        db: Session
    ):
        """Executa ação baseada na decisão do motor inteligente"""
        action = decision_result.suggested_action
        decision_type = decision_result.chosen_decision
        
        try:
            # Mapear decisões para ações
            action_handlers = {
                DecisionType.CORRIGIR: self._handle_correction_action,
                DecisionType.CONFIRMAR: self._handle_confirmation_action,
                DecisionType.AGENDAR: self._handle_scheduling_action,
                DecisionType.VISUALIZAR: self._handle_view_action,
                DecisionType.AVANÇAR: self._handle_advance_action,
                DecisionType.REPETIR: self._handle_repeat_action,
                DecisionType.ESCALATE: self._handle_escalation_action
            }
            
            handler = action_handlers.get(decision_type, self._handle_default_action)
            await handler(phone, transaction_context, decision_result, conversa, db)
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar ação {action}: {str(e)}")
            
            # Tentar ação de fallback
            if decision_result.fallback_action:
                await self._execute_fallback_action(phone, decision_result.fallback_action, conversa)
            else:
                await self._handle_action_failure(phone, conversa)
    
    async def _handle_correction_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata correção de erros"""
        if context.errors:
            error_msg = context.errors[0]  # Primeiro erro
            
            if "CPF inválido" in error_msg:
                await self.whatsapp.send_text(phone,
                    "❌ *CPF inválido!*\n\n"
                    "Por favor, digite um CPF válido com 11 dígitos.\n\n"
                    "📝 Exemplo: 12345678901\n\n"
                    "Digite seu CPF novamente:")
                
                conversa.state = "aguardando_cpf"
                
            elif "não encontrado" in error_msg:
                await self._handle_patient_not_found(phone, conversa, db)
                
            else:
                await self.whatsapp.send_text(phone,
                    f"⚠️ *Erro detectado:*\n\n{error_msg}\n\n"
                    "Por favor, tente novamente ou digite *menu* para voltar ao início.")
        else:
            await self._handle_default_action(phone, context, decision_result, conversa, db)
    
    async def _handle_confirmation_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata confirmação de dados do paciente"""
        if context.patient_data:
            patient = context.patient_data
            nome = patient.get('nome', 'Paciente')
            cpf_formatado = self._format_cpf_display(patient.get('cpf', ''))
            
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
            conversa.state = "confirmando_paciente"
            
        else:
            await self._handle_patient_not_found(phone, conversa, db)
    
    async def _handle_scheduling_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata início do agendamento"""
        if context.patient_data:
            nome = context.patient_data.get('nome', 'Paciente')
            
            mensagem = f"""
📅 *Vamos agendar sua consulta, {nome}!*

Buscando datas disponíveis...
"""
            await self.whatsapp.send_text(phone, mensagem)
            
            # Simular busca de datas (integrar com GestãoDS)
            await self._mostrar_datas_disponiveis(phone, context.patient_data, conversa, db)
        else:
            await self._handle_patient_data_missing(phone, conversa)
    
    async def _handle_view_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata visualização de agendamentos"""
        if context.patient_data:
            await self._mostrar_agendamentos_paciente(phone, context.patient_data, conversa, db)
        else:
            await self._handle_patient_data_missing(phone, conversa)
    
    async def _handle_advance_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata avanço no fluxo"""
        current_state = conversa.state
        
        if current_state == "inicio":
            await self._mostrar_menu_principal(phone, conversa)
        elif current_state == "menu_principal":
            await self._handle_menu_option(phone, context.user_input, conversa, db)
        elif current_state == "confirmando_paciente":
            await self._handle_patient_confirmation(phone, context.user_input, context, conversa, db)
        else:
            await self._mostrar_menu_principal(phone, conversa)
    
    async def _handle_repeat_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata repetição da última ação"""
        await self.whatsapp.send_text(phone,
            "🔄 Vamos tentar novamente...\n\n"
            "Por favor, digite sua resposta:")
        # Estado permanece o mesmo para repetir
    
    async def _handle_escalation_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata escalonamento para atendimento humano"""
        await self.whatsapp.send_text(phone, f"""
👨‍⚕️ *Transferindo para atendimento humano*

Detectamos que você precisa de ajuda especializada.

📞 *Entre em contato:*
Telefone: {settings.clinic_phone}
Email: {settings.clinic_email}

⏰ *Horário de atendimento:*
Segunda a Sexta: 8h às 18h
Sábado: 8h às 12h

Obrigado pela compreensão! 🙏
""")
        conversa.state = "escalated"
    
    async def _handle_default_action(
        self, 
        phone: str, 
        context: TransactionContext, 
        decision_result, 
        conversa: Conversation, 
        db: Session
    ):
        """Ação padrão quando não há handler específico"""
        await self._mostrar_menu_principal(phone, conversa)
    
    async def _mostrar_menu_principal(self, phone: str, conversa: Conversation):
        """Mostra menu principal"""
        saudacao = FormatterUtils.formatar_saudacao()
        menu = f"""
{saudacao} Bem-vindo(a) à *{settings.clinic_name}*! 🏥

Sou seu assistente inteligente. Como posso ajudar?

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
    
    async def _handle_menu_option(
        self, 
        phone: str, 
        option: str, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata opção do menu principal"""
        opcao = option.strip()
        
        opcoes = {
            "1": ("agendar", "Vamos agendar sua consulta! 📅\n\nPor favor, digite seu *CPF* (apenas números):"),
            "2": ("visualizar", "Para ver seus agendamentos, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):"),
            "3": ("cancelar", "Para cancelar uma consulta, preciso do seu *CPF*.\n\nDigite seu CPF (apenas números):"),
            "4": ("lista_espera", "Vou adicionar você na lista de espera! 📝\n\nDigite seu *CPF* (apenas números):"),
            "5": (None, None)
        }
        
        if opcao in opcoes:
            acao, mensagem = opcoes[opcao]
            
            if opcao == "5":
                await self._mostrar_contato_atendente(phone)
            else:
                await self.whatsapp.send_text(phone, mensagem)
                conversa.state = "aguardando_cpf"
                conversa.context = {"acao": acao}
        else:
            await self.whatsapp.send_text(phone, 
                "❌ Opção inválida!\n\nPor favor, digite um número de *1 a 5*.")
    
    async def _handle_patient_confirmation(
        self, 
        phone: str, 
        option: str, 
        context: TransactionContext, 
        conversa: Conversation, 
        db: Session
    ):
        """Trata confirmação do paciente"""
        opcao = option.strip()
        
        if opcao == "1":
            # Paciente confirmado, executar ação pretendida
            acao = conversa.context.get('acao')
            
            if acao == "agendar":
                await self._handle_scheduling_action(phone, context, None, conversa, db)
            elif acao == "visualizar":
                await self._handle_view_action(phone, context, None, conversa, db)
            else:
                await self._mostrar_menu_principal(phone, conversa)
                
        elif opcao == "2":
            # Tentar outro CPF
            await self.whatsapp.send_text(phone, "Por favor, digite o CPF correto:")
            conversa.state = "aguardando_cpf"
            
        elif opcao == "0":
            # Voltar ao menu
            await self._mostrar_menu_principal(phone, conversa)
        else:
            await self.whatsapp.send_text(phone,
                "❌ Opção inválida!\n\n"
                "Digite:\n*1* - Sim, é meu cadastro\n*2* - Não, outro CPF\n*0* - Voltar ao menu")
    
    async def _handle_patient_not_found(self, phone: str, conversa: Conversation, db: Session):
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
        conversa.state = "paciente_nao_encontrado"
    
    async def _handle_patient_data_missing(self, phone: str, conversa: Conversation):
        """Trata quando dados do paciente estão faltando"""
        await self.whatsapp.send_text(phone,
            "⚠️ Dados do paciente não encontrados.\n\n"
            "Por favor, digite seu CPF novamente:")
        conversa.state = "aguardando_cpf"
    
    async def _mostrar_datas_disponiveis(
        self, 
        phone: str, 
        patient_data: Dict, 
        conversa: Conversation, 
        db: Session
    ):
        """Mostra datas disponíveis para agendamento"""
        # Integração com sistema de datas real
        mensagem = """
📅 *Datas disponíveis para consulta:*

*1* - Amanhã (15/01) - Manhã
*2* - Quinta (16/01) - Tarde  
*3* - Sexta (17/01) - Manhã
*4* - Segunda (20/01) - Tarde

Digite o número da data desejada:
"""
        await self.whatsapp.send_text(phone, mensagem)
        conversa.state = "escolhendo_data"
    
    async def _mostrar_agendamentos_paciente(
        self, 
        phone: str, 
        patient_data: Dict, 
        conversa: Conversation, 
        db: Session
    ):
        """Mostra agendamentos do paciente"""
        nome = patient_data.get('nome', 'Paciente')
        
        # Integração com sistema real de agendamentos
        mensagem = f"""
📅 *Agendamentos de {nome}:*

*Próximas consultas:*
• 20/01/2024 às 14:30 - Dra. Gabriela
• 25/01/2024 às 09:00 - Dra. Gabriela

*Opções:*
*1* - Agendar nova consulta
*3* - Cancelar consulta
*0* - Voltar ao menu

Digite o número da opção:
"""
        await self.whatsapp.send_text(phone, mensagem)
        conversa.state = "visualizando_agendamentos"
    
    async def _mostrar_contato_atendente(self, phone: str):
        """Mostra informações de contato"""
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
    
    async def _execute_fallback_action(self, phone: str, fallback_action: str, conversa: Conversation):
        """Executa ação de fallback"""
        if fallback_action == "voltar_menu_principal":
            await self._mostrar_menu_principal(phone, conversa)
        elif fallback_action == "repetir_ultima_acao":
            await self.whatsapp.send_text(phone,
                "🔄 Vamos tentar novamente...\n\n"
                "Por favor, repita sua solicitação:")
        else:
            await self._mostrar_menu_principal(phone, conversa)
    
    async def _handle_action_failure(self, phone: str, conversa: Conversation):
        """Trata falha na execução de ação"""
        await self.whatsapp.send_text(phone,
            "⚠️ Ocorreu um problema no sistema.\n\n"
            "Voltando ao menu principal...")
        await self._mostrar_menu_principal(phone, conversa)
    
    async def _handle_critical_error(
        self, 
        phone: str, 
        conversa: Optional[Conversation], 
        db: Session, 
        error_msg: str
    ):
        """Trata erro crítico do sistema"""
        try:
            await self.whatsapp.send_text(phone,
                "⚠️ Ocorreu um erro no sistema.\n\n"
                f"Por favor, entre em contato: {settings.clinic_phone}\n\n"
                "Ou digite *menu* para tentar novamente.")
            
            if conversa:
                conversa.state = "erro"
                conversa.context = {
                    "error": error_msg,
                    "timestamp": datetime.utcnow().isoformat()
                }
                db.commit()
                
        except Exception as e:
            logger.error(f"❌ Erro crítico no tratamento de erro: {str(e)}")
    
    async def _mark_as_read_safe(self, phone: str, message_id: str):
        """Marca mensagem como lida de forma segura"""
        try:
            await self.whatsapp.mark_as_read(phone, message_id)
        except Exception as e:
            logger.warning(f"⚠️ Falha ao marcar como lida: {str(e)}")
    
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
    
    def _format_cpf_display(self, cpf: str) -> str:
        """Formata CPF para exibição"""
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    async def get_transaction_audit_log(self, phone: str, db: Session, limit: int = 5) -> Dict:
        """Busca log de auditoria das transações"""
        transactions = await self.transaction_service.get_transaction_history(phone, db, limit)
        
        return {
            "phone": phone,
            "total_transactions": len(transactions),
            "transactions": [
                {
                    "id": t.id,
                    "stage": t.stage_current.value,
                    "decision": t.decision_type.value,
                    "success": t.operation_success,
                    "timestamp": t.created_at.isoformat(),
                    "processing_time_ms": t.processing_time_ms
                }
                for t in transactions
            ]
        }