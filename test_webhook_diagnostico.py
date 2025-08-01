#!/usr/bin/env python3
"""
Script de diagnóstico completo para o webhook do WhatsApp
Testa todos os componentes do sistema para identificar problemas
"""

import os
import sys
import json
import asyncio
import httpx
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebhookDiagnostico:
    def __init__(self):
        self.vercel_url = "https://chatbot-clincia.vercel.app"
        self.zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
        self.zapi_token = os.getenv("ZAPI_TOKEN", "")
        self.zapi_client_token = os.getenv("ZAPI_TOKEN", "")
        self.zapi_base_url = "https://api.z-api.io"
        
    async def testar_vercel_endpoints(self):
        """Testa todos os endpoints do Vercel"""
        logger.info("=== TESTANDO ENDPOINTS DO VERCEL ===")
        
        endpoints = [
            "/",
            "/webhook",
            "/webhook/",
            "/webhook/test",
            "/webhook/health",
            "/webhook/status-info"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.vercel_url}{endpoint}", timeout=10.0)
                    logger.info(f"✅ {endpoint}: {response.status_code}")
                    if response.status_code != 200:
                        logger.warning(f"   Resposta: {response.text[:200]}")
            except Exception as e:
                logger.error(f"❌ {endpoint}: {str(e)}")
    
    async def testar_webhook_configuracao(self):
        """Testa a configuração do webhook no Z-API"""
        logger.info("=== TESTANDO CONFIGURAÇÃO DO WEBHOOK NO Z-API ===")
        
        try:
            base_url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}"
            headers = {
                "Client-Token": self.zapi_client_token,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Verificar webhook atual
                response = await client.get(f"{base_url}/webhook", headers=headers)
                
                if response.status_code == 200:
                    webhook_info = response.json()
                    logger.info("✅ Webhook configurado:")
                    logger.info(f"   URL: {webhook_info.get('webhook', 'N/A')}")
                    logger.info(f"   Ativo: {webhook_info.get('enabled', 'N/A')}")
                    logger.info(f"   Eventos: {webhook_info.get('events', 'N/A')}")
                else:
                    logger.error(f"❌ Erro ao verificar webhook: {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar configuração do webhook: {str(e)}")
    
    async def configurar_webhook_correto(self):
        """Configura o webhook corretamente no Z-API"""
        logger.info("=== CONFIGURANDO WEBHOOK CORRETAMENTE ===")
        
        try:
            base_url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}"
            headers = {
                "Client-Token": self.zapi_client_token,
                "Content-Type": "application/json"
            }
            
            # Configuração completa do webhook
            webhook_config = {
                "webhook": f"{self.vercel_url}/webhook",
                "webhookByEvents": True,
                "webhookBase64": False,
                "events": [
                    "message",
                    "message-status", 
                    "connection-status"
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{base_url}/webhook", json=webhook_config, headers=headers)
                
                if response.status_code == 200:
                    logger.info("✅ Webhook configurado com sucesso!")
                    logger.info(f"   URL: {self.vercel_url}/webhook")
                else:
                    logger.error(f"❌ Erro ao configurar webhook: {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook: {str(e)}")
    
    async def testar_envio_mensagem_simulada(self):
        """Testa o envio de uma mensagem simulada para o webhook"""
        logger.info("=== TESTANDO ENVIO DE MENSAGEM SIMULADA ===")
        
        # Simular mensagem do WhatsApp
        mensagem_simulada = {
            "event": "message",
            "data": {
                "id": "test_message_id",
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
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.vercel_url}/webhook",
                    json=mensagem_simulada,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                logger.info(f"Status da resposta: {response.status_code}")
                logger.info(f"Resposta: {response.text}")
                
                if response.status_code == 200:
                    logger.info("✅ Mensagem simulada processada com sucesso!")
                else:
                    logger.error("❌ Erro ao processar mensagem simulada")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar mensagem simulada: {str(e)}")
    
    async def verificar_instancia_zapi(self):
        """Verifica o status da instância do Z-API"""
        logger.info("=== VERIFICANDO STATUS DA INSTÂNCIA Z-API ===")
        
        try:
            base_url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}"
            headers = {
                "Client-Token": self.zapi_client_token,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/status", headers=headers)
                
                if response.status_code == 200:
                    status_info = response.json()
                    logger.info("✅ Status da instância:")
                    logger.info(f"   Conectado: {status_info.get('connected', 'N/A')}")
                    logger.info(f"   Status: {status_info.get('status', 'N/A')}")
                    logger.info(f"   QR Code: {status_info.get('qrcode', 'N/A')}")
                else:
                    logger.error(f"❌ Erro ao verificar status: {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar instância: {str(e)}")
    
    async def executar_diagnostico_completo(self):
        """Executa diagnóstico completo do sistema"""
        logger.info("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO WEBHOOK")
        logger.info("=" * 60)
        
        # 1. Testar endpoints do Vercel
        await self.testar_vercel_endpoints()
        logger.info("")
        
        # 2. Verificar instância do Z-API
        await self.verificar_instancia_zapi()
        logger.info("")
        
        # 3. Verificar configuração atual do webhook
        await self.testar_webhook_configuracao()
        logger.info("")
        
        # 4. Configurar webhook corretamente
        await self.configurar_webhook_correto()
        logger.info("")
        
        # 5. Testar mensagem simulada
        await self.testar_envio_mensagem_simulada()
        logger.info("")
        
        logger.info("=" * 60)
        logger.info("✅ DIAGNÓSTICO CONCLUÍDO")
        logger.info("")
        logger.info("📋 PRÓXIMOS PASSOS:")
        logger.info("1. Verifique se o WhatsApp está conectado no Z-API")
        logger.info("2. Envie uma mensagem para o número da clínica")
        logger.info("3. Verifique os logs do Vercel para ver se a mensagem chegou")
        logger.info("4. Se não funcionar, verifique as variáveis de ambiente")

async def main():
    diagnostico = WebhookDiagnostico()
    await diagnostico.executar_diagnostico_completo()

if __name__ == "__main__":
    asyncio.run(main()) 