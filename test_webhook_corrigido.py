#!/usr/bin/env python3
"""
Teste específico do webhook após correções
"""

import asyncio
import httpx
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def testar_webhook_corrigido():
    """Testa o webhook após as correções"""
    
    vercel_url = "https://chatbot-clincia.vercel.app"
    
    # Simular mensagem real do WhatsApp
    mensagem_teste = {
        "event": "message",
        "data": {
            "id": f"test_{int(datetime.now().timestamp())}",
            "from": "5511999999999@c.us",
            "to": "5511888888888@c.us",
            "type": "text",
            "text": {
                "body": "oi"
            },
            "fromMe": False,
            "timestamp": int(datetime.now().timestamp())
        }
    }
    
    logger.info("=== TESTANDO WEBHOOK CORRIGIDO ===")
    logger.info(f"URL: {vercel_url}/webhook")
    logger.info(f"Mensagem: {json.dumps(mensagem_teste, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar endpoint sem barra final
            response = await client.post(
                f"{vercel_url}/webhook",
                json=mensagem_teste,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
            
            if response.status_code == 200:
                logger.info("✅ Webhook funcionando corretamente!")
                return True
            else:
                logger.error("❌ Webhook ainda com problemas")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False

async def testar_envio_mensagem_real():
    """Testa envio de mensagem real via Z-API"""
    
    logger.info("=== TESTANDO ENVIO DE MENSAGEM REAL ===")
    
    zapi_config = {
        "instance_id": "VARIABLE_FROM_ENV",
        "token": "VARIABLE_FROM_ENV",
        "client_token": "VARIABLE_FROM_ENV",
        "base_url": "https://api.z-api.io"
    }
    
    try:
        base_url = f"{zapi_config['base_url']}/instances/{zapi_config['instance_id']}/token/{zapi_config['token']}"
        headers = {
            "Client-Token": zapi_config['client_token'],
            "Content-Type": "application/json"
        }
        
        # Enviar mensagem de teste
        payload = {
            "phone": "5511999999999",
            "message": "Teste do webhook - se você receber esta mensagem, o sistema está funcionando! 🎉"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/send-text",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            logger.info(f"Status do envio: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
            
            if response.status_code == 200:
                logger.info("✅ Mensagem enviada com sucesso!")
                return True
            else:
                logger.error("❌ Erro ao enviar mensagem")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro no envio: {str(e)}")
        return False

async def main():
    """Executa todos os testes"""
    
    logger.info("🚀 INICIANDO TESTES DO WEBHOOK CORRIGIDO")
    logger.info("=" * 50)
    
    # Teste 1: Webhook corrigido
    webhook_ok = await testar_webhook_corrigido()
    logger.info("")
    
    # Teste 2: Envio de mensagem real
    envio_ok = await testar_envio_mensagem_real()
    logger.info("")
    
    logger.info("=" * 50)
    logger.info("📊 RESULTADOS DOS TESTES:")
    logger.info(f"Webhook: {'✅ OK' if webhook_ok else '❌ FALHOU'}")
    logger.info(f"Envio: {'✅ OK' if envio_ok else '❌ FALHOU'}")
    
    if webhook_ok and envio_ok:
        logger.info("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        logger.info("")
        logger.info("📱 PRÓXIMOS PASSOS:")
        logger.info("1. Envie uma mensagem para o WhatsApp da clínica")
        logger.info("2. O bot deve responder com o menu principal")
        logger.info("3. Teste todas as funcionalidades")
    else:
        logger.info("⚠️  Ainda há problemas para resolver")

if __name__ == "__main__":
    asyncio.run(main()) 