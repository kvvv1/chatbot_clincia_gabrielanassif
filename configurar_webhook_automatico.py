#!/usr/bin/env python3
"""
Configuração automática do webhook Z-API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

async def configurar_webhook_zapi():
    print("🔧 CONFIGURAÇÃO AUTOMÁTICA DO WEBHOOK Z-API")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # Verificar credenciais
        if not settings.zapi_instance_id or not settings.zapi_token:
            print("❌ Credenciais Z-API não encontradas!")
            print("💡 Configure as variáveis de ambiente:")
            print("   ZAPI_INSTANCE_ID=sua_instance_id")
            print("   ZAPI_TOKEN=seu_token")
            return False
        
        print(f"1. 📡 Conectando à instância: {settings.zapi_instance_id[:8]}...")
        
        # Construir URLs
        zapi_base = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        # Determinar webhook URL
        if settings.environment == "production":
            webhook_url = f"https://{settings.app_host}/webhook"
        else:
            # Para desenvolvimento, usar ngrok ou IP público
            webhook_url = f"http://{settings.app_host}:{settings.app_port}/webhook"
        
        print(f"2. 🔗 Webhook URL: {webhook_url}")
        
        # Testar status da instância primeiro
        print("\n3. 🔍 Verificando status da instância...")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{zapi_base}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Instância ativa: {status_data}")
                else:
                    print(f"   ❌ Instância não encontrada: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro ao verificar status: {str(e)}")
            return False
        
        # Configurar webhook
        print("\n4. 📡 Configurando webhook...")
        
        webhook_config = {
            "webhook": webhook_url,
            "webhookEvents": ["message"]
        }
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{zapi_base}/webhook",
                    json=webhook_config
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook configurado com sucesso!")
                    print(f"   📋 Configuração: {webhook_config}")
                else:
                    print(f"   ❌ Erro ao configurar webhook: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro na configuração: {str(e)}")
            return False
        
        # Verificar se webhook foi configurado
        print("\n5. ✅ Verificando configuração...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_base}/webhook")
                
                if response.status_code == 200:
                    webhook_info = response.json()
                    print(f"   📋 Webhook atual: {webhook_info}")
                    
                    configured_url = webhook_info.get('webhook', '')
                    if configured_url == webhook_url:
                        print("   🎉 WEBHOOK CONFIGURADO CORRETAMENTE!")
                        return True
                    else:
                        print(f"   ⚠️ URL configurada diferente: {configured_url}")
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

async def testar_webhook_configurado():
    print("\n\n🧪 TESTANDO WEBHOOK CONFIGURADO")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # Determinar webhook URL
        if settings.environment == "production":
            webhook_url = f"https://{settings.app_host}/webhook"
        else:
            webhook_url = f"http://{settings.app_host}:{settings.app_port}/webhook"
        
        print(f"1. 📡 Testando endpoint: {webhook_url}")
        
        # Simular mensagem do Z-API
        test_message = {
            "type": "ReceivedCallback",
            "phone": "5531999999999@c.us",
            "text": {
                "message": "teste webhook"
            },
            "messageId": "webhook_test_123",
            "fromMe": False,
            "timestamp": 1640995200
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    webhook_url,
                    json=test_message
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook respondendo corretamente!")
                    print("   📋 Resposta:", response.json())
                    return True
                else:
                    print(f"   ❌ Webhook retornou erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro ao testar webhook: {str(e)}")
            print("   💡 Verifique se a aplicação está rodando")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def mostrar_proximos_passos(webhook_ok, teste_ok):
    print("\n\n🎯 PRÓXIMOS PASSOS")
    print("=" * 50)
    
    if webhook_ok and teste_ok:
        print("🎉 TUDO CONFIGURADO COM SUCESSO!")
        print()
        print("📱 Agora você pode testar:")
        print("   1. Abra o WhatsApp")
        print("   2. Envie mensagem para seu número Z-API")
        print("   3. Digite: 'oi'")
        print("   4. Deve receber: Menu com opções 1-5")
        print("   5. Digite: '1'")
        print("   6. Deve receber: 'Digite seu CPF'")
        print()
        print("🔍 Se não funcionar, verifique:")
        print("   - Aplicação está rodando?")
        print("   - Logs mostram as mensagens chegando?")
        
    elif webhook_ok and not teste_ok:
        print("⚠️ WEBHOOK CONFIGURADO, MAS TESTE FALHOU")
        print()
        print("🔧 Possíveis problemas:")
        print("   - Aplicação não está rodando")
        print("   - URL não é acessível pela internet")
        print("   - Firewall bloqueando conexões")
        print()
        print("💡 Soluções:")
        print("   1. python run.py (para subir aplicação)")
        print("   2. Use ngrok para desenvolvimento:")
        print("      ngrok http 8000")
        print("   3. Configure webhook com URL do ngrok")
        
    else:
        print("❌ CONFIGURAÇÃO FALHOU")
        print()
        print("🔧 Verifique:")
        print("   1. Credenciais Z-API estão corretas?")
        print("   2. Instância Z-API está ativa?")
        print("   3. Conectividade com internet OK?")
        print()
        print("💡 Para debug:")
        print("   python verificar_configuracao_completa.py")

if __name__ == "__main__":
    try:
        print("🚀 CONFIGURAÇÃO AUTOMÁTICA DO WEBHOOK")
        print("=" * 70)
        
        # Executar configuração
        webhook_ok = asyncio.run(configurar_webhook_zapi())
        
        if webhook_ok:
            teste_ok = asyncio.run(testar_webhook_configurado())
        else:
            teste_ok = False
        
        # Mostrar próximos passos
        mostrar_proximos_passos(webhook_ok, teste_ok)
        
    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)}")
        import traceback
        traceback.print_exc()