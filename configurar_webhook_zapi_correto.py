#!/usr/bin/env python3
"""
Script para configurar webhook usando a API correta do Z-API
"""

import asyncio
import httpx
from app.config import settings

async def configurar_webhook_zapi():
    """Configura o webhook usando a API correta do Z-API"""
    print("🔧 Configurando webhook usando API correta do Z-API...")
    
    # URL do webhook no Vercel
    vercel_webhook_url = "https://chatbot-clincia.vercel.app/webhook"
    
    print(f"📍 URL do webhook: {vercel_webhook_url}")
    
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        print(f"🌐 URL base: {base_url}")
        
        async with httpx.AsyncClient() as client:
            # Método 1: Tentar configurar webhook via settings
            print("\n1. Tentando configurar webhook via settings...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.post(
                    f"{base_url}/settings",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Método 2: Tentar configurar webhook via config
            print("\n2. Tentando configurar webhook via config...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.post(
                    f"{base_url}/config",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Método 3: Tentar configurar webhook via webhook/set
            print("\n3. Tentando configurar webhook via webhook/set...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.post(
                    f"{base_url}/webhook/set",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Método 4: Tentar configurar webhook via webhook/configure
            print("\n4. Tentando configurar webhook via webhook/configure...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.post(
                    f"{base_url}/webhook/configure",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Método 5: Tentar configurar webhook via PUT
            print("\n5. Tentando configurar webhook via PUT...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.put(
                    f"{base_url}/webhook",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Verificar configuração atual
            print("\n6. Verificando configuração atual...")
            try:
                response = await client.get(
                    f"{base_url}/webhook",
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

async def verificar_documentacao_zapi():
    """Verifica a documentação do Z-API"""
    print("\n📚 Verificando documentação do Z-API...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Tentar acessar documentação
            urls = [
                "https://developer.z-api.io/",
                "https://api.z-api.io/docs",
                "https://app.z-api.io/docs",
                "https://z-api.io/docs"
            ]
            
            for url in urls:
                try:
                    response = await client.get(url, timeout=5.0)
                    print(f"   {url}: {response.status_code}")
                except Exception as e:
                    print(f"   {url}: ❌ Erro - {e}")
    
    except Exception as e:
        print(f"❌ Erro ao verificar documentação: {e}")

async def testar_endpoints_zapi():
    """Testa diferentes endpoints da API do Z-API"""
    print("\n🧪 Testando endpoints da API do Z-API...")
    
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Lista de endpoints para testar
            endpoints = [
                "/",
                "/status",
                "/connection",
                "/settings",
                "/config",
                "/webhook",
                "/webhook/set",
                "/webhook/configure",
                "/webhook/status",
                "/webhook/info"
            ]
            
            for endpoint in endpoints:
                try:
                    response = await client.get(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        timeout=5.0
                    )
                    
                    print(f"   {endpoint}: {response.status_code}")
                    if response.status_code != 404:
                        print(f"      Resposta: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"   {endpoint}: ❌ Erro - {e}")
    
    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")

async def main():
    """Função principal"""
    print("🚀 Configurando webhook usando API correta do Z-API...")
    
    await configurar_webhook_zapi()
    await testar_endpoints_zapi()
    await verificar_documentacao_zapi()
    
    print("\n📋 Instruções manuais:")
    print("1. Acesse: https://app.z-api.io/")
    print("2. Vá para sua instância: 3E4F7360B552F0C2DBCB9E6774402775")
    print("3. Na aba 'Webhook' ou 'Configurações', configure:")
    print("   - URL: https://chatbot-clincia.vercel.app/webhook")
    print("   - Ativar todos os eventos")
    print("   - Ativar 'Notificar as enviadas por mim também'")
    print("4. Salve as configurações")

if __name__ == "__main__":
    asyncio.run(main()) 