#!/usr/bin/env python3
"""
TESTE FLUXO COMPLETO DE AGENDAMENTO - GESTÃODS
Testa todo o processo de agendamento: CPF → Datas → Horários → Confirmação
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime, timedelta
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TesteFluxoAgendamentoGestaoDS:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.base_url}/webhook"
        self.dashboard_url = f"{self.base_url}/dashboard"
        
        # Dados de teste
        self.test_phone = "5531999999999"
        self.test_cpf = "12345678901"
        self.test_name = "João Silva"
        
        # Resultados
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
        self.respostas = []
    
    def log_resultado(self, nome: str, sucesso: bool, detalhes: str = "", dados: dict = None):
        """Registra resultado de um teste"""
        resultado = {
            "nome": nome,
            "sucesso": sucesso,
            "detalhes": detalhes,
            "dados": dados or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.respostas.append(resultado)
        
        if sucesso:
            self.sucessos += 1
            logger.info(f"SUCESSO - {nome}: {detalhes}")
        else:
            self.falhas += 1
            self.erros.append(f"{nome}: {detalhes}")
            logger.error(f"FALHA - {nome}: {detalhes}")
    
    async def enviar_mensagem(self, client, message: str, step: int):
        """Envia mensagem e captura resposta"""
        message_data = {
            "event": "message",
            "data": {
                "id": f"test_agendamento_{step:03d}",
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
                return {
                    "sucesso": True,
                    "status": response_data.get('status', 'N/A'),
                    "message": response_data.get('message', ''),
                    "data": response_data
                }
            else:
                return {
                    "sucesso": False,
                    "status": response.status_code,
                    "message": response.text,
                    "data": {}
                }
        except Exception as e:
            return {
                "sucesso": False,
                "status": "ERROR",
                "message": str(e),
                "data": {}
            }
    
    async def test_fluxo_agendamento_completo(self):
        """Testa fluxo completo de agendamento"""
        logger.info("INICIANDO TESTE DO FLUXO COMPLETO DE AGENDAMENTO")
        logger.info("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            step = 1
            
            # 1. Saudação inicial
            logger.info(f"STEP {step}: Saudação inicial")
            result = await self.enviar_mensagem(client, "oi", step)
            self.log_resultado(
                f"Step {step} - Saudação", 
                result["sucesso"], 
                f"Mensagem: 'oi' - Status: {result['status']}",
                result
            )
            step += 1
            await asyncio.sleep(1)
            
            # 2. Escolher agendamento (opção 1)
            logger.info(f"STEP {step}: Escolher agendamento")
            result = await self.enviar_mensagem(client, "1", step)
            self.log_resultado(
                f"Step {step} - Escolher Agendamento", 
                result["sucesso"], 
                f"Mensagem: '1' - Status: {result['status']}",
                result
            )
            step += 1
            await asyncio.sleep(1)
            
            # 3. Informar CPF
            logger.info(f"STEP {step}: Informar CPF")
            result = await self.enviar_mensagem(client, self.test_cpf, step)
            self.log_resultado(
                f"Step {step} - CPF", 
                result["sucesso"], 
                f"Mensagem: '{self.test_cpf}' - Status: {result['status']}",
                result
            )
            step += 1
            await asyncio.sleep(1)
            
            # 4. Informar nome
            logger.info(f"STEP {step}: Informar nome")
            result = await self.enviar_mensagem(client, self.test_name, step)
            self.log_resultado(
                f"Step {step} - Nome", 
                result["sucesso"], 
                f"Mensagem: '{self.test_name}' - Status: {result['status']}",
                result
            )
            step += 1
            await asyncio.sleep(1)
            
            # 5. Verificar se mostra datas disponíveis
            logger.info(f"STEP {step}: Verificar datas disponíveis")
            result = await self.enviar_mensagem(client, "sim", step)
            self.log_resultado(
                f"Step {step} - Datas Disponíveis", 
                result["sucesso"], 
                f"Mensagem: 'sim' - Status: {result['status']}",
                result
            )
            step += 1
            await asyncio.sleep(1)
    
    async def test_gestaods_api_diretamente(self):
        """Testa API do GestãoDS diretamente"""
        logger.info("TESTANDO API DO GESTÃODS DIRETAMENTE")
        logger.info("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # 1. Testar busca de paciente por CPF
            logger.info("1. Testando busca de paciente por CPF...")
            try:
                response = await client.get(
                    f"{self.dashboard_url}/gestaods/patient/{self.test_cpf}"
                )
                if response.status_code == 200:
                    patient_data = response.json()
                    self.log_resultado(
                        "GestãoDS - Busca Paciente", 
                        True, 
                        f"Paciente encontrado: {patient_data.get('name', 'N/A')}",
                        patient_data
                    )
                else:
                    self.log_resultado(
                        "GestãoDS - Busca Paciente", 
                        False, 
                        f"Status: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                self.log_resultado(
                    "GestãoDS - Busca Paciente", 
                    False, 
                    f"Erro: {str(e)}"
                )
            
            # 2. Testar busca de datas disponíveis
            logger.info("2. Testando busca de datas disponíveis...")
            try:
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                response = await client.get(
                    f"{self.dashboard_url}/gestaods/slots/{tomorrow}"
                )
                if response.status_code == 200:
                    slots_data = response.json()
                    slots = slots_data.get('slots', [])
                    self.log_resultado(
                        "GestãoDS - Datas Disponíveis", 
                        True, 
                        f"Datas encontradas: {len(slots)} para {tomorrow}",
                        slots_data
                    )
                else:
                    self.log_resultado(
                        "GestãoDS - Datas Disponíveis", 
                        False, 
                        f"Status: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                self.log_resultado(
                    "GestãoDS - Datas Disponíveis", 
                    False, 
                    f"Erro: {str(e)}"
                )
            
            # 3. Testar busca de horários para uma data específica
            logger.info("3. Testando busca de horários...")
            try:
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                response = await client.get(
                    f"{self.dashboard_url}/gestaods/times/{tomorrow}"
                )
                if response.status_code == 200:
                    times_data = response.json()
                    times = times_data.get('times', [])
                    self.log_resultado(
                        "GestãoDS - Horários", 
                        True, 
                        f"Horários encontrados: {len(times)} para {tomorrow}",
                        times_data
                    )
                else:
                    self.log_resultado(
                        "GestãoDS - Horários", 
                        False, 
                        f"Status: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                self.log_resultado(
                    "GestãoDS - Horários", 
                    False, 
                    f"Erro: {str(e)}"
                )
    
    async def test_endpoints_gestaods(self):
        """Testa todos os endpoints do GestãoDS"""
        logger.info("TESTANDO TODOS OS ENDPOINTS DO GESTÃODS")
        logger.info("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # Lista de endpoints para testar
            endpoints = [
                ("/gestaods/health", "Health Check"),
                ("/gestaods/widget", "Widget Info"),
                ("/gestaods/config", "Configuração"),
                ("/gestaods/services", "Serviços"),
                ("/gestaods/doctors", "Médicos"),
            ]
            
            for endpoint, description in endpoints:
                try:
                    response = await client.get(f"{self.dashboard_url}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        self.log_resultado(
                            f"GestãoDS - {description}", 
                            True, 
                            f"Endpoint: {endpoint} - Status: {response.status_code}",
                            data
                        )
                    else:
                        self.log_resultado(
                            f"GestãoDS - {description}", 
                            False, 
                            f"Endpoint: {endpoint} - Status: {response.status_code}"
                        )
                except Exception as e:
                    self.log_resultado(
                        f"GestãoDS - {description}", 
                        False, 
                        f"Endpoint: {endpoint} - Erro: {str(e)}"
                    )
                
                await asyncio.sleep(0.5)
    
    async def run_test_completo(self):
        """Executa todos os testes"""
        logger.info("INICIANDO TESTE COMPLETO DO FLUXO DE AGENDAMENTO")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Executar testes
        await self.test_fluxo_agendamento_completo()
        await self.test_gestaods_api_diretamente()
        await self.test_endpoints_gestaods()
        
        # Calcular resultados
        end_time = time.time()
        duration = end_time - start_time
        total_tests = self.sucessos + self.falhas
        taxa_sucesso = (self.sucessos / total_tests * 100) if total_tests > 0 else 0
        
        # Exibir resumo
        logger.info("=" * 60)
        logger.info("RESUMO DO TESTE DE AGENDAMENTO")
        logger.info(f"Sucessos: {self.sucessos}")
        logger.info(f"Falhas: {self.falhas}")
        logger.info(f"Taxa de Sucesso: {taxa_sucesso:.1f}%")
        logger.info(f"Duração: {duration:.2f} segundos")
        
        if self.erros:
            logger.info("ERROS DETECTADOS:")
            for erro in self.erros:
                logger.error(f"  - {erro}")
        
        # Salvar resultados detalhados
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "sucessos": self.sucessos,
            "falhas": self.falhas,
            "taxa_sucesso": taxa_sucesso,
            "duracao": duration,
            "erros": self.erros,
            "respostas_detalhadas": self.respostas
        }
        
        with open("test_agendamento_gestaods_results.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        logger.info("Resultados salvos em: test_agendamento_gestaods_results.json")
        
        return resultados

async def main():
    """Função principal"""
    tester = TesteFluxoAgendamentoGestaoDS()
    results = await tester.run_test_completo()
    
    if results["falhas"] == 0:
        logger.info("TODOS OS TESTES DE AGENDAMENTO PASSARAM!")
        return 0
    else:
        logger.warning("ALGUNS TESTES DE AGENDAMENTO FALHARAM!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 