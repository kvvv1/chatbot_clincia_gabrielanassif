#!/usr/bin/env python3
"""
🧪 TESTADOR DO NOVO TOKEN Z-API
Testa especificamente o novo token fornecido
"""

import requests
import json
from datetime import datetime

# Novo token fornecido
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")

def test_token_without_client_token():
    """Testa o token sem client token"""
    print("🧪 TESTANDO TOKEN SEM CLIENT TOKEN...")
    print("=" * 50)
    
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/status"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token funcionando sem client token!")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Conectado: {data.get('connected', False)}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_token_with_client_token():
    """Testa o token com client token"""
    print("\n🧪 TESTANDO TOKEN COM CLIENT TOKEN...")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/status"
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token funcionando com client token!")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Conectado: {data.get('connected', False)}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_send_message():
    """Testa envio de mensagem"""
    print("\n📤 TESTANDO ENVIO DE MENSAGEM...")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
        test_data = {
            "phone": "553198600366@c.us",
            "message": f"Teste novo token - {datetime.now().strftime('%H:%M:%S')}"
        }
        
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"   Message ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTADOR DO NOVO TOKEN Z-API")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏥 Clínica: Gabriela Nassif")
    print(f"📱 Instance ID: {ZAPI_INSTANCE_ID}")
    print(f"🔑 Novo Token: {ZAPI_TOKEN}")
    print(f"🔑 Client Token: {ZAPI_CLIENT_TOKEN}")
    print("=" * 60)
    
    # Testar sem client token
    test1 = test_token_without_client_token()
    
    # Testar com client token
    test2 = test_token_with_client_token()
    
    # Testar envio de mensagem
    test3 = test_send_message()
    
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 40)
    print(f"Token sem Client Token: {'✅ OK' if test1 else '❌ ERRO'}")
    print(f"Token com Client Token: {'✅ OK' if test2 else '❌ ERRO'}")
    print(f"Envio de Mensagem: {'✅ OK' if test3 else '❌ ERRO'}")
    
    if test1 or test2:
        print("\n🎉 TOKEN FUNCIONANDO!")
        if test1:
            print("   O token funciona sem client token")
        if test2:
            print("   O token funciona com client token")
        if test3:
            print("   Envio de mensagens funcionando")
    else:
        print("\n⚠️  TOKEN AINDA COM PROBLEMAS!")
        print("   Pode ser necessário renovar o Client Token também")

if __name__ == "__main__":
    main() 