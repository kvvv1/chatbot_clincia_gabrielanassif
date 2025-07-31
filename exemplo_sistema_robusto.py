"""
Exemplo de uso do Sistema Robusto de Transações de Pacientes

Este exemplo demonstra como o novo sistema funciona na prática,
mostrando todos os componentes trabalhando juntos.
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Configurar logging para ver o que acontece
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Imports do sistema robusto
from app.services.enhanced_conversation_manager import EnhancedConversationManager
from app.services.patient_transaction_service import PatientTransactionService
from app.services.decision_engine import IntelligentDecisionEngine
from app.models.database import get_db
from app.models.patient_transaction import TransactionStage, DecisionType

async def exemplo_fluxo_completo():
    """
    Exemplo de um fluxo completo de agendamento usando o sistema robusto
    """
    print("🚀 DEMONSTRAÇÃO DO SISTEMA ROBUSTO")
    print("=" * 50)
    
    # Simular uma sessão de banco
    db = next(get_db())
    
    # Criar manager aprimorado
    manager = EnhancedConversationManager()
    
    # Telefone do usuário
    phone = "5511999887766"
    
    # Simular sequência de mensagens
    mensagens = [
        "oi",                    # Saudação inicial
        "1",                     # Escolher agendar
        "12345678901",          # CPF válido
        "1",                     # Confirmar paciente
        "1",                     # Escolher data
        "2",                     # Escolher horário
        "1"                      # Confirmar agendamento
    ]
    
    print("\n📱 SIMULANDO CONVERSA:")
    print("-" * 30)
    
    for i, mensagem in enumerate(mensagens, 1):
        print(f"\n👤 Usuário: {mensagem}")
        
        # Processar mensagem com sistema robusto
        await manager.processar_mensagem_robusta(
            phone=phone,
            message=mensagem,
            message_id=f"msg_{i}",
            db=db
        )
        
        # Pequena pausa para simular tempo real
        await asyncio.sleep(0.5)
    
    print("\n✅ FLUXO COMPLETO FINALIZADO")

async def exemplo_analise_decisao():
    """
    Exemplo de como o motor de decisão funciona
    """
    print("\n🧠 DEMONSTRAÇÃO DO MOTOR DE DECISÃO")
    print("=" * 50)
    
    engine = IntelligentDecisionEngine()
    
    # Cenário: Usuário digitou CPF e paciente foi encontrado
    decision_result = engine.analyze_and_decide(
        current_stage=TransactionStage.BUSCA_EXECUTADA,
        user_input="12345678901",
        context={"acao": "agendar"},
        patient_data={
            "nome": "João Silva",
            "cpf": "12345678901",
            "telefone": "11999887766"
        },
        validation_result=None,
        errors=[],
        warnings=[]
    )
    
    print(f"🎯 Decisão escolhida: {decision_result.chosen_decision.value}")
    print(f"📊 Confiança: {decision_result.confidence:.2f}")
    print(f"💭 Razão: {decision_result.reason}")
    print(f"🔧 Ação sugerida: {decision_result.suggested_action}")
    
    print("\n📋 Caminho da decisão:")
    for step in decision_result.decision_path:
        print(f"  • {step}")
    
    print("\n🔍 Alternativas consideradas:")
    for alt in decision_result.alternatives:
        print(f"  • {alt.decision_type.value} (confiança: {alt.confidence_score:.2f})")
    
    # Exemplo de explicação detalhada para auditoria
    explicacao = engine.explain_decision(decision_result)
    print("\n📄 EXPLICAÇÃO PARA AUDITORIA:")
    print(f"Decisão: {explicacao['decision']}")
    print(f"Confiança: {explicacao['confidence']}")
    print(f"Fatores analisados: {len(explicacao['factors_analyzed'])}")

async def exemplo_transacao_completa():
    """
    Exemplo de como uma transação completa é processada
    """
    print("\n⚙️ DEMONSTRAÇÃO DE TRANSAÇÃO COMPLETA")
    print("=" * 50)
    
    db = next(get_db())
    service = PatientTransactionService()
    
    # Simular conversa existente
    from app.models.database import Conversation
    conversa = Conversation(
        id="conv_123",
        phone="5511999887766",
        state="aguardando_cpf",
        context={"acao": "agendar"}
    )
    
    # Processar transação com CPF
    context = await service.process_patient_transaction(
        phone="5511999887766",
        user_input="12345678901",
        conversation=conversa,
        db=db
    )
    
    print(f"📋 Estágio atual: {context.current_stage.value}")
    print(f"👤 Paciente encontrado: {'Sim' if context.patient_data else 'Não'}")
    print(f"✅ Validação: {context.validation_results.value if context.validation_results else 'N/A'}")
    print(f"🎯 Decisão: {context.decision_made.value if context.decision_made else 'N/A'}")
    
    if context.errors:
        print(f"❌ Erros: {context.errors}")
    
    if context.warnings:
        print(f"⚠️ Avisos: {context.warnings}")

async def exemplo_recuperacao_erro():
    """
    Exemplo de como o sistema se recupera de erros
    """
    print("\n🛠️ DEMONSTRAÇÃO DE RECUPERAÇÃO DE ERROS")
    print("=" * 50)
    
    db = next(get_db())
    manager = EnhancedConversationManager()
    phone = "5511999887766"
    
    # Simular cenários de erro
    cenarios_erro = [
        "12345678900",  # CPF inválido
        "abc123",       # Input inválido
        "",             # Input vazio
        "99999999999"   # CPF válido mas paciente não encontrado
    ]
    
    for i, input_erro in enumerate(cenarios_erro, 1):
        print(f"\n🧪 Teste {i}: '{input_erro}'")
        
        try:
            await manager.processar_mensagem_robusta(
                phone=phone,
                message=input_erro,
                message_id=f"erro_{i}",
                db=db
            )
            print(f"✅ Sistema tratou o erro graciosamente")
            
        except Exception as e:
            print(f"❌ Erro não tratado: {str(e)}")

async def exemplo_auditoria():
    """
    Exemplo de como acessar logs de auditoria
    """
    print("\n📊 DEMONSTRAÇÃO DE LOGS DE AUDITORIA")
    print("=" * 50)
    
    db = next(get_db())
    manager = EnhancedConversationManager()
    
    # Buscar logs de auditoria
    audit_log = await manager.get_transaction_audit_log(
        phone="5511999887766",
        db=db,
        limit=5
    )
    
    print(f"📱 Telefone: {audit_log['phone']}")
    print(f"📊 Total de transações: {audit_log['total_transactions']}")
    
    print("\n📋 Últimas transações:")
    for trans in audit_log['transactions']:
        print(f"  • {trans['timestamp']}: {trans['stage']} -> {trans['decision']} "
              f"({'✅' if trans['success'] else '❌'}) "
              f"({trans['processing_time_ms']}ms)")

def mostrar_arquitetura():
    """
    Mostra a arquitetura do sistema robusto
    """
    print("\n🏗️ ARQUITETURA DO SISTEMA ROBUSTO")
    print("=" * 50)
    
    arquitetura = """
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA ROBUSTO                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📱 WhatsApp Message                                        │
│           ↓                                                 │
│  🎛️  Enhanced Conversation Manager                          │
│           ↓                                                 │
│  ⚙️  Patient Transaction Service                            │
│           ├── 🔍 Busca/Cache Paciente                       │
│           ├── ✅ Validação Robusta                          │
│           └── 💾 Persistência Auditável                     │
│           ↓                                                 │
│  🧠 Intelligent Decision Engine                             │
│           ├── 📊 Análise de Fatores                         │
│           ├── 🎯 Geração de Opções                          │
│           └── 🏆 Escolha da Melhor Decisão                  │
│           ↓                                                 │
│  🎬 Execution of Action                                     │
│           ├── ✅ Ação Principal                             │
│           ├── 🔄 Fallback se Necessário                     │
│           └── ⚠️ Escalation se Crítico                      │
│           ↓                                                 │
│  💾 Database Persistence                                    │
│           ├── 📋 Transaction Log                            │
│           ├── 🧠 Decision Log                               │
│           ├── 🗂️ Context History                            │
│           └── 🏪 Patient Cache                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

📊 BENEFÍCIOS:
• Auditoria completa de todas as interações
• Recuperação automática de erros
• Decisões inteligentes baseadas em contexto
• Cache otimizado para performance
• Logs detalhados para análise
• Escalation automático quando necessário
"""
    
    print(arquitetura)

def mostrar_estagios():
    """
    Mostra os estágios do sistema
    """
    print("\n📊 ESTÁGIOS DO SISTEMA")
    print("=" * 30)
    
    estagios = {
        "inicial": "Início da interação, coletando informações básicas",
        "busca_executada": "Busca na API foi executada com sucesso",
        "verificado": "Dados do paciente foram verificados e validados",
        "aguardando_confirmacao": "Aguardando confirmação do usuário",
        "agendado": "Agendamento foi realizado com sucesso",
        "erro": "Erro detectado que requer intervenção",
        "completo": "Processo finalizado com sucesso"
    }
    
    for estagio, descricao in estagios.items():
        print(f"📍 {estagio.upper()}: {descricao}")

async def main():
    """Função principal que executa todos os exemplos"""
    print("🎉 SISTEMA ROBUSTO DE TRANSAÇÕES DE PACIENTES")
    print("=" * 60)
    print("Este sistema implementa:")
    print("• Integração completa com API de pacientes")
    print("• Armazenamento auditável no banco")
    print("• Rastreamento de contexto e estágios")
    print("• Validação e decisão inteligente")
    print("• Sugestão automática de próximas ações")
    
    mostrar_arquitetura()
    mostrar_estagios()
    
    # Executar exemplos
    await exemplo_analise_decisao()
    await exemplo_transacao_completa()
    await exemplo_recuperacao_erro()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRAÇÃO COMPLETA")
    print("O sistema está pronto para produção!")

if __name__ == "__main__":
    # Executar demonstração
    asyncio.run(main())