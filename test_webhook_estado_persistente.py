"""
Teste crítico: Verifica se o estado é mantido entre mensagens via webhook
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.handlers.webhook import get_conversation_manager, process_message_event
from app.models.database import get_db, Conversation
from datetime import datetime

async def test_estado_persistente_webhook():
    """Testa se o estado persiste entre chamadas do webhook"""
    
    print("🚨 TESTE CRÍTICO: Estado Persistente no Webhook")
    print("=" * 60)
    
    # Usar o manager global (como o webhook faz)
    manager = get_conversation_manager()
    db = next(get_db())
    phone = "5511999888777"
    
    # Limpar conversas antigas
    try:
        conv_antiga = db.query(Conversation).filter_by(phone=phone).first()
        if conv_antiga:
            db.delete(conv_antiga)
            db.commit()
    except:
        pass
    
    # Mock da API
    paciente_mock = {
        "nome": "João Silva",
        "cpf": "11144477735",
        "id": "123"
    }
    async def api_paciente_mock(cpf):
        return paciente_mock
    manager.gestaods.buscar_paciente_cpf = api_paciente_mock
    
    print("🔧 Testando instância global do ConversationManager...")
    print(f"   Manager ID: {id(manager)}")
    
    # Teste 1: Primeira mensagem
    print("\n1️⃣ PRIMEIRA MENSAGEM: 'oi'")
    print("-" * 40)
    await manager.processar_mensagem(phone, "oi", "msg1", db)
    
    # Verificar estado
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ ID da conversa: {conversa.id}")
    assert conversa.state == "menu_principal", f"Estado deveria ser 'menu_principal', mas é '{conversa.state}'"
    
    # Teste 2: Segunda mensagem - USAR MESMA INSTÂNCIA
    print("\n2️⃣ SEGUNDA MENSAGEM: '1' (Agendar)")
    print("-" * 40)
    
    # Verificar se é a mesma instância
    manager2 = get_conversation_manager()
    print(f"   🔍 Manager ID 2: {id(manager2)}")
    print(f"   ✅ Mesma instância? {id(manager) == id(manager2)}")
    assert id(manager) == id(manager2), "Deve ser a mesma instância!"
    
    await manager2.processar_mensagem(phone, "1", "msg2", db)
    
    # Verificar estado
    conversa = manager2._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    assert conversa.state == "aguardando_cpf", f"Estado deveria ser 'aguardando_cpf', mas é '{conversa.state}'"
    assert conversa.context.get('acao') == 'agendar', "Contexto deve manter ação 'agendar'"
    
    # Teste 3: Terceira mensagem - CPF
    print("\n3️⃣ TERCEIRA MENSAGEM: CPF")
    print("-" * 40)
    
    manager3 = get_conversation_manager()
    print(f"   🔍 Manager ID 3: {id(manager3)}")
    assert id(manager) == id(manager3), "Deve ser a mesma instância!"
    
    await manager3.processar_mensagem(phone, "11144477735", "msg3", db)
    
    # Verificar estado
    conversa = manager3._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    
    # Verificar se chegou na confirmação
    if conversa.state == "confirmando_paciente":
        print("   ✅ SUCESSO! Chegou na confirmação do paciente!")
        assert 'paciente_temp' in conversa.context, "Deve ter paciente_temp no contexto"
        
        # Teste 4: Confirmação
        print("\n4️⃣ QUARTA MENSAGEM: '1' (Confirmar)")
        print("-" * 40)
        
        manager4 = get_conversation_manager()
        assert id(manager) == id(manager4), "Deve ser a mesma instância!"
        
        await manager4.processar_mensagem(phone, "1", "msg4", db)
        
        conversa = manager4._get_or_create_conversation(phone, db)
        print(f"   ✅ Estado final: {conversa.state}")
        print(f"   ✅ Contexto final: {conversa.context}")
        
        # Deve ter paciente confirmado
        assert 'paciente' in conversa.context, "Paciente deve estar confirmado"
        assert 'paciente_temp' not in conversa.context, "paciente_temp deve ter sido removido"
        
        print("   ✅ FLUXO COMPLETO FUNCIONANDO!")
    else:
        print(f"   ❌ Estado inesperado: {conversa.state}")
        raise AssertionError(f"Estado deveria ser 'confirmando_paciente', mas é '{conversa.state}'")
    
    print("\n" + "=" * 60)
    print("✅ TESTE DE ESTADO PERSISTENTE PASSOU!")
    print("✅ Instância global do ConversationManager FUNCIONANDO!")
    print("✅ Estados mantidos entre mensagens!")

async def test_problema_anterior():
    """Demonstra como era o problema anterior"""
    
    print("\n📋 DEMONSTRAÇÃO: Como era o problema anterior")
    print("=" * 60)
    
    from app.services.conversation import ConversationManager
    
    # Simular o problema anterior (cada mensagem = nova instância)
    manager1 = ConversationManager()
    manager2 = ConversationManager()
    manager3 = ConversationManager()
    
    print(f"❌ Manager 1 ID: {id(manager1)}")
    print(f"❌ Manager 2 ID: {id(manager2)}")
    print(f"❌ Manager 3 ID: {id(manager3)}")
    
    print(f"   Instâncias diferentes? {id(manager1) != id(manager2) != id(manager3)}")
    print("   ❌ Isso causava perda de cache e inconsistências!")
    
    # Comparar com solução atual
    global1 = get_conversation_manager()
    global2 = get_conversation_manager()
    global3 = get_conversation_manager()
    
    print(f"\n✅ Global 1 ID: {id(global1)}")
    print(f"✅ Global 2 ID: {id(global2)}")
    print(f"✅ Global 3 ID: {id(global3)}")
    
    print(f"   Mesma instância? {id(global1) == id(global2) == id(global3)}")
    print("   ✅ Agora mantém cache e consistência!")

if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTE CRÍTICO DO WEBHOOK\n")
    
    try:
        # Teste principal
        asyncio.run(test_estado_persistente_webhook())
        
        # Demonstração do problema
        asyncio.run(test_problema_anterior())
        
        print("\n🎉 PROBLEMA DO WEBHOOK RESOLVIDO!")
        print("📝 Estados agora são mantidos corretamente!")
        print("🔧 Instância global funcionando perfeitamente!")
        
    except AssertionError as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        print("⚠️  O problema do webhook ainda existe!")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()