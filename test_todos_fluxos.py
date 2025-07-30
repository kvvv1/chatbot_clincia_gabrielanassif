#!/usr/bin/env python3
"""
Teste abrangente de todos os fluxos do chatbot
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db

async def test_fluxo_completo():
    """Testa todos os fluxos do chatbot"""
    
    print("🧪 TESTE ABRANGENTE - TODOS OS FLUXOS")
    print("=" * 60)
    
    # Criar instância do ConversationManager
    conversation_manager = ConversationManager()
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    # Obter sessão do banco (mock)
    db = next(get_db())
    
    try:
        # ===== TESTE 1: FLUXO INICIAL =====
        print("\n1️⃣ TESTE - FLUXO INICIAL")
        print("-" * 30)
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após 'oi': {conversa.state}")
        
        # ===== TESTE 2: OPÇÃO 1 - AGENDAR CONSULTA =====
        print("\n2️⃣ TESTE - OPÇÃO 1 (AGENDAR CONSULTA)")
        print("-" * 40)
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="1",
            message_id="test_1_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após '1': {conversa.state}")
        print(f"✅ Contexto: {conversa.context}")
        
        # Simular CPF válido
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="52998224725",
            message_id="test_cpf_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após CPF: {conversa.state}")
        
        # ===== TESTE 3: OPÇÃO 2 - VER AGENDAMENTOS =====
        print("\n3️⃣ TESTE - OPÇÃO 2 (VER AGENDAMENTOS)")
        print("-" * 40)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_002",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="2",
            message_id="test_2_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após '2': {conversa.state}")
        print(f"✅ Contexto: {conversa.context}")
        
        # Simular CPF válido
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="52998224725",
            message_id="test_cpf_002",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após CPF: {conversa.state}")
        
        # ===== TESTE 4: OPÇÃO 3 - CANCELAR CONSULTA =====
        print("\n4️⃣ TESTE - OPÇÃO 3 (CANCELAR CONSULTA)")
        print("-" * 40)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_003",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="3",
            message_id="test_3_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após '3': {conversa.state}")
        print(f"✅ Contexto: {conversa.context}")
        
        # ===== TESTE 5: OPÇÃO 4 - LISTA DE ESPERA =====
        print("\n5️⃣ TESTE - OPÇÃO 4 (LISTA DE ESPERA)")
        print("-" * 40)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_004",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="4",
            message_id="test_4_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após '4': {conversa.state}")
        print(f"✅ Contexto: {conversa.context}")
        
        # ===== TESTE 6: OPÇÃO 5 - FALAR COM ATENDENTE =====
        print("\n6️⃣ TESTE - OPÇÃO 5 (FALAR COM ATENDENTE)")
        print("-" * 40)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_005",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="5",
            message_id="test_5_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após '5': {conversa.state}")
        
        # ===== TESTE 7: OPÇÕES INVÁLIDAS =====
        print("\n7️⃣ TESTE - OPÇÕES INVÁLIDAS")
        print("-" * 30)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_006",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="99",
            message_id="test_invalido_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após opção inválida: {conversa.state}")
        
        # ===== TESTE 8: CPF INVÁLIDO =====
        print("\n8️⃣ TESTE - CPF INVÁLIDO")
        print("-" * 25)
        
        # Resetar para início
        conversa.state = "inicio"
        conversa.context = {}
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="oi",
            message_id="test_oi_007",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="1",
            message_id="test_1_002",
            db=db
        )
        
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="123",
            message_id="test_cpf_invalido_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após CPF inválido: {conversa.state}")
        
        # ===== TESTE 9: NAVEGAÇÃO ENTRE ESTADOS =====
        print("\n9️⃣ TESTE - NAVEGAÇÃO ENTRE ESTADOS")
        print("-" * 35)
        
        # Testar voltar ao menu
        await conversation_manager.processar_mensagem(
            phone=test_phone,
            message="0",
            message_id="test_voltar_001",
            db=db
        )
        
        conversa = conversation_manager._get_or_create_conversation(test_phone, db)
        print(f"✅ Estado após voltar: {conversa.state}")
        
        print("\n✅ TESTE ABRANGENTE CONCLUÍDO!")
        print("\n📋 RESUMO DOS FLUXOS TESTADOS:")
        print("1. Fluxo inicial (oi)")
        print("2. Opção 1 - Agendar consulta")
        print("3. Opção 2 - Ver agendamentos")
        print("4. Opção 3 - Cancelar consulta")
        print("5. Opção 4 - Lista de espera")
        print("6. Opção 5 - Falar com atendente")
        print("7. Opções inválidas")
        print("8. CPF inválido")
        print("9. Navegação entre estados")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fluxo_completo()) 