#!/usr/bin/env python3
"""
Teste detalhado do fluxo de CPF
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db

async def test_fluxo_cpf_detalhado():
    """Testa detalhadamente o fluxo de CPF"""
    
    print("🧪 TESTE DETALHADO - FLUXO CPF")
    print("=" * 40)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # ===== TESTE 1: FLUXO OPÇÃO 1 - AGENDAR =====
        print("\n1️⃣ TESTE - OPÇÃO 1 (AGENDAR)")
        print("-" * 25)
        
        # Enviar "oi"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após 'oi': {conversa.state}")
        
        # Enviar "1"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="1",
            message_id="test_1_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após '1': {conversa.state}")
        print(f"Contexto: {conversa.context}")
        
        # Enviar CPF
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="12345678901",
            message_id="test_cpf_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após CPF: {conversa.state}")
        print(f"Contexto: {conversa.context}")
        
        # ===== TESTE 2: FLUXO OPÇÃO 2 - VER AGENDAMENTOS =====
        print("\n2️⃣ TESTE - OPÇÃO 2 (VER AGENDAMENTOS)")
        print("-" * 35)
        
        # Resetar conversa
        conversa.state = "inicio"
        conversa.context = {}
        
        # Enviar "oi"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_002",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após 'oi': {conversa.state}")
        
        # Enviar "2"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="2",
            message_id="test_2_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após '2': {conversa.state}")
        print(f"Contexto: {conversa.context}")
        
        # Enviar CPF
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="12345678901",
            message_id="test_cpf_002",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após CPF: {conversa.state}")
        print(f"Contexto: {conversa.context}")
        
        # ===== TESTE 3: CPF INVÁLIDO =====
        print("\n3️⃣ TESTE - CPF INVÁLIDO")
        print("-" * 20)
        
        # Resetar conversa
        conversa.state = "inicio"
        conversa.context = {}
        
        # Enviar "oi"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_003",
            db=db
        )
        
        # Enviar "1"
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="1",
            message_id="test_1_002",
            db=db
        )
        
        # Enviar CPF inválido
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="123",
            message_id="test_cpf_invalido_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após CPF inválido: {conversa.state}")
        
        print("\n✅ TESTE DETALHADO CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fluxo_cpf_detalhado()) 