#!/usr/bin/env python3
"""
DIAGNÓSTICO Z-API PRODUÇÃO
Verifica problemas na configuração do Z-API que podem estar causando falhas em produção
"""

import os
import httpx
import asyncio
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagnosticoZAPI:
    def __init__(self):
        # Configurações da imagem
        self.zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
        self.zapi_token = os.getenv("ZAPI_TOKEN", "")
        self.zapi_client_token = os.getenv("ZAPI_TOKEN", "")
        self.zapi_base_url = "https://api.z-api.io"
        
        # URL de produção
        self.vercel_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.vercel_url}/webhook"
        
        self.headers = {
            "Client-Token": self.zapi_client_token,
            "Content-Type": "application/json"
        }
    
    async def verificar_configuracao_atual(self):
        """Verifica a configuração atual no Z-API"""
        logger.info("🔍 VERIFICANDO CONFIGURAÇÃO ATUAL DO Z-API")
        
        try:
            url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}/webhook"
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Configuração atual obtida com sucesso")
                    logger.info(f"📋 Dados: {json.dumps(data, indent=2)}")
                    return data
                else:
                    logger.error(f"❌ Erro ao obter configuração: {response.status_code}")
                    logger.error(f"Resposta: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar configuração: {str(e)}")
            return None
    
    async def verificar_webhook_url(self):
        """Verifica se a URL do webhook está acessível"""
        logger.info("🌐 VERIFICANDO ACESSIBILIDADE DO WEBHOOK")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Testar endpoint de saúde
                health_url = f"{self.webhook_url}/health"
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    logger.info("✅ Webhook está acessível")
                    logger.info(f"📡 Health check: {response.json()}")
                    return True
                else:
                    logger.error(f"❌ Webhook não está respondendo: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao acessar webhook: {str(e)}")
            return False
    
    async def testar_envio_mensagem(self):
        """Testa o envio de mensagem via Z-API"""
        logger.info("📤 TESTANDO ENVIO DE MENSAGEM")
        
        try:
            url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}/send-text"
            
            payload = {
                "phone": "553198600366",
                "message": "🔧 Teste de diagnóstico - " + datetime.now().strftime("%H:%M:%S"),
                "delayMessage": 2
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Mensagem enviada com sucesso")
                    logger.info(f"📋 Resposta: {json.dumps(data, indent=2)}")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
                    logger.error(f"Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar envio: {str(e)}")
            return False
    
    async def configurar_webhook_correto(self):
        """Configura o webhook com a URL correta"""
        logger.info("🔧 CONFIGURANDO WEBHOOK CORRETO")
        
        try:
            url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}/webhook"
            
            payload = {
                "webhook": self.webhook_url,
                "webhookByEvents": False,
                "webhookBase64": False
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Webhook configurado com sucesso")
                    logger.info(f"📋 Resposta: {json.dumps(data, indent=2)}")
                    return True
                else:
                    logger.error(f"❌ Erro ao configurar webhook: {response.status_code}")
                    logger.error(f"Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook: {str(e)}")
            return False
    
    async def verificar_status_instancia(self):
        """Verifica o status da instância"""
        logger.info("📊 VERIFICANDO STATUS DA INSTÂNCIA")
        
        try:
            url = f"{self.zapi_base_url}/instances/{self.zapi_instance_id}/token/{self.zapi_token}/status"
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Status da instância obtido")
                    logger.info(f"📋 Status: {json.dumps(data, indent=2)}")
                    return data
                else:
                    logger.error(f"❌ Erro ao obter status: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status: {str(e)}")
            return None
    
    async def executar_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        logger.info("🚀 INICIANDO DIAGNÓSTICO COMPLETO Z-API")
        logger.info("=" * 60)
        
        # 1. Verificar configuração atual
        config_atual = await self.verificar_configuracao_atual()
        
        # 2. Verificar acessibilidade do webhook
        webhook_ok = await self.verificar_webhook_url()
        
        # 3. Verificar status da instância
        status = await self.verificar_status_instancia()
        
        # 4. Testar envio de mensagem
        envio_ok = await self.testar_envio_mensagem()
        
        # 5. Se webhook não estiver configurado, configurar
        if config_atual and not config_atual.get('webhook'):
            logger.info("⚠️ Webhook não configurado, configurando...")
            await self.configurar_webhook_correto()
        
        # 6. Relatório final
        logger.info("=" * 60)
        logger.info("📋 RELATÓRIO FINAL")
        logger.info(f"✅ Configuração atual: {'OK' if config_atual else 'ERRO'}")
        logger.info(f"✅ Webhook acessível: {'OK' if webhook_ok else 'ERRO'}")
        logger.info(f"✅ Status instância: {'OK' if status else 'ERRO'}")
        logger.info(f"✅ Envio mensagem: {'OK' if envio_ok else 'ERRO'}")
        
        if not webhook_ok:
            logger.error("🚨 PROBLEMA CRÍTICO: Webhook não está acessível")
            logger.error("💡 Solução: Verificar se o Vercel está funcionando")
        
        if not envio_ok:
            logger.error("🚨 PROBLEMA CRÍTICO: Não é possível enviar mensagens")
            logger.error("💡 Solução: Verificar tokens e configuração do Z-API")

async def main():
    diagnostico = DiagnosticoZAPI()
    await diagnostico.executar_diagnostico_completo()

if __name__ == "__main__":
    asyncio.run(main()) 