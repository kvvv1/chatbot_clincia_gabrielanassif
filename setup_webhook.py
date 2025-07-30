#!/usr/bin/env python3
"""
Script para configurar automaticamente o webhook no Z-API
Configura a URL do webhook para receber mensagens do WhatsApp
"""

import os
import sys
import json
import asyncio
import httpx
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebhookSetup:
    def __init__(self):
        self.zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID", "3E4F7360B552F0C2DBCB9E6774402775")
        self.zapi_token = os.getenv("ZAPI_TOKEN", "17829E98BB59E9ADD55BBBA9")
        self.zapi_client_token = os.getenv("ZAPI_CLIENT_TOKEN", "F909fc109aad54566bf42a6d09f00a8dbS")
        self.zapi_base_url = os.getenv("ZAPI_BASE_URL", "https://api.z-api.io")
        self.webhook_url = os.getenv("WEBHOOK_URL", "")
        
        if not self.webhook_url:
            logger.error("❌ URL do webhook não configurada!")
            logger.info("Configure a variável de ambiente WEBHOOK_URL")
            logger.info("Exemplo: WEBHOOK_URL=https://seu-app.vercel.app/webhook")
            sys.exit(1)
        
        self.base_url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}"
        self.headers = {
            "Client-Token": self.zapi_client_token,
            "Content-Type": "application/json"
        }
    
    async def test_zapi_connection(self) -> bool:
        """Testa conexão com Z-API"""
        logger.info("=== TESTANDO CONEXÃO Z-API ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Z-API conectado - Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Erro na conexão Z-API: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Z-API: {str(e)}")
            return False
    
    async def test_webhook_url(self) -> bool:
        """Testa se a URL do webhook está acessível"""
        logger.info("=== TESTANDO URL DO WEBHOOK ===")
        
        try:
            async with httpx.AsyncClient() as client:
                # Teste GET
                response = await client.get(self.webhook_url, timeout=10.0)
                
                if response.status_code == 200:
                    logger.info("✅ URL do webhook está acessível")
                    
                    # Teste POST
                    test_data = {
                        "event": "test",
                        "data": {"message": "test"}
                    }
                    
                    response = await client.post(
                        self.webhook_url,
                        json=test_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        logger.info("✅ Webhook está processando requisições")
                        return True
                    else:
                        logger.warning(f"⚠️ Webhook retornou status: {response.status_code}")
                        return False
                else:
                    logger.warning(f"⚠️ URL do webhook retornou: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar webhook: {str(e)}")
            return False
    
    async def get_current_webhook(self) -> Optional[Dict]:
        """Obtém configuração atual do webhook"""
        logger.info("=== OBTENDO CONFIGURAÇÃO ATUAL DO WEBHOOK ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/webhook",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Configuração atual obtida: {data.get('url', 'N/A')}")
                    return data
                else:
                    logger.warning(f"⚠️ Erro ao obter configuração: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter configuração: {str(e)}")
            return None
    
    async def set_webhook(self) -> bool:
        """Configura o webhook no Z-API"""
        logger.info("=== CONFIGURANDO WEBHOOK NO Z-API ===")
        
        webhook_config = {
            "url": self.webhook_url,
            "enabled": True,
            "events": [
                "message",
                "message-status",
                "connection-status"
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/webhook",
                    headers=self.headers,
                    json=webhook_config,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Webhook configurado com sucesso")
                    logger.info(f"   URL: {data.get('url', 'N/A')}")
                    logger.info(f"   Status: {data.get('enabled', 'N/A')}")
                    return True
                else:
                    logger.error(f"❌ Erro ao configurar webhook: {response.status_code}")
                    logger.error(f"   Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook: {str(e)}")
            return False
    
    async def update_webhook(self) -> bool:
        """Atualiza configuração do webhook"""
        logger.info("=== ATUALIZANDO CONFIGURAÇÃO DO WEBHOOK ===")
        
        webhook_config = {
            "url": self.webhook_url,
            "enabled": True,
            "events": [
                "message",
                "message-status",
                "connection-status"
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/webhook",
                    headers=self.headers,
                    json=webhook_config,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Webhook atualizado com sucesso")
                    logger.info(f"   URL: {data.get('url', 'N/A')}")
                    return True
                else:
                    logger.error(f"❌ Erro ao atualizar webhook: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar webhook: {str(e)}")
            return False
    
    async def test_webhook_delivery(self) -> bool:
        """Testa entrega de mensagem via webhook"""
        logger.info("=== TESTANDO ENTREGA DE MENSAGEM ===")
        
        test_message = {
            "phone": "553198600366",
            "message": "Teste de webhook - " + str(asyncio.get_event_loop().time())
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/send-text",
                    headers=self.headers,
                    json=test_message,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Mensagem de teste enviada")
                    logger.info("   Verifique se o webhook recebeu a mensagem")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {str(e)}")
            return False
    
    async def get_instance_info(self) -> Optional[Dict]:
        """Obtém informações da instância"""
        logger.info("=== OBTENDO INFORMAÇÕES DA INSTÂNCIA ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/instance",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Instância: {data.get('name', 'N/A')}")
                    logger.info(f"   Status: {data.get('status', 'N/A')}")
                    logger.info(f"   WhatsApp: {data.get('whatsapp', {}).get('status', 'N/A')}")
                    return data
                else:
                    logger.warning(f"⚠️ Erro ao obter informações: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações: {str(e)}")
            return None
    
    async def run_setup(self):
        """Executa todo o setup do webhook"""
        logger.info("🚀 INICIANDO SETUP DO WEBHOOK Z-API")
        logger.info("=" * 50)
        logger.info(f"URL do Webhook: {self.webhook_url}")
        logger.info("=" * 50)
        
        # Testar conexão Z-API
        if not await self.test_zapi_connection():
            logger.error("❌ Falha na conexão com Z-API")
            return False
        
        # Obter informações da instância
        await self.get_instance_info()
        
        # Testar URL do webhook
        if not await self.test_webhook_url():
            logger.warning("⚠️ URL do webhook pode não estar funcionando")
        
        # Obter configuração atual
        current_config = await self.get_current_webhook()
        
        if current_config and current_config.get('url') == self.webhook_url:
            logger.info("✅ Webhook já está configurado corretamente")
            
            # Atualizar configuração para garantir
            await self.update_webhook()
        else:
            logger.info("🔄 Configurando novo webhook")
            await self.set_webhook()
        
        # Testar entrega
        await self.test_webhook_delivery()
        
        logger.info("=" * 50)
        logger.info("🎉 SETUP DO WEBHOOK CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info("📝 PRÓXIMOS PASSOS:")
        logger.info("1. Verifique se as mensagens estão chegando no webhook")
        logger.info("2. Teste o sistema completo")
        logger.info("3. Monitore os logs da aplicação")
        
        return True

async def main():
    """Função principal"""
    setup = WebhookSetup()
    await setup.run_setup()

if __name__ == "__main__":
    asyncio.run(main()) 