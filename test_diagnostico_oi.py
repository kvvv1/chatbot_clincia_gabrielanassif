#!/usr/bin/env python3
"""
Script de diagnóstico para o problema com mensagem "oi"
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.models.database import get_db, Conversation
from app.config import settings

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'diagnostico_oi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_mensagem_oi():
    """Testa especificamente o processamento da mensagem 'oi'"""
    
    print("🔍 === DIAGNÓSTICO MENSAGEM 'OI' ===")
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🏥 Clinic Name: {settings.clinic_name}")
    print()
    
    try:
        # 1. Testar inicialização do ConversationManager
        print("1️⃣ Testando inicialização do ConversationManager...")
        conversation_manager = ConversationManager()
        print("✅ ConversationManager inicializado com sucesso")
        print()
        
        # 2. Testar NLU Processor
        print("2️⃣ Testando NLU Processor...")
        nlu_result = conversation_manager.nlu.process_message("oi")
        print(f"✅ NLU Result: {nlu_result}")
        print()
        
        # 3. Testar WhatsApp Service
        print("3️⃣ Testando WhatsApp Service...")
        print(f"✅ WhatsApp Service inicializado: {conversation_manager.whatsapp}")
        print()
        
        # 4. Testar banco de dados
        print("4️⃣ Testando conexão com banco de dados...")
        db = get_db()
        print("✅ Conexão com banco estabelecida")
        print()
        
        # 5. Testar criação de conversa
        print("5️⃣ Testando criação de conversa...")
        phone = "5511999999999"  # Número de teste
        conversa = conversation_manager._get_or_create_conversation(phone, db)
        print(f"✅ Conversa criada/encontrada: {conversa.id}")
        print(f"   Estado: {conversa.state}")
        print(f"   Contexto: {conversa.context}")
        print()
        
        # 6. Testar processamento completo
        print("6️⃣ Testando processamento completo da mensagem 'oi'...")
        
        # Simular dados do webhook
        message_data = {
            "phone": phone,
            "text": {"message": "oi"},
            "messageId": "test_message_id_123",
            "fromMe": False
        }
        
        # Processar mensagem
        await conversation_manager.processar_mensagem(
            phone=phone,
            message="oi",
            message_id="test_message_id_123",
            db=db
        )
        
        print("✅ Processamento concluído sem erros!")
        print()
        
        # 7. Verificar estado final
        print("7️⃣ Verificando estado final...")
        db.refresh(conversa)
        print(f"✅ Estado final: {conversa.state}")
        print(f"✅ Contexto final: {conversa.context}")
        print()
        
        print("🎉 === DIAGNÓSTICO CONCLUÍDO COM SUCESSO ===")
        
    except Exception as e:
        print(f"❌ ERRO NO DIAGNÓSTICO: {str(e)}")
        print(f"📋 Tipo do erro: {type(e).__name__}")
        print(f"🔍 Stack trace:")
        import traceback
        traceback.print_exc()
        
        # Tentar identificar o problema específico
        if "import" in str(e).lower():
            print("\n🔧 PROBLEMA IDENTIFICADO: Erro de importação")
            print("   Verifique se todos os módulos estão disponíveis")
        elif "database" in str(e).lower() or "connection" in str(e).lower():
            print("\n🔧 PROBLEMA IDENTIFICADO: Erro de banco de dados")
            print("   Verifique a configuração do Supabase")
        elif "whatsapp" in str(e).lower() or "zapi" in str(e).lower():
            print("\n🔧 PROBLEMA IDENTIFICADO: Erro do WhatsApp/Z-API")
            print("   Verifique as configurações do Z-API")
        else:
            print("\n🔧 PROBLEMA IDENTIFICADO: Erro genérico")
            print("   Verifique os logs para mais detalhes")

async def test_webhook_simulation():
    """Simula o processamento do webhook"""
    
    print("\n🔍 === TESTE SIMULAÇÃO WEBHOOK ===")
    
    try:
        from app.handlers.webhook import process_message_event
        
        # Dados simulados do webhook
        webhook_data = {
            "type": "ReceivedCallback",
            "phone": "5511999999999@c.us",
            "text": {"message": "oi"},
            "messageId": "webhook_test_123",
            "fromMe": False
        }
        
        print("📥 Processando dados do webhook...")
        await process_message_event(webhook_data)
        print("✅ Webhook processado com sucesso!")
        
    except Exception as e:
        print(f"❌ ERRO NO WEBHOOK: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico do chatbot...")
    print("=" * 50)
    
    # Executar testes
    asyncio.run(test_mensagem_oi())
    asyncio.run(test_webhook_simulation())
    
    print("\n" + "=" * 50)
    print("🏁 Diagnóstico finalizado!") 