#!/usr/bin/env python3
"""
Teste Z-API - Endpoints Funcionais
==================================

Teste que usa apenas os endpoints que estão funcionando na API Z-API.
Baseado no diagnóstico que mostrou que /connection e /webhook funcionam.

Uso: python test_zapi_endpoints_funcionais.py
"""

import asyncio
import sys
import os
import json
import httpx
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

class ZAPITestFuncional:
    """Classe para testar endpoints funcionais da API Z-API"""
    
    def __init__(self):
        self.base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        self.headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        self.timeout = 30
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: dict = None):
        """Registra resultado de um teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if details:
            print(f"   📝 {details}")
        if data:
            print(f"   📊 Dados: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
    
    async def test_connection_endpoint(self):
        """Testa endpoint /connection que funciona"""
        print("🔌 TESTANDO ENDPOINT /connection")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/connection", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Endpoint /connection", True, "Endpoint funcionando", data)
                    return True
                else:
                    self.log_test("Endpoint /connection", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Endpoint /connection", False, f"Erro: {str(e)}")
            return False
    
    async def test_webhook_endpoint(self):
        """Testa endpoint /webhook que funciona"""
        print("🔗 TESTANDO ENDPOINT /webhook")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/webhook", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Endpoint /webhook", True, "Endpoint funcionando", data)
                    return True
                else:
                    self.log_test("Endpoint /webhook", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Endpoint /webhook", False, f"Erro: {str(e)}")
            return False
    
    async def test_send_message_direct(self):
        """Testa envio de mensagem diretamente via API"""
        print("💬 TESTANDO ENVIO DE MENSAGEM DIRETO")
        print("=" * 50)
        
        try:
            test_phone = "553198600366"
            test_message = f"🧪 Teste direto - {datetime.now().strftime('%H:%M:%S')}"
            
            payload = {
                "phone": test_phone,
                "message": test_message,
                "delayMessage": 2
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send-text",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Envio Direto", True, "Mensagem enviada com sucesso", data)
                    return True
                elif response.status_code == 403:
                    self.log_test("Envio Direto", False, "Erro 403 - Sem permissão para enviar mensagens")
                    return False
                else:
                    self.log_test("Envio Direto", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Envio Direto", False, f"Erro: {str(e)}")
            return False
    
    async def test_configure_webhook(self):
        """Testa configuração de webhook"""
        print("⚙️ TESTANDO CONFIGURAÇÃO DE WEBHOOK")
        print("=" * 50)
        
        try:
            webhook_url = "https://chatbot-clincia.vercel.app/webhook"
            
            payload = {
                "url": webhook_url,
                "enabled": True
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/webhook",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Configurar Webhook", True, "Webhook configurado com sucesso", data)
                    return True
                elif response.status_code == 403:
                    self.log_test("Configurar Webhook", False, "Erro 403 - Sem permissão para configurar webhook")
                    return False
                else:
                    self.log_test("Configurar Webhook", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Configurar Webhook", False, f"Erro: {str(e)}")
            return False
    
    async def test_get_messages(self):
        """Testa obtenção de mensagens"""
        print("📨 TESTANDO OBTENÇÃO DE MENSAGENS")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/messages", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Obter Mensagens", True, "Mensagens obtidas com sucesso", data)
                    return True
                elif response.status_code == 405:
                    self.log_test("Obter Mensagens", False, "Método não permitido - endpoint pode não existir")
                    return False
                else:
                    self.log_test("Obter Mensagens", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Obter Mensagens", False, f"Erro: {str(e)}")
            return False
    
    async def test_alternative_status(self):
        """Testa endpoint alternativo de status"""
        print("📊 TESTANDO STATUS ALTERNATIVO")
        print("=" * 50)
        
        try:
            # Tentar diferentes variações do endpoint de status
            status_endpoints = [
                "/status",
                "/instance/status",
                "/connection/status",
                "/health"
            ]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for endpoint in status_endpoints:
                    try:
                        response = await client.get(f"{self.base_url}{endpoint}", headers=self.headers)
                        print(f"   {endpoint}: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_test(f"Status {endpoint}", True, "Status obtido com sucesso", data)
                            return True
                            
                    except Exception as e:
                        print(f"   {endpoint}: Erro - {str(e)}")
                
                self.log_test("Status Alternativo", False, "Nenhum endpoint de status funcionou")
                return False
                
        except Exception as e:
            self.log_test("Status Alternativo", False, f"Erro: {str(e)}")
            return False
    
    def generate_summary(self, results):
        """Gera resumo dos testes"""
        print("\n" + "=" * 60)
        print("📋 RESUMO DOS TESTES")
        print("=" * 60)
        
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        
        print(f"Total de testes: {total}")
        print(f"✅ Passaram: {passed}")
        print(f"❌ Falharam: {failed}")
        print(f"📊 Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ TESTES QUE PASSARAM:")
        for result in results:
            if result['success']:
                print(f"  - {result['test']}")
        
        # Análise dos resultados
        print("\n🔍 ANÁLISE:")
        if passed >= 2:
            print("✅ API Z-API está parcialmente funcional")
            print("   - Alguns endpoints estão funcionando")
            print("   - Pode ser usado com limitações")
        elif passed == 1:
            print("⚠️ API Z-API tem funcionalidade limitada")
            print("   - Apenas alguns endpoints funcionam")
            print("   - Verificar configurações de permissão")
        else:
            print("❌ API Z-API não está funcionando")
            print("   - Verificar credenciais e configurações")
            print("   - Contatar suporte do Z-API")
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 TESTE Z-API - ENDPOINTS FUNCIONAIS")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        results = []
        
        # Lista de testes
        tests = [
            ("Connection Endpoint", self.test_connection_endpoint),
            ("Webhook Endpoint", self.test_webhook_endpoint),
            ("Envio Direto", self.test_send_message_direct),
            ("Configurar Webhook", self.test_configure_webhook),
            ("Obter Mensagens", self.test_get_messages),
            ("Status Alternativo", self.test_alternative_status)
        ]
        
        # Executar testes
        for test_name, test_func in tests:
            try:
                success = await test_func()
                results.append({
                    "test": test_name,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(1)  # Pausa entre testes
            except Exception as e:
                results.append({
                    "test": test_name,
                    "success": False,
                    "details": f"Erro inesperado: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Gerar resumo
        self.generate_summary(results)
        
        # Salvar resultados
        report_file = f"test_zapi_funcional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        
        return results

async def main():
    """Função principal"""
    try:
        tester = ZAPITestFuncional()
        results = await tester.run_all_tests()
        
        passed = sum(1 for r in results if r['success'])
        total = len(results)
        
        if passed >= total * 0.5:  # Pelo menos 50% dos testes passaram
            print("\n✅ API Z-API FUNCIONAL!")
            sys.exit(0)
        else:
            print("\n❌ API Z-API COM PROBLEMAS!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 