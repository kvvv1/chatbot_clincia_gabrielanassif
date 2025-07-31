#!/usr/bin/env python3
"""
Configuração específica do webhook para Vercel
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

async def verificar_vercel_deployment():
    print("🔍 VERIFICANDO DEPLOYMENT VERCEL")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # No Vercel, app_host deve ser o domínio da aplicação
        if settings.app_host == "0.0.0.0":
            print("❌ PROBLEMA: app_host ainda está configurado para desenvolvimento!")
            print("💡 No Vercel, configure VERCEL_URL ou APP_HOST com seu domínio")
            print("   Exemplo: seu-chatbot.vercel.app")
            return None
        
        vercel_url = f"https://{settings.app_host}"
        print(f"1. 🌐 URL Vercel: {vercel_url}")
        
        # Testar health check
        print("2. 🏥 Testando aplicação no Vercel...")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{vercel_url}/webhook/health")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Aplicação funcionando!")
                    print(f"   📊 Status: {data.get('status')}")
                    print(f"   🌍 Environment: {data.get('environment')}")
                    return vercel_url
                else:
                    print(f"   ❌ Aplicação retornou erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"   ❌ Erro ao acessar aplicação: {str(e)}")
            print("   💡 Verifique se o deploy foi feito corretamente")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

async def configurar_webhook_vercel():
    print("\n\n📡 CONFIGURANDO WEBHOOK PARA VERCEL")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # Verificar credenciais Z-API
        if not settings.zapi_instance_id or not settings.zapi_token:
            print("❌ Credenciais Z-API não configuradas!")
            return False
        
        print(f"1. 📱 Instância Z-API: {settings.zapi_instance_id[:8]}...")
        
        # URL do webhook Vercel
        vercel_url = f"https://{settings.app_host}"
        webhook_url = f"{vercel_url}/webhook"
        
        print(f"2. 🔗 Webhook URL: {webhook_url}")
        
        # Construir URL da Z-API
        zapi_base = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        # Verificar status da instância
        print("3. 🔍 Verificando instância Z-API...")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{zapi_base}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Instância ativa!")
                    print(f"   📊 Status: {status_data}")
                else:
                    print(f"   ❌ Instância não encontrada: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro ao verificar instância: {str(e)}")
            return False
        
        # Configurar webhook
        print("4. ⚙️ Configurando webhook...")
        
        webhook_config = {
            "webhook": webhook_url,
            "webhookEvents": ["message", "status"]
        }
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{zapi_base}/webhook",
                    json=webhook_config
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook configurado!")
                else:
                    print(f"   ❌ Erro ao configurar: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro na configuração: {str(e)}")
            return False
        
        # Verificar configuração
        print("5. ✅ Verificando configuração...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_base}/webhook")
                
                if response.status_code == 200:
                    webhook_info = response.json()
                    configured_url = webhook_info.get('webhook', '')
                    
                    print(f"   📋 Webhook configurado: {configured_url}")
                    
                    if configured_url == webhook_url:
                        print("   🎉 WEBHOOK VERCEL CONFIGURADO CORRETAMENTE!")
                        return True
                    else:
                        print(f"   ⚠️ URL diferente da esperada")
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

async def testar_webhook_vercel():
    print("\n\n🧪 TESTANDO WEBHOOK VERCEL")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        vercel_url = f"https://{settings.app_host}"
        webhook_url = f"{vercel_url}/webhook"
        
        print(f"1. 📡 Testando: {webhook_url}")
        
        # Simular mensagem do Z-API
        test_message = {
            "type": "ReceivedCallback",
            "phone": "5531999999999@c.us",
            "text": {
                "message": "teste vercel"
            },
            "messageId": "vercel_test_123",
            "fromMe": False,
            "timestamp": 1640995200
        }
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    webhook_url,
                    json=test_message
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook Vercel funcionando!")
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
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def mostrar_instrucoes_vercel():
    print("\n\n📋 INSTRUÇÕES PARA VERCEL")
    print("=" * 50)
    
    print("1. 🌐 Verificar variáveis de ambiente no Vercel:")
    print("   - Acesse: https://vercel.com/dashboard")
    print("   - Vá em seu projeto → Settings → Environment Variables")
    print("   - Verifique se estão configuradas:")
    print("     • ZAPI_INSTANCE_ID")
    print("     • ZAPI_TOKEN")
    print("     • ZAPI_CLIENT_TOKEN")
    print("     • SUPABASE_URL")
    print("     • SUPABASE_ANON_KEY")
    print("     • APP_HOST (seu domínio .vercel.app)")
    print()
    
    print("2. 🚀 Fazer redeploy se necessário:")
    print("   vercel --prod")
    print()
    
    print("3. 📱 Testar WhatsApp:")
    print("   - Envie: 'oi'")
    print("   - Deve receber: Menu")
    print("   - Envie: '1'")
    print("   - Deve receber: 'Digite seu CPF'")
    print()
    
    print("4. 🔍 Ver logs do Vercel:")
    print("   vercel logs --follow")

async def main():
    print("🚀 CONFIGURAÇÃO WEBHOOK VERCEL")
    print("=" * 70)
    
    # Verificar deployment
    vercel_url = await verificar_vercel_deployment()
    
    if not vercel_url:
        print("\n❌ PROBLEMA NO DEPLOYMENT VERCEL!")
        print("🔧 Corrija primeiro o deployment, depois execute novamente")
        return
    
    # Configurar webhook
    webhook_ok = await configurar_webhook_vercel()
    
    if not webhook_ok:
        print("\n❌ PROBLEMA NA CONFIGURAÇÃO DO WEBHOOK!")
        return
    
    # Testar webhook
    teste_ok = await testar_webhook_vercel()
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO:")
    
    if webhook_ok and teste_ok:
        print("🎉 VERCEL CONFIGURADO COM SUCESSO!")
        print()
        print("📱 Agora teste no WhatsApp:")
        print("   1. Envie: 'oi'")
        print("   2. Deve receber: Menu com opções")
        print("   3. Envie: '1'")
        print("   4. Deve receber: 'Digite seu CPF'")
        print()
        print("🔍 Se não funcionar, verifique os logs:")
        print("   vercel logs --follow")
    else:
        print("❌ AINDA HÁ PROBLEMAS!")
        mostrar_instrucoes_vercel()

if __name__ == "__main__":
    asyncio.run(main())