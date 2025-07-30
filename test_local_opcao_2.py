#!/usr/bin/env python3
"""
Teste local para verificar o fluxo da opção 2 (ver agendamentos)
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db

async def test_fluxo_opcao_2_local():
    """Testa o fluxo da opção 2 localmente"""
    
    print("🧪 TESTE LOCAL - FLUXO OPÇÃO 2")
    print("=" * 50)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # Teste 1: Enviar "oi" para iniciar conversa
        print("\n1️⃣ Enviando 'oi' para iniciar conversa...")
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_001",
            db=db
        )
        print("✅ Teste 1 concluído")
        
        # Verificar estado da conversa
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após 'oi': {conversa.state}")
        
        # Teste 2: Enviar "2" para escolher ver agendamentos
        print("\n2️⃣ Enviando '2' para ver agendamentos...")
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="2",
            message_id="test_2_001",
            db=db
        )
        print("✅ Teste 2 concluído")
        
        # Verificar estado da conversa
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após '2': {conversa.state}")
        print(f"Contexto após '2': {conversa.context}")
        
        # Teste 3: Enviar CPF de teste
        print("\n3️⃣ Enviando CPF de teste...")
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="12345678901",
            message_id="test_cpf_001",
            db=db
        )
        print("✅ Teste 3 concluído")
        
        # Verificar estado da conversa
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"Estado após CPF: {conversa.state}")
        print(f"Contexto após CPF: {conversa.context}")
        
        print("\n✅ Teste local concluído!")
        print("\n📋 Resumo esperado:")
        print("- Teste 1 (oi): Estado deveria ser 'menu_principal'")
        print("- Teste 2 (2): Estado deveria ser 'aguardando_cpf' com ação 'visualizar'")
        print("- Teste 3 (CPF): Estado deveria ser 'visualizando_agendamentos'")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fluxo_opcao_2_local()) 