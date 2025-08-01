#!/usr/bin/env python3
"""
Teste Final Z-API
=================

Teste final da API Z-API usando apenas os endpoints que funcionam.
Tenta diferentes abordagens para envio de mensagens e configuração.

Uso: python test_zapi_final.py
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

class ZAPITestFinal:
    """Classe para teste final da API Z-API"""
    
    def __init__(self):
        self.base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        self.headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        self.timeout = 30
        
    def log_result(self, test_name: str, success: bool, details: str = "", data: dict = None):
        """Registra resultado de um teste"""
        status = "✅ SUCESSO" if success else "❌ FALHA"
        print(f"{status} - {test_name}")
        if details:
            print(f"   📝 {details}")
        if data:
            print(f"   📊 Dados: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
    
    async def test_instance_status(self):
        """Testa status da instância usando endpoint que funciona"""
        print("📊 TESTANDO STATUS DA INSTÂNCIA")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/instance/status", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Status da Instância", True, "Status obtido com sucesso", data)
                    return True
                else:
                    self.log_result("Status da Instância", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_result("Status da Instância", False, f"Erro: {str(e)}")
            return False
    
    async def test_webhook_configuration(self):
        """Testa configuração de webhook"""
        print("🔗 TESTANDO CONFIGURAÇÃO DE WEBHOOK")
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
                    self.log_result("Configurar Webhook", True, "Webhook configurado", data)
                    return True
                else:
                    self.log_result("Configurar Webhook", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_result("Configurar Webhook", False, f"Erro: {str(e)}")
            return False
    
    async def test_send_message_variations(self):
        """Testa diferentes variações de envio de mensagem"""
        print("💬 TESTANDO DIFERENTES MÉTODOS DE ENVIO")
        print("=" * 50)
        
        test_phone = "553198600366"
        test_message = f"🧪 Teste final - {datetime.now().strftime('%H:%M:%S')}"
        
        # Diferentes endpoints para envio
        send_endpoints = [
            "/send-text",
            "/send-message",
            "/message/send",
            "/chat/send"
        ]
        
        # Diferentes formatos de payload
        payload_variations = [
            {"phone": test_phone, "message": test_message},
            {"phone": test_phone, "message": test_message, "delayMessage": 2},
            {"to": test_phone, "text": test_message},
            {"number": test_phone, "content": test_message}
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for i, endpoint in enumerate(send_endpoints):
                for j, payload in enumerate(payload_variations):
                    try:
                        print(f"   Testando {endpoint} com payload {j+1}...")
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=self.headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_result(f"Envio {endpoint}", True, f"Sucesso com payload {j+1}", data)
                            return True
                        elif response.status_code == 403:
                            print(f"   ❌ 403 - Sem permissão")
                        else:
                            print(f"   ❌ {response.status_code}")
                            
                    except Exception as e:
                        print(f"   ❌ Erro: {str(e)}")
                    
                    await asyncio.sleep(0.5)  # Pausa entre tentativas
        
        self.log_result("Envio de Mensagens", False, "Nenhum método de envio funcionou")
        return False
    
    async def test_connection_info(self):
        """Testa informações de conexão"""
        print("🔌 TESTANDO INFORMAÇÕES DE CONEXÃO")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/connection", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Informações de Conexão", True, "Dados obtidos", data)
                    return True
                else:
                    self.log_result("Informações de Conexão", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_result("Informações de Conexão", False, f"Erro: {str(e)}")
            return False
    
    async def test_qr_code_generation(self):
        """Testa geração de QR Code"""
        print("📱 TESTANDO GERAÇÃO DE QR CODE")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/qr-code", headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("QR Code", True, "QR Code gerado", data)
                    return True
                elif response.status_code == 403:
                    self.log_result("QR Code", False, "Sem permissão para gerar QR Code")
                    return False
                else:
                    self.log_result("QR Code", False, f"Status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_result("QR Code", False, f"Erro: {str(e)}")
            return False
    
    def generate_final_report(self, results):
        """Gera relatório final"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL Z-API")
        print("=" * 60)
        
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        
        print(f"Total de testes: {total}")
        print(f"✅ Sucessos: {passed}")
        print(f"❌ Falhas: {failed}")
        print(f"📊 Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        print("\n✅ FUNCIONALIDADES QUE FUNCIONAM:")
        for result in results:
            if result['success']:
                print(f"  - {result['test']}")
        
        print("\n❌ FUNCIONALIDADES COM PROBLEMAS:")
        for result in results:
            if not result['success']:
                print(f"  - {result['test']}")
        
        print("\n🔍 ANÁLISE FINAL:")
        if passed >= 3:
            print("✅ API Z-API FUNCIONAL!")
            print("   - A maioria dos endpoints está funcionando")
            print("   - Sistema pode ser usado com algumas limitações")
            print("   - Recomenda-se verificar permissões para envio de mensagens")
        elif passed >= 2:
            print("⚠️ API Z-API PARCIALMENTE FUNCIONAL")
            print("   - Alguns endpoints funcionam")
            print("   - Funcionalidade limitada")
            print("   - Verificar configurações de permissão")
        else:
            print("❌ API Z-API COM PROBLEMAS CRÍTICOS")
            print("   - Poucos endpoints funcionam")
            print("   - Verificar credenciais e configurações")
            print("   - Contatar suporte do Z-API")
        
        print("\n💡 RECOMENDAÇÕES:")
        print("1. Verificar permissões no painel do Z-API")
        print("2. Confirmar se a instância está ativa")
        print("3. Verificar se o WhatsApp está conectado")
        print("4. Testar manualmente no painel do Z-API")
        print("5. Contatar suporte se necessário")
    
    async def run_final_test(self):
        """Executa teste final completo"""
        print("🚀 TESTE FINAL Z-API")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        results = []
        
        # Lista de testes
        tests = [
            ("Status da Instância", self.test_instance_status),
            ("Informações de Conexão", self.test_connection_info),
            ("Configuração de Webhook", self.test_webhook_configuration),
            ("Envio de Mensagens", self.test_send_message_variations),
            ("QR Code", self.test_qr_code_generation)
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
        
        # Gerar relatório final
        self.generate_final_report(results)
        
        # Salvar resultados
        report_file = f"test_zapi_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": len(results),
                    "passed": sum(1 for r in results if r['success']),
                    "failed": sum(1 for r in results if not r['success'])
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        
        return results

async def main():
    """Função principal"""
    try:
        tester = ZAPITestFinal()
        results = await tester.run_final_test()
        
        passed = sum(1 for r in results if r['success'])
        total = len(results)
        
        if passed >= total * 0.6:  # Pelo menos 60% dos testes passaram
            print("\n🎉 API Z-API PRONTA PARA USO!")
            sys.exit(0)
        elif passed >= total * 0.4:  # Pelo menos 40% dos testes passaram
            print("\n⚠️ API Z-API COM LIMITAÇÕES!")
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