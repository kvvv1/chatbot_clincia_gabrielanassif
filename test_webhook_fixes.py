#!/usr/bin/env python3
"""
Script de teste para verificar as correções dos problemas de webhook
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"  # Ajuste conforme necessário

async def test_webhook_endpoints():
    """Testa os endpoints do webhook"""
    print("🧪 Testando endpoints do webhook...")
    
    async with httpx.AsyncClient() as client:
        
        # Teste 1: GET /webhook/ (health)
        print("\n1. Testando GET /webhook/")
        try:
            response = await client.get(f"{BASE_URL}/webhook/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 2: POST /webhook/message
        print("\n2. Testando POST /webhook/message")
        try:
            test_data = {
                "event": "message",
                "data": {
                    "id": "test_123",
                    "type": "text",
                    "from": "553198600366@c.us",
                    "fromMe": False,
                    "text": {
                        "body": "1"
                    }
                }
            }
            response = await client.post(
                f"{BASE_URL}/webhook/message",
                json=test_data
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: POST /webhook/status
        print("\n3. Testando POST /webhook/status")
        try:
            status_data = {
                "event": "status",
                "data": {
                    "id": "test_123",
                    "status": "delivered"
                }
            }
            response = await client.post(
                f"{BASE_URL}/webhook/status",
                json=status_data
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 4: GET /webhook/status-info (novo endpoint)
        print("\n4. Testando GET /webhook/status-info")
        try:
            response = await client.get(f"{BASE_URL}/webhook/status-info")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 5: Rota não mapeada (fallback)
        print("\n5. Testando rota não mapeada (fallback)")
        try:
            response = await client.post(
                f"{BASE_URL}/webhook/rota-inexistente",
                json={"test": "data"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

async def test_conversation_manager():
    """Testa o ConversationManager com MockQuery"""
    print("\n🧪 Testando ConversationManager...")
    
    try:
        from app.services.conversation import ConversationManager
        from app.models.database import get_db
        
        # Obter database mock
        db = next(get_db())
        
        # Criar ConversationManager
        manager = ConversationManager()
        
        # Testar _get_or_create_conversation
        print("   Testando _get_or_create_conversation...")
        conversa = manager._get_or_create_conversation("553198600366@c.us", db)
        print(f"   ✅ Conversa criada: {conversa.phone}")
        
        print("   ✅ ConversationManager funcionando com MockQuery")
        
    except Exception as e:
        print(f"   ❌ Erro no ConversationManager: {e}")

async def test_main_endpoints():
    """Testa endpoints principais"""
    print("\n🧪 Testando endpoints principais...")
    
    async with httpx.AsyncClient() as client:
        
        # Teste 1: GET /
        print("\n1. Testando GET /")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 2: GET /health
        print("\n2. Testando GET /health")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

async def main():
    """Função principal"""
    print("🚀 Iniciando testes das correções...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testar endpoints principais
    await test_main_endpoints()
    
    # Testar ConversationManager
    await test_conversation_manager()
    
    # Testar endpoints do webhook
    await test_webhook_endpoints()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main()) 