#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE STATUS DO WHATSAPP
Verifica se o WhatsApp está conectado e funcionando
"""

import os
import requests
import json
from app.config import settings

def verificar_status_whatsapp():
    """Verifica o status completo do WhatsApp"""
    print("🔍 VERIFICANDO STATUS DO WHATSAPP")
    print("=" * 50)
    
    # Verificar configurações
    print("📋 CONFIGURAÇÕES:")
    print(f"   Instance ID: {settings.zapi_instance_id[:10]}..." if settings.zapi_instance_id else "❌ Não configurado")
    print(f"   Token: {'✅ Configurado' if settings.zapi_token else '❌ Não configurado'}")
    print(f"   Client Token: {'✅ Configurado' if settings.zapi_client_token else '❌ Não configurado'}")
    
    if not all([settings.zapi_instance_id, settings.zapi_token, settings.zapi_client_token]):
        print("\n❌ PROBLEMA: Credenciais Z-API não configuradas!")
        return
    
    # URL base
    base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
    headers = {"Client-Token": settings.zapi_client_token}
    
    print(f"\n🌐 URL Base: {base_url}")
    
    try:
        # 1. Verificar status da instância
        print("\n1️⃣ VERIFICANDO STATUS DA INSTÂNCIA...")
        response = requests.get(f"{base_url}/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {json.dumps(data, indent=2)}")
            
            # Verificar conexão
            connected = data.get('connected', False)
            smartphone_connected = data.get('smartphoneConnected', False)
            
            print(f"\n📱 STATUS DO WHATSAPP:")
            print(f"   Conectado: {'✅ Sim' if connected else '❌ Não'}")
            print(f"   Smartphone: {'✅ Conectado' if smartphone_connected else '❌ Desconectado'}")
            
            if not connected:
                print("\n🔧 PROBLEMA: WhatsApp não está conectado!")
                print("   Solução: Conecte o WhatsApp no painel Z-API")
                return
                
            if not smartphone_connected:
                print("\n🔧 PROBLEMA: Smartphone não está conectado!")
                print("   Solução: Verifique se o celular está online")
                return
                
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
        
        # 2. Verificar webhooks
        print("\n2️⃣ VERIFICANDO WEBHOOKS...")
        webhook_url = "https://chatbot-clincia.vercel.app/webhook"
        
        # Tentar diferentes endpoints para webhook
        webhook_endpoints = [
            "/webhook",
            "/webhook/info",
            "/settings"
        ]
        
        webhook_ok = False
        for endpoint in webhook_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                print(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        # Verificar se tem webhook configurado
                        webhook_config = data.get('webhook') or data.get('url') or data.get('webhookUrl')
                        if webhook_config:
                            print(f"   🎯 Webhook encontrado: {webhook_config}")
                            if webhook_config == webhook_url:
                                print("   ✅ Webhook configurado corretamente!")
                                webhook_ok = True
                            else:
                                print("   ⚠️ Webhook diferente do esperado")
                
            except Exception as e:
                print(f"   {endpoint}: Erro - {str(e)}")
        
        if not webhook_ok:
            print("\n🔧 PROBLEMA: Webhook não configurado!")
            print("   Solução: Configure o webhook no painel Z-API")
            print(f"   URL esperada: {webhook_url}")
        
        # 3. Testar envio de mensagem
        print("\n3️⃣ TESTANDO ENVIO DE MENSAGEM...")
        test_phone = "5531999999999"  # Número de teste
        
        payload = {
            "phone": test_phone,
            "message": "Teste de conexão - " + str(int(time.time()))
        }
        
        try:
            response = requests.post(
                f"{base_url}/send-text",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Mensagem enviada com sucesso!")
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar envio: {str(e)}")
        
        # 4. Verificar logs do webhook
        print("\n4️⃣ VERIFICANDO LOGS DO WEBHOOK...")
        try:
            response = requests.get("https://chatbot-clincia.vercel.app/webhook/health", timeout=10)
            if response.status_code == 200:
                print("✅ Webhook está respondendo!")
            else:
                print(f"❌ Webhook com problema: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao verificar webhook: {str(e)}")
        
        # Resumo
        print("\n" + "=" * 50)
        print("📊 RESUMO DO DIAGNÓSTICO:")
        
        if connected and smartphone_connected:
            print("✅ WhatsApp conectado e funcionando")
        else:
            print("❌ WhatsApp não conectado")
            
        if webhook_ok:
            print("✅ Webhook configurado")
        else:
            print("❌ Webhook não configurado")
            
        print("\n🔧 PRÓXIMOS PASSOS:")
        if not connected or not smartphone_connected:
            print("   1. Conecte o WhatsApp no painel Z-API")
            print("   2. Verifique se o celular está online")
            
        if not webhook_ok:
            print("   3. Configure o webhook no painel Z-API")
            print(f"      URL: {webhook_url}")
            print("   4. Ative todos os eventos")
            
        print("   5. Teste enviando uma mensagem para o número conectado")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

if __name__ == "__main__":
    import time
    verificar_status_whatsapp() 