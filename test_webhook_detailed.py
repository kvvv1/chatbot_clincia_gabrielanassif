#!/usr/bin/env python3
"""
Teste detalhado do webhook para identificar problemas
"""

import requests
import json
import time
from datetime import datetime

def test_webhook_endpoints():
    """Testa todos os endpoints do webhook"""
    
    # URL base do Vercel (substitua pela sua URL real)
    base_url = "https://seu-app.vercel.app"  # Substitua pela URL real
    
    print(f"=== TESTE DETALHADO DO WEBHOOK ===")
    print(f"URL Base: {base_url}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Teste 1: Endpoint de saúde
    print("1. Testando endpoint de saúde...")
    try:
        response = requests.get(f"{base_url}/webhook/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()
    
    # Teste 2: Endpoint de teste
    print("2. Testando endpoint de teste...")
    try:
        response = requests.get(f"{base_url}/webhook/test", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()
    
    # Teste 3: Simular webhook do Z-API
    print("3. Simulando webhook do Z-API...")
    webhook_data = {
        "event": "message",
        "data": {
            "id": "test_123",
            "type": "text",
            "from": "553198600366@c.us",
            "fromMe": False,
            "text": {
                "body": "1"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()
    
    # Teste 4: Teste de mensagem
    print("4. Testando endpoint de teste de mensagem...")
    try:
        response = requests.post(f"{base_url}/webhook/test-message", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()
    
    # Teste 5: Verificar redirecionamentos
    print("5. Verificando redirecionamentos...")
    try:
        response = requests.post(f"{base_url}/webhook", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code in [301, 302, 307, 308]:
            print(f"   Location: {response.headers.get('Location', 'N/A')}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()

def test_zapi_webhook_config():
    """Testa a configuração do webhook no Z-API"""
    print("=== TESTE DE CONFIGURAÇÃO Z-API ===")
    
    # Você precisará das credenciais do Z-API
    zapi_instance_id = "SEU_INSTANCE_ID"  # Substitua
    zapi_token = "SEU_TOKEN"  # Substitua
    zapi_client_token = "SEU_CLIENT_TOKEN"  # Substitua
    
    base_url = f"https://api.z-api.io/instances/{zapi_instance_id}/token/{zapi_token}"
    
    print(f"URL Base Z-API: {base_url}")
    print()
    
    # Teste 1: Verificar status do webhook
    print("1. Verificando status do webhook no Z-API...")
    try:
        headers = {
            "Client-Token": zapi_client_token,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{base_url}/webhook", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Erro: {str(e)}")
        print()

def main():
    """Função principal"""
    print("Iniciando testes do webhook...")
    print()
    
    # Teste dos endpoints
    test_webhook_endpoints()
    
    # Teste da configuração Z-API (comente se não tiver as credenciais)
    # test_zapi_webhook_config()
    
    print("=== FIM DOS TESTES ===")

if __name__ == "__main__":
    main() 