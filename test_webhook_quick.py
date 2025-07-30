#!/usr/bin/env python3
"""
Teste rápido do webhook para identificar problemas
"""

import requests
import json
import sys

def test_webhook_quick():
    """Teste rápido do webhook"""
    
    # Substitua pela sua URL real
    webhook_url = "https://seu-app.vercel.app/webhook"
    
    print(f"=== TESTE RÁPIDO DO WEBHOOK ===")
    print(f"URL: {webhook_url}")
    print()
    
    # Teste 1: GET básico
    try:
        print("1. Testando GET...")
        response = requests.get(webhook_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        print()
    
    # Teste 2: POST com dados simulados
    try:
        print("2. Testando POST...")
        
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
        print()
        
        if response.status_code == 200:
            print("✅ Webhook funcionando!")
        else:
            print("❌ Problema no webhook")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        print()
    
    # Teste 3: Verificar redirecionamento
    try:
        print("3. Verificando redirecionamento...")
        response = requests.post(webhook_url, timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', 'N/A')
            print(f"   Redirecionamento para: {location}")
            print("   ⚠️  Problema: Webhook está redirecionando!")
        else:
            print("   ✅ Sem redirecionamento")
        print()
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        print()

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
        print(f"Usando URL: {webhook_url}")
    else:
        print("Uso: python test_webhook_quick.py [URL_DO_WEBHOOK]")
        print("Exemplo: python test_webhook_quick.py https://meu-app.vercel.app/webhook")
        return
    
    test_webhook_quick()

if __name__ == "__main__":
    main() 