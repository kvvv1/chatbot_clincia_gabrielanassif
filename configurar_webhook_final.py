#!/usr/bin/env python3
"""
Configuração final do webhook com URL do Vercel conhecida
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

# URL do Vercel confirmada
VERCEL_URL = "https://chatbot-clincia.vercel.app"
WEBHOOK_URL = f"{VERCEL_URL}/webhook"

async def verificar_aplicacao_vercel():
    print("🔍 VERIFICANDO APLICAÇÃO VERCEL")
    print("=" * 50)
    
    print(f"1. 🌐 URL: {VERCEL_URL}")
    
    # Testar health check
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{VERCEL_URL}/webhook/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Aplicação online!")
                print(f"   📊 Status: {data.get('status')}")
                print(f"   🌍 Environment: {data.get('environment')}")
                print(f"   📅 Deploy: {data.get('deploy_version')}")
                return True
            else:
                print(f"   ❌ Health check falhou: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Erro ao acessar aplicação: {str(e)}")
        return False

async def configurar_webhook_zapi():
    print("\n\n📱 CONFIGURANDO WEBHOOK Z-API")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # Verificar credenciais
        if not settings.zapi_instance_id or not settings.zapi_token:
            print("❌ Credenciais Z-API não configuradas!")
            print("💡 Configure no arquivo .env:")
            print("   ZAPI_INSTANCE_ID=sua_instance")
            print("   ZAPI_TOKEN=seu_token")
            return False
        
        print(f"1. 📱 Instância Z-API: {settings.zapi_instance_id[:8]}...")
        print(f"2. 🔗 Webhook URL: {WEBHOOK_URL}")
        
        # Construir URL da Z-API
        zapi_base = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        # Verificar status da instância
        print("\n3. 🔍 Verificando instância Z-API...")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{zapi_base}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Instância ativa!")
                    if 'connected' in str(status_data).lower():
                        print(f"   📱 WhatsApp conectado!")
                    else:
                        print(f"   ⚠️ Verificar conexão WhatsApp")
                    print(f"   📊 Status: {status_data}")
                else:
                    print(f"   ❌ Instância não encontrada: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro ao verificar instância: {str(e)}")
            return False
        
        # Configurar webhook
        print("\n4. ⚙️ Configurando webhook...")
        
        webhook_config = {
            "webhook": WEBHOOK_URL,
            "webhookEvents": ["message", "status", "received"]
        }
        
        print(f"   📋 Configuração: {webhook_config}")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{zapi_base}/webhook",
                    json=webhook_config
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook configurado com sucesso!")
                    result = response.json()
                    print(f"   📋 Resultado: {result}")
                else:
                    print(f"   ❌ Erro ao configurar: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro na configuração: {str(e)}")
            return False
        
        # Verificar configuração
        print("\n5. ✅ Verificando configuração final...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_base}/webhook")
                
                if response.status_code == 200:
                    webhook_info = response.json()
                    configured_url = webhook_info.get('webhook', '')
                    
                    print(f"   📋 Webhook configurado: {configured_url}")
                    
                    if configured_url == WEBHOOK_URL:
                        print("   🎉 WEBHOOK CONFIGURADO CORRETAMENTE!")
                        return True
                    else:
                        print(f"   ⚠️ URL diferente da esperada")
                        print(f"   Expected: {WEBHOOK_URL}")
                        print(f"   Got: {configured_url}")
                        return False
                else:
                    print(f"   ❌ Erro na verificação: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro na verificação: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

async def testar_webhook_funcionando():
    print("\n\n🧪 TESTANDO WEBHOOK")
    print("=" * 50)
    
    print(f"1. 📡 Testando endpoint: {WEBHOOK_URL}")
    
    # Simular mensagem do Z-API
    test_message = {
        "type": "ReceivedCallback",
        "phone": "5531999999999@c.us",
        "text": {
            "message": "teste final"
        },
        "messageId": "final_test_123",
        "fromMe": False,
        "timestamp": 1640995200
    }
    
    print(f"2. 📨 Enviando mensagem de teste...")
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                WEBHOOK_URL,
                json=test_message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("   ✅ Webhook funcionando perfeitamente!")
                result = response.json()
                print(f"   📋 Resposta: {result}")
                return True
            else:
                print(f"   ❌ Webhook retornou erro: {response.status_code}")
                print(f"   📝 Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")
        return False

def mostrar_resultado_final(app_ok, webhook_ok, teste_ok):
    print("\n\n" + "=" * 70)
    print("🎯 RESULTADO FINAL")
    print("=" * 70)
    
    print(f"📱 Aplicação Vercel: {'✅ ONLINE' if app_ok else '❌ PROBLEMA'}")
    print(f"🔗 Webhook Z-API: {'✅ CONFIGURADO' if webhook_ok else '❌ PROBLEMA'}")
    print(f"🧪 Teste Funcional: {'✅ FUNCIONANDO' if teste_ok else '❌ PROBLEMA'}")
    
    if app_ok and webhook_ok and teste_ok:
        print("\n🎉 CHATBOT TOTALMENTE FUNCIONAL!")
        print("=" * 50)
        print()
        print("📱 TESTE AGORA NO WHATSAPP:")
        print("   1. Abra o WhatsApp")
        print("   2. Envie mensagem para seu número Z-API")
        print("   3. Digite: 'oi'")
        print("   4. ✅ Deve receber: Menu com opções 1-5")
        print("   5. Digite: '1'")
        print("   6. ✅ Deve receber: 'Digite seu CPF'")
        print("   7. Digite: '2'")
        print("   8. ✅ Deve receber: 'Digite seu CPF para agendamentos'")
        print()
        print("🔍 Para monitorar:")
        print(f"   Logs Vercel: https://vercel.com/dashboard")
        print(f"   Health Check: {VERCEL_URL}/webhook/health")
        print()
        print("🎯 SEU CHATBOT ESTÁ PRONTO! 🚀")
        
    else:
        print("\n⚠️ AINDA HÁ PROBLEMAS")
        print("=" * 50)
        
        if not app_ok:
            print("🔧 Aplicação Vercel:")
            print("   - Verifique deploy no Vercel")
            print("   - Confirme variáveis de ambiente")
        
        if not webhook_ok:
            print("🔧 Webhook Z-API:")
            print("   - Verifique credenciais Z-API")
            print("   - Confirme instância ativa")
        
        if not teste_ok:
            print("🔧 Teste Funcional:")
            print("   - Verifique logs da aplicação")
            print("   - Teste manual no WhatsApp")

async def main():
    print("🚀 CONFIGURAÇÃO FINAL - VERCEL + Z-API")
    print("=" * 70)
    print(f"🌐 URL Vercel: {VERCEL_URL}")
    print(f"📡 Webhook: {WEBHOOK_URL}")
    print()
    
    # Executar verificações
    app_ok = await verificar_aplicacao_vercel()
    
    if not app_ok:
        print("❌ Aplicação Vercel não está respondendo!")
        return
    
    webhook_ok = await configurar_webhook_zapi()
    teste_ok = False
    
    if webhook_ok:
        teste_ok = await testar_webhook_funcionando()
    
    # Mostrar resultado
    mostrar_resultado_final(app_ok, webhook_ok, teste_ok)

if __name__ == "__main__":
    asyncio.run(main())