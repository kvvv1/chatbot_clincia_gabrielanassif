#!/usr/bin/env python3
"""
Debug específico para problema de leitura do usuário
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_fallback_config():
    """Configurar fallback para quando não há .env"""
    from app.config import create_fallback_settings
    import app.config as config_module
    
    # Usar configurações fallback
    config_module.settings = create_fallback_settings()
    print("⚙️  Usando configurações fallback (SQLite)")

async def debug_leitura_completa():
    print("🔍 DEBUG - LEITURA DO USUÁRIO")
    print("=" * 50)
    
    setup_fallback_config()
    
    from app.models.database import get_db_session, Conversation
    from app.services.conversation import ConversationManager
    
    db = get_db_session()
    conversation_manager = ConversationManager()
    test_phone = "5531999999999@c.us"
    
    # LIMPAR ESTADO ANTERIOR
    print("1. 🧹 Limpando estados anteriores...")
    db.query(Conversation).filter_by(phone=test_phone).delete()
    db.commit()
    print("   ✅ Estados limpos")
    
    # TESTE 1: Primeira mensagem
    print("\n2. 📨 TESTE 1: Primeira mensagem 'oi'")
    await conversation_manager.processar_mensagem(test_phone, "oi", "msg1", db)
    
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   📋 Estado após 'oi': {conversa.state if conversa else 'NENHUM'}")
    print(f"   📋 Contexto: {conversa.context if conversa else 'NENHUM'}")
    
    if not conversa or conversa.state != "menu_principal":
        print("   ❌ PROBLEMA: Estado não mudou para menu_principal!")
        return
    
    # TESTE 2: Opção do menu
    print("\n3. 📨 TESTE 2: Resposta '1' (agendar)")
    print("   🎯 Estado ANTES da mensagem:")
    conversa_antes = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"      Estado: {conversa_antes.state}")
    print(f"      Contexto: {conversa_antes.context}")
    
    await conversation_manager.processar_mensagem(test_phone, "1", "msg2", db)
    
    print("   🎯 Estado DEPOIS da mensagem:")
    conversa_depois = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"      Estado: {conversa_depois.state}")
    print(f"      Contexto: {conversa_depois.context}")
    
    if conversa_depois.state == "aguardando_cpf" and conversa_depois.context.get("acao") == "agendar":
        print("   ✅ SUCESSO: Estado mudou corretamente!")
    else:
        print("   ❌ PROBLEMA: Estado não mudou corretamente!")
        print(f"      Esperado: estado='aguardando_cpf', acao='agendar'")
        print(f"      Recebido: estado='{conversa_depois.state}', contexto={conversa_depois.context}")
        
        # DIAGNÓSTICO DETALHADO
        print("\n   🔍 DIAGNÓSTICO:")
        
        # Verificar se a conversa está sendo encontrada
        print(f"      ID da conversa: {conversa_depois.id}")
        print(f"      Telefone: {conversa_depois.phone}")
        print(f"      Criado em: {conversa_depois.created_at}")
        print(f"      Atualizado em: {conversa_depois.updated_at}")
        
        return
    
    # TESTE 3: CPF
    print("\n4. 📨 TESTE 3: CPF '12345678901'")
    await conversation_manager.processar_mensagem(test_phone, "12345678901", "msg3", db)
    
    conversa_cpf = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   📋 Estado após CPF: {conversa_cpf.state}")
    print(f"   📋 Contexto: {conversa_cpf.context}")
    
    print("\n" + "=" * 50)
    print("🎯 RESULTADO:")
    
    if conversa_cpf.state == "aguardando_cpf":
        print("❌ PROBLEMA CONFIRMADO!")
        print("   O sistema está VOLTANDO PARA O MENU em vez de processar as opções!")
        print("   Isso indica problema no handler ou na lógica de estados.")
    else:
        print("✅ FUNCIONANDO!")
        print("   O sistema está processando as mensagens corretamente.")
    
    db.close()

async def debug_handlers_direto():
    print("\n\n🔧 DEBUG - HANDLERS DIRETOS")
    print("=" * 50)
    
    setup_fallback_config()
    
    from app.models.database import get_db_session, Conversation
    from app.services.conversation import ConversationManager
    
    db = get_db_session()
    manager = ConversationManager()
    test_phone = "5531888888888@c.us"
    
    # Criar conversa em estado específico
    print("1. 🎯 Criando conversa em estado 'menu_principal'...")
    
    # Limpar anterior
    db.query(Conversation).filter_by(phone=test_phone).delete()
    db.commit()
    
    # Criar nova
    conversa = Conversation(
        phone=test_phone,
        state="menu_principal",
        context={}
    )
    db.add(conversa)
    db.commit()
    
    print(f"   ✅ Conversa criada: ID {conversa.id}, Estado: {conversa.state}")
    
    # Testar handler direto
    print("\n2. 🔧 Testando handler menu_principal diretamente...")
    
    # Simular NLU result
    nlu_result = {"intent": "menu_option", "confidence": 0.9}
    
    try:
        await manager._handle_menu_principal(test_phone, "1", conversa, db, nlu_result)
        
        # Verificar resultado
        db.refresh(conversa)
        print(f"   📋 Estado após handler: {conversa.state}")
        print(f"   📋 Contexto após handler: {conversa.context}")
        
        if conversa.state == "aguardando_cpf":
            print("   ✅ HANDLER FUNCIONANDO!")
        else:
            print("   ❌ HANDLER COM PROBLEMA!")
            
    except Exception as e:
        print(f"   ❌ ERRO no handler: {str(e)}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    import asyncio
    
    try:
        asyncio.run(debug_leitura_completa())
        asyncio.run(debug_handlers_direto())
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()