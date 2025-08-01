#!/usr/bin/env python3
"""
TESTE SIMPLES DOS ENDPOINTS DO GESTÃODS
Verifica se os endpoints do GestãoDS estão funcionando no dashboard
"""

import asyncio
import httpx
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TesteGestaoDSEndpoints:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.dashboard_url = f"{self.base_url}/dashboard"
        
        # Dados de teste
        self.test_cpf = "12345678901"
        self.test_date = "2025-08-01"
    
    async def test_endpoint(self, endpoint: str, description: str):
        """Testa um endpoint específico"""
        url = f"{self.dashboard_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Testando: {description}")
                logger.info(f"URL: {url}")
                
                response = await client.get(url)
                
                logger.info(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ SUCESSO - {description}")
                    logger.info(f"Resposta: {data}")
                    return True
                else:
                    logger.error(f"❌ FALHA - {description}")
                    logger.error(f"Status: {response.status_code}")
                    logger.error(f"Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ ERRO - {description}")
            logger.error(f"Erro: {str(e)}")
            return False
    
    async def run_tests(self):
        """Executa todos os testes"""
        logger.info("INICIANDO TESTE DOS ENDPOINTS DO GESTÃODS")
        logger.info("=" * 60)
        
        # Lista de endpoints para testar
        endpoints = [
            ("/gestaods/health", "Health Check do GestãoDS"),
            ("/gestaods/widget", "Widget do GestãoDS"),
            ("/gestaods/config", "Configuração do GestãoDS"),
            ("/gestaods/services", "Serviços do GestãoDS"),
            ("/gestaods/doctors", "Médicos do GestãoDS"),
            (f"/gestaods/patient/{self.test_cpf}", f"Busca Paciente CPF {self.test_cpf}"),
            (f"/gestaods/slots/{self.test_date}", f"Slots para {self.test_date}"),
            (f"/gestaods/times/{self.test_date}", f"Horários para {self.test_date}"),
        ]
        
        sucessos = 0
        falhas = 0
        
        for endpoint, description in endpoints:
            resultado = await self.test_endpoint(endpoint, description)
            if resultado:
                sucessos += 1
            else:
                falhas += 1
            
            logger.info("-" * 40)
            await asyncio.sleep(1)  # Aguardar entre testes
        
        # Resumo
        total = sucessos + falhas
        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("RESUMO DOS TESTES")
        logger.info(f"Sucessos: {sucessos}")
        logger.info(f"Falhas: {falhas}")
        logger.info(f"Taxa de Sucesso: {taxa_sucesso:.1f}%")
        
        if falhas == 0:
            logger.info("🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
        else:
            logger.warning("⚠️ ALGUNS ENDPOINTS FALHARAM!")
        
        return sucessos, falhas

async def main():
    """Função principal"""
    tester = TesteGestaoDSEndpoints()
    sucessos, falhas = await tester.run_tests()
    
    if falhas == 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 