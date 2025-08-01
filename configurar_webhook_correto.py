#!/usr/bin/env python3
"""
Script para configurar webhook corretamente no Z-API
"""

import asyncio
import httpx
from app.config import settings

async def configurar_webhook_correto():
    """Configura o webhook corretamente no Z-API"""
    print("🔧 Configurando webhook corretamente no Z-API...")
    
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
            # Método 1: Tentar configurar webhook via POST
            print("\n1. Tentando configurar webhook via POST...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.post(
                    f"{base_url}/webhook",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Método 2: Tentar configurar webhook via PUT
            print("\n2. Tentando configurar webhook via PUT...")
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
            
            # Método 3: Tentar configurar webhook via PATCH
            print("\n3. Tentando configurar webhook via PATCH...")
            try:
                payload = {
                    "webhook": vercel_webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": False
                }
                
                response = await client.patch(
                    f"{base_url}/webhook",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Verificar configuração atual
            print("\n4. Verificando configuração atual...")
            try:
                response = await client.get(
                    f"{base_url}/webhook",
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Testar outros endpoints
            print("\n5. Testando outros endpoints...")
            endpoints = [
                "/webhook/set",
                "/webhook/configure",
                "/settings/webhook",
                "/config/webhook"
            ]
            
            for endpoint in endpoints:
                try:
                    payload = {
                        "webhook": vercel_webhook_url,
                        "webhookByEvents": True,
                        "webhookBase64": False
                    }
                    
                    response = await client.post(
                        f"{base_url}{endpoint}",
                        json=payload,
                        headers=headers
                    )
                    
                    print(f"   {endpoint}: {response.status_code}")
                    if response.status_code != 404:
                        print(f"      Resposta: {response.text}")
                        
                except Exception as e:
                    print(f"   {endpoint}: ❌ Erro - {e}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

async def verificar_documentacao_zapi():
    """Verifica a documentação do Z-API para entender como configurar webhook"""
    print("\n📚 Verificando documentação do Z-API...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Tentar acessar documentação
            urls = [
                "https://developer.z-api.io/",
                "https://api.z-api.io/docs",
                "https://app.z-api.io/docs"
            ]
            
            for url in urls:
                try:
                    response = await client.get(url, timeout=5.0)
                    print(f"   {url}: {response.status_code}")
                except Exception as e:
                    print(f"   {url}: ❌ Erro - {e}")
    
    except Exception as e:
        print(f"❌ Erro ao verificar documentação: {e}")

async def main():
    """Função principal"""
    print("🚀 Configurando webhook corretamente...")
    
    await configurar_webhook_correto()
    await verificar_documentacao_zapi()
    
    print("\n📋 Instruções manuais:")
    print("1. Acesse: https://app.z-api.io/")
    print("2. Vá para sua instância: VARIABLE_FROM_ENV")
    print("3. Configure manualmente o webhook para: https://chatbot-clincia.vercel.app/webhook")
    print("4. Ative os eventos: message, status, connection")

if __name__ == "__main__":
    asyncio.run(main()) 