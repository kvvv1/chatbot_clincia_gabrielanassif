#!/usr/bin/env python3
"""
TESTE WEBHOOK MENSAGEM REAL - Z-API
Simula uma mensagem real do Z-API para verificar se o webhook está funcionando
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TesteWebhookMensagemReal:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.base_url}/webhook"
        
        # Dados de teste
        self.test_phone = "5531999999999"
        self.test_message_id = "test_msg_123"
        
        # Resultados
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
    
    def log_resultado(self, teste: str, sucesso: bool, detalhes: str = ""):
        """Registra resultado do teste"""
        if sucesso:
            self.sucessos += 1
            logger.info(f"✅ {teste}: {detalhes}")
        else:
            self.falhas += 1
            logger.error(f"❌ {teste}: {detalhes}")
            self.erros.append(f"{teste}: {detalhes}")
    
    async def test_webhook_health(self):
        """Testa saúde do webhook"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.webhook_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_resultado("Webhook Health", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_resultado("Webhook Health", False, f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.log_resultado("Webhook Health", False, str(e))
            return False
    
    async def test_mensagem_simples(self, mensagem: str):
        """Testa envio de mensagem simples"""
        try:
            # Simular payload do Z-API
            payload = {
                "phone": f"{self.test_phone}@c.us",
                "text": {
                    "message": mensagem
                },
                "messageId": f"{self.test_message_id}_{int(time.time())}",
                "fromMe": False,
                "timestamp": int(time.time())
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Z-API/1.0"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.webhook_url}/message",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_resultado(f"Mensagem '{mensagem}'", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_resultado(f"Mensagem '{mensagem}'", False, f"Status: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            self.log_resultado(f"Mensagem '{mensagem}'", False, str(e))
            return False
    
    async def test_fluxo_completo(self):
        """Testa fluxo completo de conversa"""
        mensagens_teste = [
            "oi",
            "1",
            "12345678901",
            "João Silva",
            "sim"
        ]
        
        logger.info("🔄 Iniciando teste de fluxo completo...")
        
        for i, mensagem in enumerate(mensagens_teste, 1):
            logger.info(f"📝 Testando mensagem {i}/{len(mensagens_teste)}: '{mensagem}'")
            await self.test_mensagem_simples(mensagem)
            
            # Aguardar entre mensagens
            if i < len(mensagens_teste):
                await asyncio.sleep(2)
    
    async def test_webhook_principal(self):
        """Testa webhook principal"""
        try:
            payload = {
                "phone": f"{self.test_phone}@c.us",
                "text": {
                    "message": "teste webhook principal"
                },
                "messageId": f"test_principal_{int(time.time())}",
                "fromMe": False
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_resultado("Webhook Principal", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_resultado("Webhook Principal", False, f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.log_resultado("Webhook Principal", False, str(e))
            return False
    
    async def executar_testes(self):
        """Executa todos os testes"""
        logger.info("🚀 Iniciando testes do webhook Z-API")
        logger.info(f"📡 URL do webhook: {self.webhook_url}")
        
        # Teste 1: Health check
        await self.test_webhook_health()
        await asyncio.sleep(1)
        
        # Teste 2: Webhook principal
        await self.test_webhook_principal()
        await asyncio.sleep(1)
        
        # Teste 3: Fluxo completo
        await self.test_fluxo_completo()
        
        # Resultados
        total = self.sucessos + self.falhas
        taxa_sucesso = (self.sucessos / total * 100) if total > 0 else 0
        
        logger.info("=" * 50)
        logger.info("📊 RESULTADOS DOS TESTES")
        logger.info("=" * 50)
        logger.info(f"✅ Sucessos: {self.sucessos}")
        logger.info(f"❌ Falhas: {self.falhas}")
        logger.info(f"📈 Taxa de Sucesso: {taxa_sucesso:.1f}%")
        
        if self.erros:
            logger.info("🔍 Erros encontrados:")
            for erro in self.erros:
                logger.error(f"   - {erro}")
        
        # Salvar resultados
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "sucessos": self.sucessos,
            "falhas": self.falhas,
            "taxa_sucesso": taxa_sucesso,
            "erros": self.erros
        }
        
        with open("test_webhook_mensagem_real_results.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Resultados salvos em: test_webhook_mensagem_real_results.json")
        
        return self.sucessos > 0

async def main():
    """Função principal"""
    tester = TesteWebhookMensagemReal()
    sucesso = await tester.executar_testes()
    
    if sucesso:
        logger.info("🎉 Testes concluídos com sucesso!")
    else:
        logger.error("💥 Testes falharam!")

if __name__ == "__main__":
    asyncio.run(main()) 