#!/usr/bin/env python3
"""
Teste simples para debugar o problema
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db

async def test_debug_simples():
    """Teste simples para debugar"""
    
    print("🧪 TESTE SIMPLES - DEBUG")
    print("=" * 30)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # Teste 1: Verificar se o banco mock funciona
        print("\n1️⃣ Teste do banco mock")
        print("-" * 20)
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Conversa inicial: {conversa.state}")
        
        # Alterar estado
        conversa.state = "teste"
        conversa.context = {"teste": "valor"}
        db.commit()
        
        # Buscar novamente
        conversa2 = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Conversa após alteração: {conversa2.state}")
        print(f"Contexto: {conversa2.context}")
        
        # Teste 2: Processar uma mensagem simples
        print("\n2️⃣ Teste de processamento")
        print("-" * 25)
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_debug_001",
            db=db
        )
        
        conversa3 = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após 'oi': {conversa3.state}")
        
        # Teste 3: Processar opção 1
        print("\n3️⃣ Teste opção 1")
        print("-" * 15)
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="1",
            message_id="test_debug_002",
            db=db
        )
        
        conversa4 = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após '1': {conversa4.state}")
        print(f"Contexto: {conversa4.context}")
        
        # Teste 4: Processar CPF
        print("\n4️⃣ Teste CPF")
        print("-" * 10)
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="12345678901",
            message_id="test_debug_003",
            db=db
        )
        
        conversa5 = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após CPF: {conversa5.state}")
        print(f"Contexto: {conversa5.context}")
        
        print("\n✅ TESTE SIMPLES CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_debug_simples()) 