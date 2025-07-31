#!/usr/bin/env python3
"""
Script para resetar o estado de um usuário específico no chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_config():
    from app.config import create_fallback_settings
    import app.config as config_module
    config_module.settings = create_fallback_settings()

async def resetar_estado_usuario():
    print("🔧 RESETANDO ESTADO DO USUÁRIO")
    print("=" * 50)
    
    setup_config()
    
    from app.services.conversation import ConversationManager
    from app.models.database import get_db, Conversation
    
    # Usar número do WhatsApp (pode ser passado como argumento)
    if len(sys.argv) > 1:
        phone_input = sys.argv[1]
        print(f"📱 Usando número fornecido: {phone_input}")
    else:
        phone_input = "5531995531183"  # Número padrão baseado no que você usou
        print(f"📱 Usando número padrão: {phone_input}")
    
    # Normalizar formato
    if not phone_input.endswith("@c.us"):
        if phone_input.startswith("55"):
            phone = f"{phone_input}@c.us"
        else:
            phone = f"55{phone_input}@c.us"
    else:
        phone = phone_input
    
    print(f"📱 Número formatado: {phone}")
    
    manager = ConversationManager()
    db = next(get_db())
    
    print("\n1. 🧹 Limpando estado anterior...")
    
    # Tentar limpar do cache do manager
    if hasattr(manager, 'conversation_cache'):
        if phone in manager.conversation_cache:
            del manager.conversation_cache[phone]
            print("   ✅ Cache do manager limpo")
    
    # Limpar do banco de dados
    try:
        if hasattr(db, 'conversations'):
            # Modo Mock - limpar lista
            original_len = len(db.conversations)
            db.conversations = [c for c in db.conversations if c.get('phone') != phone]
            removed = original_len - len(db.conversations)
            print(f"   ✅ {removed} registros removidos do Mock DB")
        else:
            # Banco real
            deleted = db.query(Conversation).filter_by(phone=phone).delete()
            db.commit()
            print(f"   ✅ {deleted} registros removidos do banco real")
    except Exception as e:
        print(f"   ⚠️ Erro ao limpar banco: {e}")
    
    print("\n2. 🔄 Criando estado limpo...")
    
    # Criar nova conversa limpa
    conversa = manager._get_or_create_conversation(phone, db)
    conversa.state = "inicio"
    conversa.context = {}
    
    # Salvar estado limpo
    try:
        if hasattr(db, 'commit'):
            db.commit()
        print("   ✅ Estado limpo criado")
    except:
        print("   ✅ Estado limpo criado (Mock)")
    
    print("\n3. ✅ RESET COMPLETO!")
    print(f"   📱 Usuário: {phone}")
    print(f"   🔄 Estado: {conversa.state}")
    print(f"   📋 Contexto: {conversa.context}")
    
    print("\n🎯 AGORA VOCÊ PODE:")
    print("   1. Enviar uma nova mensagem para o chatbot")
    print("   2. O fluxo deve começar do início")
    print("   3. Seguir normalmente: Menu → Opção → CPF → etc.")
    
    print("\n💡 DICAS:")
    print("   - Evite digitar '0' durante o fluxo")
    print("   - Digite apenas números das opções (1, 2, 3, 4, 5)")
    print("   - Se travar novamente, rode este script")

if __name__ == "__main__":
    import asyncio
    asyncio.run(resetar_estado_usuario())