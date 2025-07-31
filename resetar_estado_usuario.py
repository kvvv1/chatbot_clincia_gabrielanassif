#!/usr/bin/env python3
"""
Script para resetar o estado de um usuário específico
Use quando o chatbot não estiver respondendo adequadamente
"""

import asyncio
from app.services.conversation import ConversationManager
from app.models.database import get_db

async def resetar_estado_usuario():
    """Reseta o estado de um usuário específico"""
    
    print("🔧 RESETANDO ESTADO DO USUÁRIO")
    print("=" * 50)
    
    # Solicitar número do usuário
    phone = input("📱 Digite o número do telefone (com DDD, ex: 11999887766): ").strip()
    
    if not phone:
        print("❌ Número não fornecido")
        return
    
    # Formatar telefone
    phone_clean = ''.join(filter(str.isdigit, phone))
    if not phone_clean.startswith('55'):
        phone_clean = '55' + phone_clean
    
    print(f"📱 Resetando estado para: {phone_clean}")
    
    try:
        manager = ConversationManager()
        db = get_db()
        
        # Buscar conversa existente
        conversa = manager._get_or_create_conversation(phone_clean, db)
        
        print(f"🔍 Estado atual: {conversa.state}")
        print(f"📋 Contexto atual: {conversa.context}")
        
        # Resetar para estado inicial
        conversa.state = "inicio"
        conversa.context = {}
        db.commit()
        
        print("✅ Estado resetado para 'inicio'")
        print("✅ Contexto limpo")
        print("✅ Mudanças salvas no banco")
        
        # Verificar se foi resetado
        db.refresh(conversa)
        print(f"🔍 Novo estado: {conversa.state}")
        print(f"📋 Novo contexto: {conversa.context}")
        
        print("\n" + "=" * 50)
        print("🎉 RESET CONCLUÍDO COM SUCESSO!")
        print("📱 Agora o usuário pode enviar 'oi' novamente")
        print("🤖 O chatbot responderá com o menu principal")
        
        # Teste opcional
        teste = input("\n🧪 Quer testar o 'oi' agora? (s/n): ").strip().lower()
        if teste in ['s', 'sim', 'y', 'yes']:
            print("\n⏳ Testando processamento de 'oi'...")
            await manager.processar_mensagem(phone_clean, "oi", "test_reset", db)
            
            # Verificar resultado
            conversa = manager._get_or_create_conversation(phone_clean, db)
            print(f"✅ Estado após teste: {conversa.state}")
            print(f"📋 Contexto após teste: {conversa.context}")
            
            if conversa.state == "menu_principal":
                print("🎉 FUNCIONANDO! Menu foi exibido corretamente")
            else:
                print("⚠️ Algo ainda não está correto")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(resetar_estado_usuario())