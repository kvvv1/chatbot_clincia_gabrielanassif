#!/usr/bin/env python3
"""
Script para configurar webhook no Z-API para apontar para o Vercel
"""

import asyncio
import httpx
from app.config import settings

async def configurar_webhook_vercel():
    """Configura o webhook no Z-API para apontar para o Vercel"""
    print("🔧 Configurando webhook no Z-API para Vercel...")
    
    # URL do webhook no Vercel
    vercel_webhook_url = "https://chatbot-clincia.vercel.app/webhook"
    
    print(f"📍 URL do webhook: {vercel_webhook_url}")
    
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        # Payload para configurar webhook
        payload = {
            "webhook": vercel_webhook_url,
            "webhookByEvents": True,
            "webhookBase64": False
        }
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        print(f"🌐 URL base: {base_url}")
        print(f"📦 Payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            # Configurar webhook
            print("\n1. Configurando webhook...")
            try:
                response = await client.post(
                    f"{base_url}/webhook",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook configurado com sucesso!")
                    print(f"   📄 Resposta: {data}")
                else:
                    print(f"   ❌ Erro ao configurar webhook: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Erro na configuração: {e}")
                return False
            
            # Verificar se foi configurado
            print("\n2. Verificando configuração...")
            try:
                response = await client.get(
                    f"{base_url}/webhook",
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook verificado: {data}")
                    
                    if 'webhook' in data and vercel_webhook_url in data['webhook']:
                        print("   ✅ Webhook configurado corretamente para Vercel!")
                        return True
                    else:
                        print("   ⚠️  Webhook não está apontando para Vercel")
                        return False
                else:
                    print(f"   ❌ Erro ao verificar: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Erro na verificação: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

async def testar_webhook_vercel():
    """Testa o webhook no Vercel"""
    print("\n🧪 Testando webhook no Vercel...")
    
    vercel_webhook_url = "https://chatbot-clincia.vercel.app/webhook"
    
    try:
        async with httpx.AsyncClient() as client:
            # Teste 1: Verificar se o servidor está online
            print("\n1. Verificando se o servidor está online...")
            try:
                response = await client.get(
                    "https://chatbot-clincia.vercel.app/",
                    timeout=10.0
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Servidor Vercel online!")
                else:
                    print(f"   ❌ Servidor não respondeu corretamente: {response.text}")
                    return False
            except Exception as e:
                print(f"   ❌ Erro ao verificar servidor: {e}")
                return False
            
            # Teste 2: Testar webhook
            print("\n2. Testando webhook...")
            test_data = {
                "event": "message",
                "data": {
                    "id": "test_vercel",
                    "type": "text",
                    "from": "553198600366@c.us",
                    "fromMe": False,
                    "text": {
                        "body": "Teste de webhook Vercel"
                    }
                }
            }
            
            try:
                response = await client.post(
                    vercel_webhook_url,
                    json=test_data,
                    timeout=15.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook funcionando: {data}")
                    return True
                else:
                    print(f"   ❌ Erro no webhook: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Erro ao testar webhook: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        return False

async def main():
    """Função principal"""
    print("🚀 Configurando webhook para Vercel...")
    
    # Configurar webhook
    success = await configurar_webhook_vercel()
    
    if success:
        print("\n✅ Webhook configurado com sucesso!")
        
        # Testar webhook
        test_success = await testar_webhook_vercel()
        
        if test_success:
            print("\n🎉 TUDO FUNCIONANDO! Webhook configurado e testado com sucesso!")
            print("\n📋 Resumo:")
            print("   ✅ Webhook configurado no Z-API")
            print("   ✅ Webhook apontando para Vercel")
            print("   ✅ Servidor Vercel online")
            print("   ✅ Webhook respondendo corretamente")
            print("\n🚀 Sistema pronto para receber mensagens do WhatsApp!")
        else:
            print("\n⚠️  Webhook configurado, mas teste falhou")
            print("   Verifique se o deploy no Vercel foi feito corretamente")
    else:
        print("\n❌ Falha ao configurar webhook")
        print("   Verifique as credenciais do Z-API")

if __name__ == "__main__":
    asyncio.run(main()) 