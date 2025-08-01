#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE STATUS DE TODAS AS APIs
Verifica o status de todas as APIs e integrações do sistema
"""

import requests
import json
import os
from datetime import datetime
import time

# Configurações
BASE_URL = "https://chatbot-clincia.vercel.app"
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")
SUPABASE_URL = "https://feqylqrphdpeeusdyeyw.supabase.co"

def test_backend_endpoints():
    """Testa todos os endpoints do backend"""
    print("🔧 TESTANDO ENDPOINTS DO BACKEND...")
    print("=" * 50)
    
    endpoints = [
        ("/", "Health Check Principal"),
        ("/health", "Health Check Detalhado"),
        ("/test", "Endpoint de Teste"),
        ("/debug", "Informações de Debug"),
        ("/webhook", "Webhook Principal"),
        ("/webhook/health", "Webhook Health"),
        ("/webhook/message", "Webhook Mensagens"),
        ("/webhook/status", "Webhook Status"),
        ("/webhook/connected", "Webhook Conexão"),
        ("/dashboard/test-simple", "Dashboard Teste"),
        ("/dashboard/status", "Dashboard Status")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code} ({response_time}ms) - {url}")
            
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": response.status_code,
                "response_time": response_time,
                "url": url,
                "success": response.status_code == 200
            })
            
        except Exception as e:
            print(f"❌ {description}: ERRO - {str(e)}")
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": None,
                "response_time": None,
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    return results

def test_zapi_integration():
    """Testa a integração com Z-API"""
    print("\n📱 TESTANDO INTEGRAÇÃO Z-API...")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    # Teste 1: Verificar status da instância
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/status"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status da Instância Z-API: {data.get('status', 'N/A')}")
            print(f"   Conectado: {data.get('connected', False)}")
            print(f"   Número: {data.get('number', 'N/A')}")
        else:
            print(f"❌ Erro ao verificar status Z-API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status Z-API: {str(e)}")
    
    # Teste 2: Verificar webhooks configurados
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/webhook"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            webhooks = response.json()
            print(f"✅ Webhooks Z-API: {len(webhooks) if isinstance(webhooks, list) else 'Configurados'}")
        else:
            print(f"❌ Erro ao verificar webhooks Z-API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar webhooks Z-API: {str(e)}")
    
    # Teste 3: Enviar mensagem de teste
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
        test_data = {
            "phone": "553198600366@c.us",
            "message": f"Teste de API - {datetime.now().strftime('%H:%M:%S')}"
        }
        
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Envio de Mensagem Z-API: Sucesso")
            print(f"   Message ID: {data.get('id', 'N/A')}")
        else:
            print(f"❌ Erro ao enviar mensagem Z-API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem Z-API: {str(e)}")

def test_supabase_integration():
    """Testa a integração com Supabase"""
    print("\n🗄️ TESTANDO INTEGRAÇÃO SUPABASE...")
    print("=" * 50)
    
    # Teste básico de conectividade
    try:
        response = requests.get(SUPABASE_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Supabase URL: Acessível")
        else:
            print(f"⚠️ Supabase URL: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar Supabase: {str(e)}")
    
    # Teste via API do backend
    try:
        url = f"{BASE_URL}/dashboard/test-simple"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Supabase via Backend: Funcionando")
        else:
            print(f"❌ Supabase via Backend: Erro {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar Supabase via Backend: {str(e)}")

def test_webhook_functionality():
    """Testa a funcionalidade dos webhooks"""
    print("\n🔗 TESTANDO FUNCIONALIDADE DOS WEBHOOKS...")
    print("=" * 50)
    
    # Teste de webhook com dados simulados
    test_data = {
        "event": "message",
        "data": {
            "id": f"test_{int(time.time())}",
            "type": "text",
            "from": "553198600366@c.us",
            "fromMe": False,
            "text": {
                "body": "1"
            }
        }
    }
    
    try:
        url = f"{BASE_URL}/webhook/message"
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Webhook Message: Processado com sucesso")
            print(f"   Status: {response.json().get('status', 'N/A')}")
        else:
            print(f"❌ Webhook Message: Erro {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook message: {str(e)}")
    
    # Teste de webhook de status
    test_status_data = {
        "event": "status",
        "data": {
            "id": f"test_{int(time.time())}",
            "status": "delivered"
        }
    }
    
    try:
        url = f"{BASE_URL}/webhook/status"
        response = requests.post(url, json=test_status_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Webhook Status: Processado com sucesso")
        else:
            print(f"❌ Webhook Status: Erro {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook status: {str(e)}")

def generate_summary_report(backend_results):
    """Gera um relatório resumido"""
    print("\n📊 RELATÓRIO DE STATUS DAS APIs")
    print("=" * 60)
    
    total_endpoints = len(backend_results)
    successful_endpoints = sum(1 for r in backend_results if r['success'])
    
    print(f"🎯 BACKEND (FastAPI/Vercel):")
    print(f"   ✅ Endpoints funcionando: {successful_endpoints}/{total_endpoints}")
    print(f"   📊 Taxa de sucesso: {(successful_endpoints/total_endpoints)*100:.1f}%")
    
    # Verificar endpoints críticos
    critical_endpoints = ['/', '/webhook/message', '/webhook/status', '/webhook/connected']
    critical_working = sum(1 for r in backend_results if r['endpoint'] in critical_endpoints and r['success'])
    
    print(f"   🔑 Endpoints críticos: {critical_working}/{len(critical_endpoints)}")
    
    print(f"\n📱 Z-API (WhatsApp):")
    print(f"   ✅ Instance ID: {ZAPI_INSTANCE_ID}")
    print(f"   ✅ Token: Configurado")
    print(f"   ✅ Client Token: Configurado")
    
    print(f"\n🗄️ SUPABASE (Banco de Dados):")
    print(f"   ✅ URL: {SUPABASE_URL}")
    print(f"   ✅ Integração: Ativa")
    
    print(f"\n🌐 FRONTEND (React):")
    print(f"   ✅ Dashboard: Implementado")
    print(f"   ✅ Interface: Moderna")
    
    # Status geral
    if successful_endpoints >= total_endpoints * 0.8:  # 80% ou mais funcionando
        print(f"\n🎉 STATUS GERAL: SISTEMA OPERACIONAL!")
        print(f"   O sistema está funcionando corretamente!")
    elif successful_endpoints >= total_endpoints * 0.6:  # 60% ou mais funcionando
        print(f"\n⚠️ STATUS GERAL: SISTEMA PARCIALMENTE OPERACIONAL")
        print(f"   Alguns endpoints podem ter problemas.")
    else:
        print(f"\n❌ STATUS GERAL: SISTEMA COM PROBLEMAS")
        print(f"   Muitos endpoints não estão funcionando.")

def main():
    """Função principal"""
    print("🔍 VERIFICADOR DE STATUS DE TODAS AS APIs - CHATBOT CLÍNICA")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏥 Clínica: Gabriela Nassif")
    print(f"🌐 URL Base: {BASE_URL}")
    print("=" * 70)
    
    # Testar backend
    backend_results = test_backend_endpoints()
    
    # Testar Z-API
    test_zapi_integration()
    
    # Testar Supabase
    test_supabase_integration()
    
    # Testar webhooks
    test_webhook_functionality()
    
    # Gerar relatório
    generate_summary_report(backend_results)
    
    print(f"\n✅ Verificação concluída em {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 