#!/usr/bin/env python3
"""
Teste com CPF válido
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db
from app.utils.validators import ValidatorUtils

async def test_cpf_valido():
    """Testa com CPF válido"""
    
    print("🧪 TESTE - CPF VÁLIDO")
    print("=" * 25)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # Testar validação de CPF
        print("\n1️⃣ Teste de validação de CPF")
        print("-" * 30)
        
        cpf_invalido = "12345678901"
        cpf_valido = "52998224725"  # CPF válido de exemplo
        
        print(f"CPF inválido '{cpf_invalido}': {ValidatorUtils.validar_cpf(cpf_invalido)}")
        print(f"CPF válido '{cpf_valido}': {ValidatorUtils.validar_cpf(cpf_valido)}")
        
        # Testar fluxo com CPF válido
        print("\n2️⃣ Teste de fluxo com CPF válido")
        print("-" * 35)
        
        # Criar conversa com estado aguardando_cpf
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        conversa.state = "aguardando_cpf"
        conversa.context = {"acao": "agendar"}
        db.commit()
        
        print(f"Estado inicial: {conversa.state}")
        print(f"Contexto inicial: {conversa.context}")
        
        # Chamar diretamente o método _handle_cpf com CPF válido
        print("\nChamando _handle_cpf com CPF válido...")
        await conversation_manager._handle_cpf(
            phone=test_phone,
            message=cpf_valido,
            conversa=conversa,
            db=db
        )
        
        print(f"Estado após _handle_cpf: {conversa.state}")
        print(f"Contexto após _handle_cpf: {conversa.context}")
        
        print("\n✅ TESTE CPF VÁLIDO CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cpf_valido()) 