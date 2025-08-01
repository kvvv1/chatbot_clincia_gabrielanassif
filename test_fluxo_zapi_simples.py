#!/usr/bin/env python3
"""
TESTE SIMPLES DO FLUXO Z-API
Testa apenas o fluxo principal de conversa do chatbot
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime, timedelta
import time

# Configurar logging simples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TesteFluxoZAPISimples:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.base_url}/webhook"
        
        # Dados de teste
        self.test_phone = "5531999999999"
        
        # Resultados
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
    
    def log_resultado(self, nome: str, sucesso: bool, detalhes: str = ""):
        """Registra resultado de um teste"""
        if sucesso:
            self.sucessos += 1
            logger.info(f"SUCESSO - {nome}: {detalhes}")
        else:
            self.falhas += 1
            self.erros.append(f"{nome}: {detalhes}")
            logger.error(f"FALHA - {nome}: {detalhes}")
    
    async def test_webhook_health(self):
        """Testa saúde do webhook"""
        logger.info("Testando saúde do webhook...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.webhook_url}/health")
                sucesso = response.status_code == 200
                self.log_resultado("Webhook Health", sucesso, f"Status: {response.status_code}")
            except Exception as e:
                self.log_resultado("Webhook Health", False, f"Erro: {str(e)}")
    
    async def test_conversation_flow(self):
        """Testa fluxo completo de conversa"""
        logger.info("Testando fluxo completo de conversa...")
        
        # Sequência de mensagens para testar
        messages = [
            "oi",
            "quero agendar",
            "12345678901",
            "João Silva",
            "1"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, message in enumerate(messages, 1):
                message_data = {
                    "event": "message",
                    "data": {
                        "id": f"test_message_{i:03d}",
                        "from": self.test_phone,
                        "to": "553198600366",
                        "type": "text",
                        "text": {
                            "body": message
                        },
                        "timestamp": int(time.time()),
                        "chatId": f"{self.test_phone}@c.us"
                    }
                }
                
                try:
                    response = await client.post(
                        f"{self.webhook_url}/message",
                        json=message_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        self.log_resultado(
                            f"Conversação Step {i}", 
                            True, 
                            f"Mensagem: '{message}' - Resposta: {response_data.get('status', 'N/A')}"
                        )
                    else:
                        self.log_resultado(
                            f"Conversação Step {i}", 
                            False, 
                            f"Mensagem: '{message}' - Status: {response.status_code}"
                        )
                except Exception as e:
                    self.log_resultado(
                        f"Conversação Step {i}", 
                        False, 
                        f"Mensagem: '{message}' - Erro: {str(e)}"
                    )
                
                # Aguardar entre mensagens
                await asyncio.sleep(1)
    
    async def test_dashboard_conversations(self):
        """Testa listagem de conversas"""
        logger.info("Testando listagem de conversas...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.base_url}/dashboard/conversations")
                if response.status_code == 200:
                    data = response.json()
                    conversations = data.get('conversations', [])
                    self.log_resultado(
                        "Dashboard Conversations", 
                        True, 
                        f"Conversas encontradas: {len(conversations)}"
                    )
                else:
                    self.log_resultado("Dashboard Conversations", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_resultado("Dashboard Conversations", False, f"Erro: {str(e)}")
    
    async def run_test(self):
        """Executa todos os testes"""
        logger.info("INICIANDO TESTE SIMPLES DO FLUXO Z-API")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # Executar testes
        await self.test_webhook_health()
        await self.test_conversation_flow()
        await self.test_dashboard_conversations()
        
        # Calcular resultados
        end_time = time.time()
        duration = end_time - start_time
        total_tests = self.sucessos + self.falhas
        taxa_sucesso = (self.sucessos / total_tests * 100) if total_tests > 0 else 0
        
        # Exibir resumo
        logger.info("=" * 50)
        logger.info("RESUMO DO TESTE")
        logger.info(f"Sucessos: {self.sucessos}")
        logger.info(f"Falhas: {self.falhas}")
        logger.info(f"Taxa de Sucesso: {taxa_sucesso:.1f}%")
        logger.info(f"Duração: {duration:.2f} segundos")
        
        if self.erros:
            logger.info("ERROS DETECTADOS:")
            for erro in self.erros:
                logger.error(f"  - {erro}")
        
        # Salvar resultados
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "sucessos": self.sucessos,
            "falhas": self.falhas,
            "taxa_sucesso": taxa_sucesso,
            "duracao": duration,
            "erros": self.erros
        }
        
        with open("test_fluxo_zapi_simples_results.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        logger.info("Resultados salvos em: test_fluxo_zapi_simples_results.json")
        
        return resultados

async def main():
    """Função principal"""
    tester = TesteFluxoZAPISimples()
    results = await tester.run_test()
    
    if results["falhas"] == 0:
        logger.info("TODOS OS TESTES PASSARAM!")
        return 0
    else:
        logger.warning("ALGUNS TESTES FALHARAM!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 