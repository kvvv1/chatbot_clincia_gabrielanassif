#!/usr/bin/env python3
"""
🔧 CONFIGURADOR COMPLETO DE WEBHOOKS Z-API
Configura todos os 5 tipos de webhooks necessários para o chatbot funcionar perfeitamente
"""

import requests
import json
import os
from datetime import datetime

# Configurações do Z-API
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")

# URL base do seu servidor (ajuste conforme necessário)
BASE_URL = "https://chatbot-clincia.vercel.app"  # Ajuste para sua URL real

# URLs dos webhooks
WEBHOOK_URLS = {
    "ao_enviar": f"{BASE_URL}/webhook/status",
    "ao_desconectar": f"{BASE_URL}/webhook/connected", 
    "receber_status": f"{BASE_URL}/webhook/status",
    "ao_receber": f"{BASE_URL}/webhook/message",
    "ao_conectar": f"{BASE_URL}/webhook/connected"
}

def test_webhook_endpoints():
    """Testa se todos os endpoints dos webhooks estão funcionando"""
    print("🧪 TESTANDO ENDPOINTS DOS WEBHOOKS...")
    
    endpoints_to_test = [
        ("/", "Health Check"),
        ("/webhook", "Webhook Principal"),
        ("/webhook/message", "Webhook Mensagens"),
        ("/webhook/status", "Webhook Status"),
        ("/webhook/connected", "Webhook Conexão"),
        ("/webhook/health", "Webhook Health")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code} - {url}")
        except Exception as e:
            print(f"❌ {description}: ERRO - {str(e)}")

def configure_webhook_zapi(webhook_type, webhook_url):
    """Configura um webhook específico no Z-API"""
    
    # Headers necessários para a API do Z-API
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    # URL da API do Z-API para configurar webhooks
    api_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/webhook"
    
    # Dados para configurar o webhook
    webhook_data = {
        "url": webhook_url,
        "enabled": True
    }
    
    try:
        print(f"🔧 Configurando webhook '{webhook_type}'...")
        print(f"   URL: {webhook_url}")
        
        response = requests.post(api_url, headers=headers, json=webhook_data, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Webhook '{webhook_type}' configurado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao configurar webhook '{webhook_type}': {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook '{webhook_type}': {str(e)}")
        return False

def get_current_webhooks():
    """Obtém a configuração atual dos webhooks no Z-API"""
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    api_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/webhook"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao obter webhooks atuais: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter webhooks atuais: {str(e)}")
        return None

def configure_all_webhooks():
    """Configura todos os webhooks necessários"""
    
    print("🚀 CONFIGURANDO TODOS OS WEBHOOKS DO Z-API")
    print("=" * 60)
    
    # Primeiro, testar se os endpoints estão funcionando
    test_webhook_endpoints()
    print()
    
    # Verificar webhooks atuais
    print("📋 VERIFICANDO CONFIGURAÇÃO ATUAL...")
    current_webhooks = get_current_webhooks()
    if current_webhooks:
        print(f"Webhooks atuais: {json.dumps(current_webhooks, indent=2)}")
    print()
    
    # Configurar cada webhook
    success_count = 0
    total_webhooks = len(WEBHOOK_URLS)
    
    for webhook_type, webhook_url in WEBHOOK_URLS.items():
        print(f"🔧 Configurando: {webhook_type.upper()}")
        print(f"   URL: {webhook_url}")
        
        if configure_webhook_zapi(webhook_type, webhook_url):
            success_count += 1
        
        print("-" * 40)
    
    # Resumo final
    print("📊 RESUMO DA CONFIGURAÇÃO")
    print("=" * 60)
    print(f"✅ Webhooks configurados com sucesso: {success_count}/{total_webhooks}")
    
    if success_count == total_webhooks:
        print("🎉 TODOS OS WEBHOOKS FORAM CONFIGURADOS COM SUCESSO!")
    else:
        print("⚠️  Alguns webhooks não puderam ser configurados. Verifique os erros acima.")
    
    return success_count == total_webhooks

def generate_webhook_config_guide():
    """Gera um guia manual para configurar webhooks no painel Z-API"""
    
    print("\n📖 GUIA MANUAL PARA CONFIGURAR WEBHOOKS NO PAINEL Z-API")
    print("=" * 70)
    
    guide = f"""
🔧 CONFIGURAÇÃO MANUAL NO PAINEL Z-API

1️⃣ Acesse: https://app.z-api.io/
2️⃣ Faça login na sua conta
3️⃣ Vá para "Instâncias"
4️⃣ Clique na instância: {ZAPI_INSTANCE_ID}
5️⃣ Vá para a aba "Webhook" ou "Configurações"

📋 CONFIGURAR OS 5 WEBHOOKS:

✅ AO ENVIAR:
   URL: {WEBHOOK_URLS['ao_enviar']}
   Descrição: Recebe confirmação quando uma mensagem é enviada

✅ AO DESCONECTAR:
   URL: {WEBHOOK_URLS['ao_desconectar']}
   Descrição: Recebe notificação quando o WhatsApp é desconectado

✅ RECEBER STATUS DA MENSAGEM:
   URL: {WEBHOOK_URLS['receber_status']}
   Descrição: Recebe status de entrega, leitura, etc.

✅ AO RECEBER:
   URL: {WEBHOOK_URLS['ao_receber']}
   Descrição: Recebe mensagens enviadas pelos clientes

✅ AO CONECTAR:
   URL: {WEBHOOK_URLS['ao_conectar']}
   Descrição: Recebe notificação quando o WhatsApp é conectado

⚙️ CONFIGURAÇÕES ADICIONAIS:
   ✅ Ativar "Notificar as enviadas por mim também"
   ✅ Ativar todos os eventos
   ✅ Salvar configurações

🧪 TESTE APÓS CONFIGURAÇÃO:
   1. Envie uma mensagem para o WhatsApp da clínica
   2. Verifique se o webhook recebe a notificação
   3. Verifique se a resposta é enviada automaticamente
"""
    
    print(guide)

def main():
    """Função principal"""
    
    print("🤖 CONFIGURADOR DE WEBHOOKS Z-API - CHATBOT CLÍNICA")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏥 Clínica: Gabriela Nassif")
    print(f"📱 Instance ID: {ZAPI_INSTANCE_ID}")
    print(f"🌐 URL Base: {BASE_URL}")
    print("=" * 60)
    
    # Perguntar se quer configurar automaticamente ou manualmente
    print("\nEscolha uma opção:")
    print("1️⃣ - Configurar automaticamente via API")
    print("2️⃣ - Gerar guia manual para configurar no painel")
    print("3️⃣ - Testar apenas os endpoints")
    
    try:
        opcao = input("\nDigite sua opção (1, 2 ou 3): ").strip()
        
        if opcao == "1":
            success = configure_all_webhooks()
            if success:
                print("\n🎉 CONFIGURAÇÃO AUTOMÁTICA CONCLUÍDA!")
                print("Seu chatbot está pronto para receber mensagens!")
            else:
                print("\n⚠️  Use o guia manual para configurar os webhooks restantes.")
                generate_webhook_config_guide()
                
        elif opcao == "2":
            generate_webhook_config_guide()
            
        elif opcao == "3":
            test_webhook_endpoints()
            
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main() 