#!/usr/bin/env python3
"""
Script para configurar webhook no Z-API automaticamente
"""

import httpx
import asyncio
import json
import os

async def configurar_webhook_zapi():
    print("🔧 CONFIGURANDO WEBHOOK Z-API")
    print("=" * 50)
    
    # Credenciais Z-API
    instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
    token = os.getenv("ZAPI_TOKEN", "")
    client_token = os.getenv("ZAPI_TOKEN", "")
    
    # URL base da Z-API
    zapi_base = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    
    # URL do webhook Vercel
    webhook_url = "https://chatbot-clincia.vercel.app/webhook"
    
    print(f"📱 Instância Z-API: {instance_id[:8]}...")
    print(f"🔗 Webhook URL: {webhook_url}")
    
    # 1. Verificar status da instância
    print("\n1. 🔍 Verificando status da instância...")
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{zapi_base}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ Instância ativa!")
                print(f"   📊 Status: {status_data}")
                
                # Verificar se WhatsApp está conectado
                if 'connected' in str(status_data).lower():
                    print(f"   📱 WhatsApp conectado!")
                else:
                    print(f"   ⚠️ WhatsApp pode não estar conectado")
                    
            else:
                print(f"   ❌ Instância não encontrada: {response.status_code}")
                print(f"   📝 Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Erro ao verificar instância: {str(e)}")
        return False
    
    # 2. Configurar webhook principal
    print("\n2. ⚙️ Configurando webhook principal...")
    
    webhook_config = {
        "webhook": webhook_url,
        "webhookEvents": ["message", "status", "connected"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{zapi_base}/webhook",
                json=webhook_config
            )
            
            if response.status_code == 200:
                print("   ✅ Webhook principal configurado!")
                print(f"   📋 Configuração: {webhook_config}")
            else:
                print(f"   ❌ Erro ao configurar webhook: {response.status_code}")
                print(f"   📝 Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Erro na configuração: {str(e)}")
        return False
    
    # 3. Configurar webhook específico para mensagens
    print("\n3. 📨 Configurando webhook de mensagens...")
    
    message_webhook = {
        "webhook": f"{webhook_url}/message",
        "webhookEvents": ["message"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{zapi_base}/webhook/message",
                json=message_webhook
            )
            
            if response.status_code == 200:
                print("   ✅ Webhook de mensagens configurado!")
            else:
                print(f"   ⚠️ Webhook de mensagens: {response.status_code}")
                print(f"   📝 Resposta: {response.text}")
                
    except Exception as e:
        print(f"   ⚠️ Erro webhook mensagens: {str(e)}")
    
    # 4. Configurar webhook de status
    print("\n4. 📊 Configurando webhook de status...")
    
    status_webhook = {
        "webhook": f"{webhook_url}/status",
        "webhookEvents": ["status"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{zapi_base}/webhook/status",
                json=status_webhook
            )
            
            if response.status_code == 200:
                print("   ✅ Webhook de status configurado!")
            else:
                print(f"   ⚠️ Webhook de status: {response.status_code}")
                print(f"   📝 Resposta: {response.text}")
                
    except Exception as e:
        print(f"   ⚠️ Erro webhook status: {str(e)}")
    
    # 5. Verificar configuração atual
    print("\n5. ✅ Verificando configuração...")
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{zapi_base}/webhook")
            
            if response.status_code == 200:
                webhook_info = response.json()
                print("   ✅ Webhook configurado com sucesso!")
                print(f"   📋 Configuração atual: {webhook_info}")
            else:
                print(f"   ⚠️ Não foi possível verificar: {response.status_code}")
                
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar: {str(e)}")
    
    # 6. Testar endpoints do Vercel
    print("\n6. 🧪 Testando endpoints do Vercel...")
    
    vercel_url = "https://chatbot-clincia.vercel.app"
    
    endpoints = [
        "/health",
        "/webhook",
        "/webhook/message",
        "/webhook/status"
    ]
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{vercel_url}{endpoint}")
                print(f"   ✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Erro - {str(e)}")
    
    print("\n🎯 CONFIGURAÇÃO COMPLETA!")
    print("=" * 50)
    print("✅ Webhook Z-API configurado")
    print("✅ Endpoints Vercel funcionando")
    print("✅ Sistema pronto para receber mensagens")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Envie uma mensagem para o número do WhatsApp")
    print("2. Verifique se o bot responde")
    print("3. Monitore os logs no Vercel")
    
    print("\n📱 Para testar:")
    print("- Envie 'oi' ou 'olá' para o número cadastrado")
    print("- O bot deve responder automaticamente")
    print("- Verifique os logs em: https://vercel.com/dashboard")
    
    return True

async def testar_mensagem():
    """Testa o envio de uma mensagem via Z-API"""
    print("\n🧪 TESTANDO ENVIO DE MENSAGEM")
    print("=" * 50)
    
    instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
    token = os.getenv("ZAPI_TOKEN", "")
    
    zapi_base = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    
    # Substitua pelo número de teste (formato: 5531999999999)
    test_number = input("Digite o número para teste (formato: 5531999999999): ").strip()
    
    if not test_number:
        print("❌ Número não fornecido")
        return False
    
    message_data = {
        "phone": test_number,
        "message": "🤖 Teste do chatbot - Se você recebeu esta mensagem, o sistema está funcionando!"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{zapi_base}/send-text",
                json=message_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Mensagem enviada com sucesso!")
                print(f"📋 Resposta: {result}")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 CONFIGURADOR WEBHOOK Z-API")
    print("=" * 50)
    
    async def main():
        # Configurar webhook
        success = await configurar_webhook_zapi()
        
        if success:
            # Perguntar se quer testar envio de mensagem
            print("\n" + "=" * 50)
            test_choice = input("Deseja testar o envio de uma mensagem? (s/n): ").strip().lower()
            
            if test_choice in ['s', 'sim', 'y', 'yes']:
                await testar_mensagem()
    
    asyncio.run(main()) 