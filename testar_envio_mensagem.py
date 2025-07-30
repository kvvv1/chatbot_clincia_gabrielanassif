#!/usr/bin/env python3
"""
Script para testar envio de mensagens e identificar problemas
"""

import asyncio
import httpx
import json
from datetime import datetime
from app.config import settings

async def testar_envio_mensagem():
    """Testa o envio de mensagens via Z-API"""
    print("🧪 Testando envio de mensagens...")
    
    # Configurações
    phone = "553198600366@c.us"  # Seu número de telefone
    message = "Teste de mensagem - " + datetime.now().strftime("%H:%M:%S")
    
    print(f"📱 Telefone: {phone}")
    print(f"💬 Mensagem: {message}")
    
    try:
        # URL base do Z-API
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        # Payload da mensagem
        payload = {
            "phone": phone,
            "message": message,
            "delayMessage": 0
        }
        
        print(f"\n🌐 URL: {base_url}/send-text")
        print(f"📋 Headers: {headers}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        async with httpx.AsyncClient() as client:
            # Teste 1: Verificar se a instância está conectada
            print("\n1. Verificando status da instância...")
            try:
                response = await client.get(
                    f"{base_url}/status",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Instância: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
                    return
            except Exception as e:
                print(f"   ❌ Erro ao verificar status: {e}")
                return
            
            # Teste 2: Enviar mensagem
            print("\n2. Enviando mensagem...")
            try:
                response = await client.post(
                    f"{base_url}/send-text",
                    json=payload,
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Mensagem enviada com sucesso!")
                    print(f"   📄 Resposta: {json.dumps(data, indent=2)}")
                else:
                    print(f"   ❌ Erro ao enviar mensagem:")
                    print(f"   📄 Resposta: {response.text}")
                    
                    # Tentar identificar o problema
                    if "Instance not found" in response.text:
                        print("   🔍 Problema: Instância não encontrada")
                        print("   💡 Solução: Verifique o ZAPI_INSTANCE_ID")
                    elif "Unauthorized" in response.text:
                        print("   🔍 Problema: Não autorizado")
                        print("   💡 Solução: Verifique ZAPI_TOKEN e ZAPI_CLIENT_TOKEN")
                    elif "phone" in response.text.lower():
                        print("   🔍 Problema: Formato de telefone inválido")
                        print("   💡 Solução: Verifique o formato do telefone")
                    
            except Exception as e:
                print(f"   ❌ Erro ao enviar mensagem: {e}")
            
            # Teste 3: Verificar mensagens enviadas
            print("\n3. Verificando mensagens enviadas...")
            try:
                response = await client.get(
                    f"{base_url}/chat-history",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Histórico: {len(data)} mensagens")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao verificar histórico: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    print("\n✅ Teste de envio concluído!")

async def testar_webhook_local():
    """Testa o webhook local"""
    print("\n🌐 Testando webhook local...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Teste 1: Verificar se o servidor está rodando
            print("\n1. Verificando servidor local...")
            try:
                response = await client.get("http://localhost:8000/")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Servidor local funcionando")
                else:
                    print(f"   ❌ Erro: {response.text}")
                    return
            except Exception as e:
                print(f"   ❌ Servidor não está rodando: {e}")
                print("   💡 Execute: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
                return
            
            # Teste 2: Testar webhook de mensagem
            print("\n2. Testando webhook de mensagem...")
            test_data = {
                "event": "message",
                "data": {
                    "id": "test_" + datetime.now().strftime("%H%M%S"),
                    "type": "text",
                    "from": "553198600366@c.us",
                    "fromMe": False,
                    "text": {
                        "body": "Teste via script"
                    }
                }
            }
            
            try:
                response = await client.post(
                    "http://localhost:8000/webhook/message",
                    json=test_data
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook processado: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao testar webhook: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral no teste local: {e}")

async def main():
    """Função principal"""
    print("🚀 Iniciando testes de mensagens...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testar envio via Z-API
    await testar_envio_mensagem()
    
    # Testar webhook local
    await testar_webhook_local()
    
    print("\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main()) 