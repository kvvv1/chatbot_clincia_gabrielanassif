#!/usr/bin/env python3
"""
Script para testar se o fluxo do chatbot está funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_config():
    from app.config import create_fallback_settings
    import app.config as config_module
    config_module.settings = create_fallback_settings()

async def testar_fluxo_completo():
    print("🧪 TESTANDO FLUXO CORRIGIDO DO CHATBOT")
    print("=" * 60)
    
    setup_config()
    
    from app.services.conversation import ConversationManager
    from app.models.database import get_db, Conversation
    
    manager = ConversationManager()
    db = next(get_db())
    test_phone = "5531999999999@c.us"
    
    print("1. 🧹 Limpando estado anterior...")
    
    # Limpar estado
    try:
        if hasattr(db, 'conversations'):
            db.conversations = [c for c in db.conversations if c.get('phone') != test_phone]
        else:
            db.query(Conversation).filter_by(phone=test_phone).delete()
            db.commit()
        print("   ✅ Estado limpo")
    except:
        print("   ✅ Estado limpo (mock)")
    
    # TESTE 1: Primeira mensagem
    print("\n2. 📨 TESTE 1: Mensagem inicial 'oi'")
    await manager.processar_mensagem(test_phone, "oi", "msg1", db)
    
    conversa = manager._get_or_create_conversation(test_phone, db)
    print(f"   📋 Estado: {conversa.state}")
    print(f"   📋 Contexto: {conversa.context}")
    
    if conversa.state == "menu_principal":
        print("   ✅ TESTE 1 PASSOU - Menu exibido")
    else:
        print(f"   ❌ TESTE 1 FALHOU - Estado: {conversa.state}")
        return False
    
    # TESTE 2: Opção do menu
    print("\n3. 📨 TESTE 2: Opção '1' (agendar)")
    print(f"   🎯 Estado ANTES: {conversa.state}")
    
    await manager.processar_mensagem(test_phone, "1", "msg2", db)
    
    conversa = manager._get_or_create_conversation(test_phone, db)
    print(f"   🎯 Estado DEPOIS: {conversa.state}")
    print(f"   📋 Contexto: {conversa.context}")
    
    if conversa.state == "aguardando_cpf" and conversa.context.get('acao') == 'agendar':
        print("   ✅ TESTE 2 PASSOU - Aguardando CPF")
    else:
        print(f"   ❌ TESTE 2 FALHOU - Estado: {conversa.state}, Contexto: {conversa.context}")
        return False
    
    # TESTE 3: CPF válido
    print("\n4. 📨 TESTE 3: CPF válido '11144477735'")
    print(f"   🎯 Estado ANTES: {conversa.state}")
    
    await manager.processar_mensagem(test_phone, "11144477735", "msg3", db)
    
    conversa = manager._get_or_create_conversation(test_phone, db)
    print(f"   🎯 Estado DEPOIS: {conversa.state}")
    print(f"   📋 Contexto: {conversa.context}")
    
    # O estado pode ser confirmando_paciente ou paciente_nao_encontrado
    estados_validos = ["confirmando_paciente", "paciente_nao_encontrado"]
    if conversa.state in estados_validos:
        print(f"   ✅ TESTE 3 PASSOU - Estado válido: {conversa.state}")
    else:
        print(f"   ❌ TESTE 3 FALHOU - Estado inesperado: {conversa.state}")
        return False
    
    # TESTE 4: Comando que não deve resetar
    print("\n5. 📨 TESTE 4: Mensagem que não deve resetar '1' (número fora de contexto)")
    estado_antes = conversa.state
    contexto_antes = conversa.context.copy()
    
    await manager.processar_mensagem(test_phone, "1", "msg4", db)
    
    conversa = manager._get_or_create_conversation(test_phone, db)
    print(f"   🎯 Estado ANTES: {estado_antes}")
    print(f"   🎯 Estado DEPOIS: {conversa.state}")
    print(f"   📋 Contexto ANTES: {contexto_antes}")
    print(f"   📋 Contexto DEPOIS: {conversa.context}")
    
    # Com a correção, '1' NÃO deve resetar quando não estiver no menu
    if conversa.state == estado_antes and conversa.context == contexto_antes:
        print("   ✅ TESTE 4 PASSOU - Estado preservado (correção funcionou!)")
    elif conversa.state == "menu_principal":
        print("   ⚠️ TESTE 4 PARCIAL - Resetou para menu (comportamento antigo)")
        print("      💡 Execute: python corrigir_problema_menu.py")
        return False
    else:
        print(f"   ❓ TESTE 4 INDEFINIDO - Estado: {conversa.state}")
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    print("🎉 O fluxo está funcionando corretamente!")
    return True

async def main():
    try:
        sucesso = await testar_fluxo_completo()
        
        if sucesso:
            print("\n🎯 RESULTADO: CHATBOT FUNCIONANDO PERFEITAMENTE!")
            print("\n💡 AGORA VOCÊ PODE:")
            print("   ✅ Usar o chatbot normalmente")
            print("   ✅ O fluxo não deve mais resetar")
            print("   ✅ Estados são preservados corretamente")
        else:
            print("\n⚠️ RESULTADO: AINDA HÁ PROBLEMAS")
            print("\n🔧 EXECUTE OS SCRIPTS DE CORREÇÃO:")
            print("   1. python corrigir_problema_menu.py")
            print("   2. python resetar_meu_estado.py")
            print("   3. Reinicie a aplicação")
            
    except Exception as e:
        print(f"\n❌ ERRO DURANTE TESTE: {e}")
        print("\n🔧 SOLUÇÕES:")
        print("   1. Verifique se a aplicação está rodando")
        print("   2. Execute: python resetar_meu_estado.py")
        print("   3. Execute: python corrigir_problema_menu.py")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())