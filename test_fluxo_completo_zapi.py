#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DO FLUXO Z-API
Testa todo o fluxo de conversa do chatbot, desde o envio da mensagem
até a resposta completa, incluindo integrações com GestãoDS.
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime
import time
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_fluxo_zapi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TesteFluxoZAPI:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.base_url}/webhook"
        self.dashboard_url = f"{self.base_url}/dashboard"
        
        # Dados de teste
        self.test_phone = "5531999999999"
        self.test_name = "João Silva"
        self.test_cpf = "12345678901"
        
        # Resultados do teste
        self.test_results = {
            "inicio": datetime.now().isoformat(),
            "testes": [],
            "erros": [],
            "sucessos": 0,
            "falhas": 0
        }
    
    def log_test(self, nome: str, status: str, detalhes: str = "", dados: Dict = None):
        """Registra resultado de um teste"""
        resultado = {
            "nome": nome,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "detalhes": detalhes,
            "dados": dados or {}
        }
        
        self.test_results["testes"].append(resultado)
        
        if status == "SUCESSO":
            self.test_results["sucessos"] += 1
            logger.info(f"✅ {nome}: {detalhes}")
        else:
            self.test_results["falhas"] += 1
            self.test_results["erros"].append(resultado)
            logger.error(f"❌ {nome}: {detalhes}")
    
    async def test_health_endpoints(self):
        """Testa endpoints de saúde"""
        logger.info("🔍 Testando endpoints de saúde...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Teste webhook health
            try:
                response = await client.get(f"{self.webhook_url}/health")
                if response.status_code == 200:
                    self.log_test("Webhook Health", "SUCESSO", f"Status: {response.status_code}")
                else:
                    self.log_test("Webhook Health", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Webhook Health", "FALHA", f"Erro: {str(e)}")
            
            # Teste dashboard health
            try:
                response = await client.get(f"{self.dashboard_url}/health")
                if response.status_code == 200:
                    self.log_test("Dashboard Health", "SUCESSO", f"Status: {response.status_code}")
                else:
                    self.log_test("Dashboard Health", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Dashboard Health", "FALHA", f"Erro: {str(e)}")
    
    async def test_webhook_message_simulation(self):
        """Simula envio de mensagem via webhook"""
        logger.info("📨 Simulando envio de mensagem via webhook...")
        
        # Simular mensagem de "oi"
        message_data = {
            "event": "message",
            "data": {
                "id": "test_message_001",
                "from": self.test_phone,
                "to": "553198600366",
                "type": "text",
                "text": {
                    "body": "oi"
                },
                "timestamp": int(time.time()),
                "chatId": f"{self.test_phone}@c.us"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.webhook_url}/message",
                    json=message_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    self.log_test(
                        "Webhook Message Simulation", 
                        "SUCESSO", 
                        f"Resposta recebida: {response_data.get('status', 'N/A')}",
                        {"request": message_data, "response": response_data}
                    )
                else:
                    self.log_test(
                        "Webhook Message Simulation", 
                        "FALHA", 
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                self.log_test("Webhook Message Simulation", "FALHA", f"Erro: {str(e)}")
    
    async def test_gestaods_integration(self):
        """Testa integração com GestãoDS"""
        logger.info("🏥 Testando integração com GestãoDS...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Teste widget
            try:
                response = await client.get(f"{self.dashboard_url}/gestaods/widget")
                if response.status_code == 200:
                    widget_data = response.json()
                    self.log_test(
                        "GestãoDS Widget", 
                        "SUCESSO", 
                        f"Widget carregado: {widget_data.get('status', 'N/A')}",
                        widget_data
                    )
                else:
                    self.log_test("GestãoDS Widget", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GestãoDS Widget", "FALHA", f"Erro: {str(e)}")
            
            # Teste busca de horários
            try:
                from datetime import timedelta
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                response = await client.get(f"{self.dashboard_url}/gestaods/slots/{tomorrow}")
                if response.status_code == 200:
                    slots_data = response.json()
                    self.log_test(
                        "GestãoDS Slots", 
                        "SUCESSO", 
                        f"Horários encontrados: {len(slots_data.get('slots', []))}",
                        slots_data
                    )
                else:
                    self.log_test("GestãoDS Slots", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GestãoDS Slots", "FALHA", f"Erro: {str(e)}")
    
    async def test_conversation_flow(self):
        """Testa fluxo completo de conversa"""
        logger.info("💬 Testando fluxo completo de conversa...")
        
        # Simular sequência de mensagens
        conversation_steps = [
            {"message": "oi", "expected_response": "Olá"},
            {"message": "quero agendar", "expected_response": "agendamento"},
            {"message": "12345678901", "expected_response": "CPF"},
            {"message": "João Silva", "expected_response": "nome"},
            {"message": "1", "expected_response": "opção"}
        ]
        
        for i, step in enumerate(conversation_steps):
            message_data = {
                "event": "message",
                "data": {
                    "id": f"test_message_{i+1:03d}",
                    "from": self.test_phone,
                    "to": "553198600366",
                    "type": "text",
                    "text": {
                        "body": step["message"]
                    },
                    "timestamp": int(time.time()),
                    "chatId": f"{self.test_phone}@c.us"
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        f"{self.webhook_url}/message",
                        json=message_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        self.log_test(
                            f"Conversação Step {i+1}", 
                            "SUCESSO", 
                            f"Mensagem: '{step['message']}' - Resposta: {response_data.get('status', 'N/A')}",
                            {"step": i+1, "message": step["message"], "response": response_data}
                        )
                    else:
                        self.log_test(
                            f"Conversação Step {i+1}", 
                            "FALHA", 
                            f"Mensagem: '{step['message']}' - Status: {response.status_code}"
                        )
                except Exception as e:
                    self.log_test(
                        f"Conversação Step {i+1}", 
                        "FALHA", 
                        f"Mensagem: '{step['message']}' - Erro: {str(e)}"
                    )
            
            # Aguardar um pouco entre as mensagens
            await asyncio.sleep(1)
    
    async def test_websocket_connection(self):
        """Testa conexão WebSocket"""
        logger.info("🔌 Testando conexão WebSocket...")
        
        try:
            import websockets
            uri = f"wss://chatbot-clincia.vercel.app/dashboard/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Enviar mensagem de teste
                await websocket.send(json.dumps({
                    "type": "test",
                    "message": "Teste de conexão WebSocket"
                }))
                
                # Aguardar resposta
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                self.log_test(
                    "WebSocket Connection", 
                    "SUCESSO", 
                    f"Conexão estabelecida e resposta recebida",
                    {"response": response_data}
                )
                
        except Exception as e:
            self.log_test("WebSocket Connection", "FALHA", f"Erro: {str(e)}")
    
    async def test_dashboard_endpoints(self):
        """Testa endpoints do dashboard"""
        logger.info("📊 Testando endpoints do dashboard...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Teste listagem de conversas
            try:
                response = await client.get(f"{self.dashboard_url}/conversations")
                if response.status_code == 200:
                    conversations = response.json()
                    self.log_test(
                        "Dashboard Conversations", 
                        "SUCESSO", 
                        f"Conversas encontradas: {len(conversations.get('conversations', []))}",
                        conversations
                    )
                else:
                    self.log_test("Dashboard Conversations", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Dashboard Conversations", "FALHA", f"Erro: {str(e)}")
            
            # Teste analytics
            try:
                response = await client.get(f"{self.dashboard_url}/analytics")
                if response.status_code == 200:
                    analytics = response.json()
                    self.log_test(
                        "Dashboard Analytics", 
                        "SUCESSO", 
                        f"Analytics carregados",
                        analytics
                    )
                else:
                    self.log_test("Dashboard Analytics", "FALHA", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Dashboard Analytics", "FALHA", f"Erro: {str(e)}")
    
    async def run_complete_test(self):
        """Executa todos os testes"""
        logger.info("🚀 INICIANDO TESTE COMPLETO DO FLUXO Z-API")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Executar todos os testes
        await self.test_health_endpoints()
        await self.test_webhook_message_simulation()
        await self.test_gestaods_integration()
        await self.test_conversation_flow()
        await self.test_websocket_connection()
        await self.test_dashboard_endpoints()
        
        # Finalizar resultados
        end_time = time.time()
        duration = end_time - start_time
        
        self.test_results["fim"] = datetime.now().isoformat()
        self.test_results["duracao_segundos"] = duration
        self.test_results["taxa_sucesso"] = (
            self.test_results["sucessos"] / 
            (self.test_results["sucessos"] + self.test_results["falhas"]) * 100
        ) if (self.test_results["sucessos"] + self.test_results["falhas"]) > 0 else 0
        
        # Salvar resultados
        with open("test_fluxo_zapi_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Exibir resumo
        logger.info("=" * 60)
        logger.info("📊 RESUMO DO TESTE")
        logger.info(f"✅ Sucessos: {self.test_results['sucessos']}")
        logger.info(f"❌ Falhas: {self.test_results['falhas']}")
        logger.info(f"📈 Taxa de Sucesso: {self.test_results['taxa_sucesso']:.1f}%")
        logger.info(f"⏱️  Duração: {duration:.2f} segundos")
        logger.info(f"📄 Resultados salvos em: test_fluxo_zapi_results.json")
        
        if self.test_results["erros"]:
            logger.info("\n🔍 ERROS DETECTADOS:")
            for erro in self.test_results["erros"]:
                logger.error(f"  - {erro['nome']}: {erro['detalhes']}")
        
        return self.test_results

async def main():
    """Função principal"""
    tester = TesteFluxoZAPI()
    results = await tester.run_complete_test()
    
    # Retornar código de saída baseado no sucesso
    if results["falhas"] == 0:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        logger.warning("⚠️  ALGUNS TESTES FALHARAM!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 