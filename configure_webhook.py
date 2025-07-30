#!/usr/bin/env python3
"""
Script para configurar e verificar webhook no Z-API
"""

import os
import requests
import json
from datetime import datetime

def get_env_var(var_name, default=""):
    """Obtém variável de ambiente"""
    return os.getenv(var_name, default)

def configure_zapi_webhook():
    """Configura o webhook no Z-API"""
    
    # Obter configurações do ambiente
    zapi_instance_id = get_env_var('ZAPI_INSTANCE_ID')
    zapi_token = get_env_var('ZAPI_TOKEN')
    zapi_client_token = get_env_var('ZAPI_CLIENT_TOKEN')
    app_host = get_env_var('APP_HOST', 'seu-app.vercel.app')  # Substitua pela sua URL
    
    if not all([zapi_instance_id, zapi_token, zapi_client_token]):
        print("❌ Variáveis de ambiente do Z-API não configuradas!")
        print("Configure as seguintes variáveis:")
        print("- ZAPI_INSTANCE_ID")
        print("- ZAPI_TOKEN") 
        print("- ZAPI_CLIENT_TOKEN")
        return False
    
    webhook_url = f"https://{app_host}/webhook"
    
    print(f"=== CONFIGURAÇÃO DO WEBHOOK Z-API ===")
    print(f"Instance ID: {zapi_instance_id}")
    print(f"Token: {zapi_token[:10]}...")
    print(f"Client Token: {zapi_client_token[:10]}...")
    print(f"Webhook URL: {webhook_url}")
    print()
    
    # URL base da API do Z-API
    base_url = f"https://api.z-api.io/instances/{zapi_instance_id}/token/{zapi_token}"
    
    # Headers necessários
    headers = {
        "Client-Token": zapi_client_token,
        "Content-Type": "application/json"
    }
    
    # Payload para configurar webhook
    payload = {
        "webhook": webhook_url,
        "webhookByEvents": True,
        "webhookBase64": False
    }
    
    try:
        print("1. Configurando webhook...")
        response = requests.post(
            f"{base_url}/webhook",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook configurado com sucesso!")
        else:
            print("❌ Erro ao configurar webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro na comunicação com Z-API: {str(e)}")
        return False
    
    print()
    
    # Verificar status do webhook
    try:
        print("2. Verificando status do webhook...")
        response = requests.get(
            f"{base_url}/webhook",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            webhook_info = response.json()
            print("✅ Status do webhook obtido!")
            print(f"   Webhook configurado: {webhook_info.get('webhook', 'N/A')}")
        else:
            print("❌ Erro ao verificar status do webhook")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
    
    return True

def test_webhook_endpoint():
    """Testa o endpoint do webhook"""
    
    app_host = get_env_var('APP_HOST', 'seu-app.vercel.app')  # Substitua pela sua URL
    webhook_url = f"https://{app_host}/webhook"
    
    print(f"\n=== TESTE DO ENDPOINT WEBHOOK ===")
    print(f"URL: {webhook_url}")
    print()
    
    # Teste 1: GET para verificar se está online
    try:
        print("1. Testando endpoint GET...")
        response = requests.get(webhook_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint GET funcionando!")
        else:
            print("❌ Endpoint GET com problema")
            
    except Exception as e:
        print(f"❌ Erro no teste GET: {str(e)}")
    
    # Teste 2: POST com dados simulados
    try:
        print("\n2. Testando endpoint POST...")
        
        test_data = {
            "event": "message",
            "data": {
                "id": "test_123",
                "type": "text",
                "from": "553198600366@c.us",
                "fromMe": False,
                "text": {
                    "body": "teste"
                }
            }
        }
        
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint POST funcionando!")
        else:
            print("❌ Endpoint POST com problema")
            
    except Exception as e:
        print(f"❌ Erro no teste POST: {str(e)}")

def main():
    """Função principal"""
    print("Iniciando configuração do webhook...")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Configurar webhook no Z-API
    success = configure_zapi_webhook()
    
    if success:
        # Testar endpoint
        test_webhook_endpoint()
    
    print("\n=== INSTRUÇÕES ===")
    print("1. Verifique se o webhook foi configurado corretamente")
    print("2. Teste enviando uma mensagem para o WhatsApp da clínica")
    print("3. Verifique os logs no Vercel para ver se está funcionando")
    print("4. Se houver problemas, verifique as variáveis de ambiente")

if __name__ == "__main__":
    main() 