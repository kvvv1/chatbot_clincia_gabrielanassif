#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO CORRIGIDO DO WEBHOOK Z-API
Usando as credenciais corretas fornecidas pelo usuário
"""

import requests
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ✅ CONFIGURAÇÕES CORRETAS FORNECIDAS PELO USUÁRIO
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")  # ✅ TOKEN CORRETO
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")

# URL base do seu servidor
BASE_URL = "https://chatbot-clincia.vercel.app"

def test_vercel_endpoints():
    """Testa se os endpoints do Vercel estão funcionando"""
    logger.info("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO WEBHOOK")
    logger.info("=" * 60)
    logger.info("=== TESTANDO ENDPOINTS DO VERCEL ===")
    
    endpoints_to_test = [
        ("/", "Health Check"),
        ("/webhook", "Webhook Principal"),
        ("/webhook/", "Webhook Slash"),
        ("/webhook/test", "Webhook Test"),
        ("/webhook/health", "Webhook Health"),
        ("/webhook/status-info", "Webhook Status Info")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            logger.info(f"✅ {description}: {response.status_code}")
            if response.status_code != 200:
                logger.warning(f"   Resposta: {response.text[:200]}")
        except Exception as e:
            logger.error(f"❌ {description}: ERRO - {str(e)}")

def test_zapi_instance_status():
    """Testa o status da instância Z-API"""
    logger.info("\n=== VERIFICANDO STATUS DA INSTÂNCIA Z-API ===")
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/status"
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Instância Z-API ativa")
            logger.info(f"   Status: {data.get('status', 'N/A')}")
            logger.info(f"   Conectado: {data.get('connected', 'N/A')}")
        else:
            logger.error(f"❌ Erro ao verificar status: {response.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {str(e)}")

def test_zapi_webhook_config():
    """Testa a configuração atual do webhook"""
    logger.info("\n=== VERIFICANDO CONFIGURAÇÃO DO WEBHOOK NO Z-API ===")
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/webhook"
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Webhook configurado:")
            logger.info(f"   URL: {data.get('url', 'N/A')}")
            logger.info(f"   Ativo: {data.get('enabled', 'N/A')}")
            logger.info(f"   Eventos: {data.get('events', 'N/A')}")
        else:
            logger.error(f"❌ Erro ao verificar webhook: {response.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao verificar webhook: {str(e)}")

def configure_zapi_webhook():
    """Configura o webhook no Z-API"""
    logger.info("\n=== CONFIGURANDO WEBHOOK CORRETAMENTE ===")
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/webhook"
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": f"{BASE_URL}/webhook",
        "enabled": True,
        "events": ["message", "message-status", "connection-status"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Webhook configurado com sucesso!")
            logger.info(f"   URL: {data.get('url', 'N/A')}")
            logger.info(f"   Ativo: {data.get('enabled', 'N/A')}")
        else:
            logger.error(f"❌ Erro ao configurar webhook: {response.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar webhook: {str(e)}")

def test_webhook_message():
    """Testa o envio de uma mensagem simulada para o webhook"""
    logger.info("\n=== TESTANDO ENVIO DE MENSAGEM SIMULADA ===")
    
    # Simular mensagem recebida do WhatsApp
    test_message = {
        "type": "ReceivedCallback",
        "phone": "5531999999999@c.us",
        "text": {
            "message": "Olá, gostaria de agendar uma consulta"
        },
        "messageId": "test_message_123",
        "fromMe": False,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        logger.info(f"Status da resposta: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Mensagem simulada processada com sucesso!")
            logger.info(f"   Resposta: {data}")
        else:
            logger.error(f"❌ Erro ao processar mensagem simulada: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem simulada: {str(e)}")

def test_send_message():
    """Testa o envio de uma mensagem via Z-API"""
    logger.info("\n=== TESTANDO ENVIO DE MENSAGEM VIA Z-API ===")
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone": "5531999999999",
        "message": "Teste de mensagem via Z-API - " + datetime.now().strftime("%H:%M:%S")
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Mensagem enviada com sucesso!")
            logger.info(f"   ID: {data.get('id', 'N/A')}")
            logger.info(f"   Status: {data.get('status', 'N/A')}")
        else:
            logger.error(f"❌ Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {str(e)}")

def main():
    """Executa todos os testes"""
    try:
        test_vercel_endpoints()
        test_zapi_instance_status()
        test_zapi_webhook_config()
        configure_zapi_webhook()
        test_webhook_message()
        test_send_message()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DIAGNÓSTICO CONCLUÍDO")
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        logger.info("1. Verifique se o WhatsApp está conectado no Z-API")
        logger.info("2. Envie uma mensagem para o número da clínica")
        logger.info("3. Verifique os logs do Vercel para ver se a mensagem chegou")
        logger.info("4. Se não funcionar, verifique as variáveis de ambiente")
        
    except Exception as e:
        logger.error(f"❌ Erro no diagnóstico: {str(e)}")

if __name__ == "__main__":
    main() 