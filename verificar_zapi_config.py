#!/usr/bin/env python3
"""
Script para verificar configuração do Z-API
"""

import asyncio
import httpx
from app.config import settings

async def verificar_zapi():
    """Verifica a configuração do Z-API"""
    print("🔍 Verificando configuração do Z-API...")
    
    # Verificar variáveis de ambiente
    print("\n📋 Variáveis de ambiente:")
    print(f"   ZAPI_BASE_URL: {settings.zapi_base_url}")
    print(f"   ZAPI_INSTANCE_ID: {settings.zapi_instance_id}")
    print(f"   ZAPI_TOKEN: {'***' if settings.zapi_token else 'NÃO CONFIGURADO'}")
    print(f"   ZAPI_CLIENT_TOKEN: {'***' if settings.zapi_client_token else 'NÃO CONFIGURADO'}")
    
    # Testar conexão com Z-API
    print("\n🌐 Testando conexão com Z-API...")
    
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Teste 1: Verificar status da instância
            print("\n1. Verificando status da instância...")
            try:
                response = await client.get(
                    f"{base_url}/status",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Instância conectada: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao verificar status: {e}")
            
            # Teste 2: Verificar webhook configurado
            print("\n2. Verificando webhook configurado...")
            try:
                response = await client.get(
                    f"{base_url}/webhook",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook configurado: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao verificar webhook: {e}")
            
            # Teste 3: Tentar enviar mensagem de teste
            print("\n3. Testando envio de mensagem...")
            try:
                test_payload = {
                    "phone": "553198600366@c.us",
                    "message": "Teste de conexão - Z-API",
                    "delayMessage": 0
                }
                
                response = await client.post(
                    f"{base_url}/send-text",
                    json=test_payload,
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Mensagem enviada: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao enviar mensagem: {e}")
            
            # Teste 4: Verificar QR Code (se necessário)
            print("\n4. Verificando QR Code...")
            try:
                response = await client.get(
                    f"{base_url}/qr-code",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ QR Code: {data}")
                else:
                    print(f"   ❌ Erro: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro ao verificar QR Code: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral na comunicação com Z-API: {e}")
    
    print("\n✅ Verificação do Z-API concluída!")

if __name__ == "__main__":
    asyncio.run(verificar_zapi()) 