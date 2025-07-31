#!/usr/bin/env python3
"""
Debug do problema de menu - verifica estados da conversa
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import get_db_session, Conversation
from app.services.conversation import ConversationManager
import asyncio

async def debug_menu_problema():
    print("🔍 DEBUG - Problema do Menu Principal")
    print("=" * 50)
    
    # Configurar
    db = get_db_session()
    conversation_manager = ConversationManager()
    test_phone = "5531999999999@c.us"
    
    print(f"📱 Telefone de teste: {test_phone}")
    
    # Limpar conversas anteriores para este teste
    print("\n1. 🧹 Limpando conversas anteriores...")
    db.query(Conversation).filter_by(phone=test_phone).delete()
    db.commit()
    print("   ✅ Conversas limpas")
    
    # TESTE 1: Primeira mensagem (deve criar conversa e mostrar menu)
    print("\n2. 📨 Primeira mensagem: 'oi'")
    await conversation_manager.processar_mensagem(test_phone, "oi", "msg1", db)
    
    # Verificar estado após primeira mensagem
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   Estado após 'oi': {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    # TESTE 2: Segunda mensagem (deve processar opção do menu)
    print("\n3. 📨 Segunda mensagem: '1'")
    await conversation_manager.processar_mensagem(test_phone, "1", "msg2", db)
    
    # Verificar estado após segunda mensagem
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   Estado após '1': {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    # TESTE 3: Terceira mensagem (deve processar CPF)
    print("\n4. 📨 Terceira mensagem: '2'")
    await conversation_manager.processar_mensagem(test_phone, "2", "msg3", db)
    
    # Verificar estado após terceira mensagem
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   Estado após '2': {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    # TESTE 4: Mensagem com comando global
    print("\n5. 📨 Comando global: 'menu'")
    await conversation_manager.processar_mensagem(test_phone, "menu", "msg4", db)
    
    # Verificar estado após comando global
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   Estado após 'menu': {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    # TESTE 5: Tentar novamente opção 1
    print("\n6. 📨 Tentativa '1' novamente")
    await conversation_manager.processar_mensagem(test_phone, "1", "msg5", db)
    
    # Verificar estado final
    conversa = db.query(Conversation).filter_by(phone=test_phone).first()
    print(f"   Estado final: {conversa.state}")
    print(f"   Contexto final: {conversa.context}")
    
    print("\n" + "=" * 50)
    print("🎯 ANÁLISE:")
    
    if conversa.state == "aguardando_cpf" and conversa.context.get("acao") == "agendar":
        print("✅ FUNCIONANDO CORRETAMENTE!")
        print("   O menu está processando as opções normalmente.")
    else:
        print("❌ PROBLEMA IDENTIFICADO!")
        print("   O menu não está processando as opções.")
        print(f"   Estado esperado: aguardando_cpf")
        print(f"   Estado atual: {conversa.state}")
        print(f"   Contexto esperado: {{'acao': 'agendar'}}")
        print(f"   Contexto atual: {conversa.context}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(debug_menu_problema())