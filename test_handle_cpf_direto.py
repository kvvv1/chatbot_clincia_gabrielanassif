#!/usr/bin/env python3
"""
Teste para chamar diretamente o método _handle_cpf
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db

async def test_handle_cpf_direto():
    """Testa chamar diretamente o método _handle_cpf"""
    
    print("🧪 TESTE DIRETO - _handle_cpf")
    print("=" * 35)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # Criar conversa com estado aguardando_cpf
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        conversa.state = "aguardando_cpf"
        conversa.context = {"acao": "agendar"}
        db.commit()
        
        print(f"Estado inicial: {conversa.state}")
        print(f"Contexto inicial: {conversa.context}")
        
        # Chamar diretamente o método _handle_cpf
        print("\nChamando _handle_cpf diretamente...")
        await conversation_manager._handle_cpf(
            phone=test_phone,
            message="12345678901",
            conversa=conversa,
            db=db
        )
        
        print(f"Estado após _handle_cpf: {conversa.state}")
        print(f"Contexto após _handle_cpf: {conversa.context}")
        
        print("\n✅ TESTE DIRETO CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_handle_cpf_direto()) 