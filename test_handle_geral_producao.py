#!/usr/bin/env python3
"""
TESTE HANDLE GERAL PRODUÇÃO
Testa o handle geral em produção: menu e todos os fluxos
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

class TesteHandleGeralProducao:
    def __init__(self):
        self.base_url = "https://chatbot-clincia.vercel.app"
        self.webhook_url = f"{self.base_url}/webhook"
        
        # Dados de teste
        self.test_phone = "5531999999999"
        self.test_message_id = "test_handle_"
        
        # Resultados
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
        self.respostas = []
    
    def log_resultado(self, teste: str, sucesso: bool, detalhes: str = "", resposta: dict = None):
        """Registra resultado do teste"""
        if sucesso:
            self.sucessos += 1
            logger.info(f"✅ {teste}: {detalhes}")
        else:
            self.falhas += 1
            logger.error(f"❌ {teste}: {detalhes}")
            self.erros.append(f"{teste}: {detalhes}")
        
        if resposta:
            self.respostas.append({
                "teste": teste,
                "sucesso": sucesso,
                "resposta": resposta,
                "timestamp": datetime.now().isoformat()
            })
    
    async def test_webhook_health(self):
        """Testa saúde do webhook"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.webhook_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_resultado("Webhook Health", True, f"Status: {data.get('status')}", data)
                    return True
                else:
                    self.log_resultado("Webhook Health", False, f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.log_resultado("Webhook Health", False, str(e))
            return False
    
    async def enviar_mensagem_webhook(self, mensagem: str, descricao: str = ""):
        """Envia mensagem via webhook e retorna resposta"""
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
                    self.log_resultado(f"Mensagem '{mensagem}'", True, f"Status: {data.get('status')} - {descricao}", data)
                    return True, data
                else:
                    self.log_resultado(f"Mensagem '{mensagem}'", False, f"Status: {response.status_code} - {response.text} - {descricao}")
                    return False, None
        except Exception as e:
            self.log_resultado(f"Mensagem '{mensagem}'", False, str(e) + f" - {descricao}")
            return False, None
    
    async def test_fluxo_menu_principal(self):
        """Testa fluxo do menu principal"""
        logger.info("🎯 TESTANDO FLUXO DO MENU PRINCIPAL")
        
        # Teste 1: Primeira mensagem (deve mostrar menu)
        sucesso, resposta = await self.enviar_mensagem_webhook("oi", "Primeira mensagem - deve mostrar menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Teste 2: Opção inválida
        sucesso, resposta = await self.enviar_mensagem_webhook("9", "Opção inválida - deve mostrar erro")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Teste 3: Comando global (menu)
        sucesso, resposta = await self.enviar_mensagem_webhook("menu", "Comando global menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_fluxo_agendamento(self):
        """Testa fluxo completo de agendamento"""
        logger.info("📅 TESTANDO FLUXO DE AGENDAMENTO")
        
        # Step 1: Escolher agendamento
        sucesso, resposta = await self.enviar_mensagem_webhook("1", "Escolher agendamento")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Step 2: Informar CPF
        sucesso, resposta = await self.enviar_mensagem_webhook("12345678901", "Informar CPF")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Step 3: Informar nome
        sucesso, resposta = await self.enviar_mensagem_webhook("João Silva", "Informar nome")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Step 4: Confirmar paciente
        sucesso, resposta = await self.enviar_mensagem_webhook("sim", "Confirmar paciente")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_fluxo_visualizar_agendamentos(self):
        """Testa fluxo de visualizar agendamentos"""
        logger.info("👁️ TESTANDO FLUXO DE VISUALIZAR AGENDAMENTOS")
        
        # Voltar ao menu
        sucesso, resposta = await self.enviar_mensagem_webhook("menu", "Voltar ao menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Escolher visualizar agendamentos
        sucesso, resposta = await self.enviar_mensagem_webhook("2", "Escolher visualizar agendamentos")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Informar CPF
        sucesso, resposta = await self.enviar_mensagem_webhook("12345678901", "Informar CPF para visualizar")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_fluxo_cancelamento(self):
        """Testa fluxo de cancelamento"""
        logger.info("❌ TESTANDO FLUXO DE CANCELAMENTO")
        
        # Voltar ao menu
        sucesso, resposta = await self.enviar_mensagem_webhook("menu", "Voltar ao menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Escolher cancelamento
        sucesso, resposta = await self.enviar_mensagem_webhook("3", "Escolher cancelamento")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Informar CPF
        sucesso, resposta = await self.enviar_mensagem_webhook("12345678901", "Informar CPF para cancelamento")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_fluxo_lista_espera(self):
        """Testa fluxo de lista de espera"""
        logger.info("📝 TESTANDO FLUXO DE LISTA DE ESPERA")
        
        # Voltar ao menu
        sucesso, resposta = await self.enviar_mensagem_webhook("menu", "Voltar ao menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Escolher lista de espera
        sucesso, resposta = await self.enviar_mensagem_webhook("4", "Escolher lista de espera")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Informar CPF
        sucesso, resposta = await self.enviar_mensagem_webhook("12345678901", "Informar CPF para lista de espera")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_fluxo_atendente(self):
        """Testa fluxo de falar com atendente"""
        logger.info("👨‍💼 TESTANDO FLUXO DE ATENDENTE")
        
        # Voltar ao menu
        sucesso, resposta = await self.enviar_mensagem_webhook("menu", "Voltar ao menu")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Escolher atendente
        sucesso, resposta = await self.enviar_mensagem_webhook("5", "Escolher falar com atendente")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def test_comandos_globais(self):
        """Testa comandos globais"""
        logger.info("🌐 TESTANDO COMANDOS GLOBAIS")
        
        # Teste comando sair
        sucesso, resposta = await self.enviar_mensagem_webhook("0", "Comando sair")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Teste comando ajuda
        sucesso, resposta = await self.enviar_mensagem_webhook("ajuda", "Comando ajuda")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        # Teste comando status
        sucesso, resposta = await self.enviar_mensagem_webhook("status", "Comando status")
        if not sucesso:
            return False
        
        await asyncio.sleep(2)
        
        return True
    
    async def executar_testes(self):
        """Executa todos os testes"""
        logger.info("🚀 INICIANDO TESTE COMPLETO DO HANDLE GERAL EM PRODUÇÃO")
        logger.info(f"📡 URL: {self.webhook_url}")
        logger.info("=" * 60)
        
        # Teste 1: Health check
        await self.test_webhook_health()
        await asyncio.sleep(1)
        
        # Teste 2: Fluxo do menu principal
        await self.test_fluxo_menu_principal()
        await asyncio.sleep(2)
        
        # Teste 3: Fluxo de agendamento
        await self.test_fluxo_agendamento()
        await asyncio.sleep(2)
        
        # Teste 4: Fluxo de visualizar agendamentos
        await self.test_fluxo_visualizar_agendamentos()
        await asyncio.sleep(2)
        
        # Teste 5: Fluxo de cancelamento
        await self.test_fluxo_cancelamento()
        await asyncio.sleep(2)
        
        # Teste 6: Fluxo de lista de espera
        await self.test_fluxo_lista_espera()
        await asyncio.sleep(2)
        
        # Teste 7: Fluxo de atendente
        await self.test_fluxo_atendente()
        await asyncio.sleep(2)
        
        # Teste 8: Comandos globais
        await self.test_comandos_globais()
        
        # Resultados
        total = self.sucessos + self.falhas
        taxa_sucesso = (self.sucessos / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 RESULTADOS FINAIS DOS TESTES")
        logger.info("=" * 60)
        logger.info(f"✅ Sucessos: {self.sucessos}")
        logger.info(f"❌ Falhas: {self.falhas}")
        logger.info(f"📈 Taxa de Sucesso: {taxa_sucesso:.1f}%")
        
        if self.erros:
            logger.info("🔍 Erros encontrados:")
            for erro in self.erros:
                logger.error(f"   - {erro}")
        
        # Salvar resultados detalhados
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "sucessos": self.sucessos,
            "falhas": self.falhas,
            "taxa_sucesso": taxa_sucesso,
            "erros": self.erros,
            "respostas_detalhadas": self.respostas
        }
        
        with open("test_handle_geral_producao_results.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Resultados salvos em: test_handle_geral_producao_results.json")
        
        return self.sucessos > 0

async def main():
    """Função principal"""
    tester = TesteHandleGeralProducao()
    sucesso = await tester.executar_testes()
    
    if sucesso:
        logger.info("🎉 Testes do handle geral concluídos com sucesso!")
    else:
        logger.error("💥 Testes do handle geral falharam!")

if __name__ == "__main__":
    asyncio.run(main()) 