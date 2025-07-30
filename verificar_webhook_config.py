#!/usr/bin/env python3
"""
Script para verificar se o webhook está configurado no Z-API
"""

import requests
import json

def verificar_webhook_zapi():
    """Verifica se o webhook está configurado no Z-API"""
    print("🔍 Verificando configuração do webhook no Z-API...")
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "17829E98BB59E9ADD55BBBA9"
    client_token = "F909fc109aad54566bf42a6d09f00a8dbS"
    
    # URL esperada do webhook
    expected_webhook = "https://chatbot-clincia.vercel.app/webhook"
    
    try:
        # Tentar diferentes endpoints para verificar webhook
        base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        headers = {"Client-Token": client_token}
        
        print(f"🌐 URL base: {base_url}")
        print(f"📍 Webhook esperado: {expected_webhook}")
        
        # Teste 1: Verificar status da instância
        print("\n1. Verificando status da instância...")
        response = requests.get(f"{base_url}/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data}")
            print(f"🔧 Conectado: {data.get('connected', False)}")
            print(f"📱 Smartphone conectado: {data.get('smartphoneConnected', False)}")
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
        
        # Teste 2: Tentar obter configuração do webhook
        print("\n2. Tentando obter configuração do webhook...")
        
        endpoints_to_try = [
            "/webhook",
            "/webhook/info", 
            "/webhook/status",
            "/settings",
            "/config"
        ]
        
        webhook_found = False
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                print(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      Resposta: {json.dumps(data, indent=2)}")
                    
                    # Verificar se contém webhook
                    if isinstance(data, dict):
                        webhook_url = data.get('webhook') or data.get('url')
                        if webhook_url:
                            print(f"      🎯 Webhook encontrado: {webhook_url}")
                            if webhook_url == expected_webhook:
                                print("      ✅ Webhook configurado corretamente!")
                                webhook_found = True
                            else:
                                print("      ⚠️ Webhook diferente do esperado")
                
            except Exception as e:
                print(f"   {endpoint}: Erro - {str(e)}")
        
        # Conclusão
        print("\n📋 CONCLUSÃO:")
        if webhook_found:
            print("✅ Webhook está configurado!")
            print("🔧 O problema pode ser:")
            print("   - Eventos não ativados")
            print("   - WhatsApp não conectado")
            print("   - Mensagem sendo enviada para número errado")
        else:
            print("❌ Webhook NÃO está configurado!")
            print("🔧 SOLUÇÃO:")
            print("   1. Acesse: https://app.z-api.io/")
            print("   2. Vá para sua instância: 3E4F7360B552F0C2DBCB9E6774402775")
            print("   3. Configure webhook: https://chatbot-clincia.vercel.app/webhook")
            print("   4. Ative todos os eventos")
        
        # Verificar se WhatsApp está conectado
        print("\n3. Verificando conexão do WhatsApp...")
        if data.get('smartphoneConnected'):
            print("✅ WhatsApp conectado!")
        else:
            print("❌ WhatsApp NÃO conectado!")
            print("🔧 Conecte o WhatsApp primeiro")
        
        return webhook_found
        
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {str(e)}")
        return False

def testar_envio_mensagem():
    """Testa envio de mensagem direto via Z-API"""
    print("\n📨 Testando envio de mensagem via Z-API...")
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "17829E98BB59E9ADD55BBBA9"
    client_token = "F909fc109aad54566bf42a6d09f00a8dbS"
    
    try:
        base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        headers = {"Client-Token": client_token}
        
        # Testar envio de mensagem
        payload = {
            "phone": "553198600366",
            "message": "Teste do chatbot - Se você receber esta mensagem, o sistema está funcionando!"
        }
        
        response = requests.post(
            f"{base_url}/send-text",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mensagem enviada com sucesso!")
            print(f"📊 Resposta: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar envio: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO COMPLETO DO WEBHOOK")
    print("=" * 50)
    
    # Verificar webhook
    webhook_ok = verificar_webhook_zapi()
    
    # Testar envio de mensagem
    if webhook_ok:
        testar_envio_mensagem()
    
    print("\n📋 PRÓXIMOS PASSOS:")
    if not webhook_ok:
        print("1. Configure o webhook no painel Z-API")
        print("2. Ative todos os eventos")
        print("3. Teste novamente")
    else:
        print("1. Verifique se está enviando para o número correto")
        print("2. Confirme se o WhatsApp está conectado")
        print("3. Teste enviando 'oi' no WhatsApp") 