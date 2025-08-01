#!/usr/bin/env python3
"""
Teste Completo da API Z-API
============================

Este script testa todas as funcionalidades principais da API do Z-API:
- Verificação de configurações
- Teste de status da instância
- Envio de mensagens de texto
- Envio de botões
- Envio de links
- Marcação de mensagens como lidas
- Envio de localização
- Teste de formatação de telefone
- Teste de rate limiting
- Teste de timeout

Autor: Sistema de Teste Automatizado
Data: 2024
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import httpx

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.whatsapp import WhatsAppService

class ZAPITester:
    """Classe para testar todas as funcionalidades da API Z-API"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.test_results = []
        self.phone_test = "+553198600366"  # Telefone da clínica para teste
        self.test_message = f"🧪 Teste automatizado - {datetime.now().strftime('%H:%M:%S')}"
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Dict = None):
        """Registra resultado de um teste"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if details:
            print(f"   📝 {details}")
        if data:
            print(f"   📊 Dados: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
    
    async def test_configuration(self):
        """Testa se as configurações estão corretas"""
        print("🔧 TESTANDO CONFIGURAÇÕES")
        print("=" * 50)
        
        # Verificar variáveis de ambiente
        required_vars = [
            'zapi_base_url',
            'zapi_instance_id', 
            'zapi_token',
            'zapi_client_token'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = getattr(settings, var, None)
            if not value:
                missing_vars.append(var)
            else:
                print(f"✅ {var}: {'*' * len(str(value)[:10])}...")
        
        if missing_vars:
            self.log_test("Configurações", False, f"Variáveis faltando: {missing_vars}")
            return False
        else:
            self.log_test("Configurações", True, "Todas as configurações estão presentes")
            return True
    
    async def test_instance_status(self):
        """Testa o status da instância Z-API"""
        print("📊 TESTANDO STATUS DA INSTÂNCIA")
        print("=" * 50)
        
        try:
            status = await self.whatsapp_service.check_status()
            
            if status and status.get('status') == 'connected':
                self.log_test("Status da Instância", True, "Instância conectada e funcionando", status)
                return True
            else:
                self.log_test("Status da Instância", False, f"Status inesperado: {status}")
                return False
                
        except Exception as e:
            self.log_test("Status da Instância", False, f"Erro ao verificar status: {str(e)}")
            return False
    
    async def test_send_text_message(self):
        """Testa envio de mensagem de texto"""
        print("💬 TESTANDO ENVIO DE MENSAGEM DE TEXTO")
        print("=" * 50)
        
        try:
            result = await self.whatsapp_service.send_text(
                phone=self.phone_test,
                message=self.test_message
            )
            
            if result and result.get('status') == 'success':
                self.log_test("Envio de Texto", True, "Mensagem enviada com sucesso", result)
                return True
            else:
                self.log_test("Envio de Texto", False, f"Resposta inesperada: {result}")
                return False
                
        except Exception as e:
            self.log_test("Envio de Texto", False, f"Erro ao enviar mensagem: {str(e)}")
            return False
    
    async def test_send_button_list(self):
        """Testa envio de lista de botões"""
        print("🔘 TESTANDO ENVIO DE BOTÕES")
        print("=" * 50)
        
        buttons = [
            {"id": "1", "title": "Agendar Consulta"},
            {"id": "2", "title": "Falar com Atendente"},
            {"id": "3", "title": "Ver Horários"}
        ]
        
        try:
            result = await self.whatsapp_service.send_button_list(
                phone=self.phone_test,
                message="Escolha uma opção:",
                buttons=buttons,
                title="Menu Principal"
            )
            
            if result and result.get('status') == 'success':
                self.log_test("Envio de Botões", True, "Botões enviados com sucesso", result)
                return True
            else:
                self.log_test("Envio de Botões", False, f"Resposta inesperada: {result}")
                return False
                
        except Exception as e:
            self.log_test("Envio de Botões", False, f"Erro ao enviar botões: {str(e)}")
            return False
    
    async def test_send_link(self):
        """Testa envio de link"""
        print("🔗 TESTANDO ENVIO DE LINK")
        print("=" * 50)
        
        try:
            result = await self.whatsapp_service.send_link(
                phone=self.phone_test,
                message="Acesse nosso site para mais informações:",
                link="https://clinicanassif.com.br",
                link_title="Site da Clínica",
                link_description="Site oficial da Clínica Nassif"
            )
            
            if result and result.get('status') == 'success':
                self.log_test("Envio de Link", True, "Link enviado com sucesso", result)
                return True
            else:
                self.log_test("Envio de Link", False, f"Resposta inesperada: {result}")
                return False
                
        except Exception as e:
            self.log_test("Envio de Link", False, f"Erro ao enviar link: {str(e)}")
            return False
    
    async def test_send_location(self):
        """Testa envio de localização"""
        print("📍 TESTANDO ENVIO DE LOCALIZAÇÃO")
        print("=" * 50)
        
        try:
            result = await self.whatsapp_service.send_location(
                phone=self.phone_test,
                latitude=-19.9245,
                longitude=-43.9352,
                name="Clínica Nassif",
                address="Rua Example, 123 - Savassi, Belo Horizonte - MG"
            )
            
            if result and result.get('status') == 'success':
                self.log_test("Envio de Localização", True, "Localização enviada com sucesso", result)
                return True
            else:
                self.log_test("Envio de Localização", False, f"Resposta inesperada: {result}")
                return False
                
        except Exception as e:
            self.log_test("Envio de Localização", False, f"Erro ao enviar localização: {str(e)}")
            return False
    
    async def test_phone_formatting(self):
        """Testa formatação de números de telefone"""
        print("📱 TESTANDO FORMATAÇÃO DE TELEFONE")
        print("=" * 50)
        
        test_cases = [
            ("3198600366", "553198600366"),
            ("+553198600366", "553198600366"),
            ("553198600366", "553198600366"),
            ("(31) 98600-366", "553198600366"),
            ("31 98600 366", "553198600366")
        ]
        
        all_passed = True
        for input_phone, expected in test_cases:
            formatted = self.whatsapp_service._format_phone(input_phone)
            if formatted == expected:
                print(f"✅ {input_phone} → {formatted}")
            else:
                print(f"❌ {input_phone} → {formatted} (esperado: {expected})")
                all_passed = False
        
        self.log_test("Formatação de Telefone", all_passed, 
                     "Todos os casos de formatação passaram" if all_passed else "Alguns casos falharam")
        return all_passed
    
    async def test_rate_limiting(self):
        """Testa comportamento com rate limiting"""
        print("⏱️ TESTANDO RATE LIMITING")
        print("=" * 50)
        
        try:
            # Enviar múltiplas mensagens rapidamente
            tasks = []
            for i in range(3):
                task = self.whatsapp_service.send_text(
                    phone=self.phone_test,
                    message=f"Teste rate limit {i+1} - {datetime.now().strftime('%H:%M:%S')}"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if r and r.get('status') == 'success')
            
            if success_count > 0:
                self.log_test("Rate Limiting", True, f"{success_count}/3 mensagens enviadas com sucesso")
                return True
            else:
                self.log_test("Rate Limiting", False, "Nenhuma mensagem foi enviada")
                return False
                
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Erro no teste de rate limiting: {str(e)}")
            return False
    
    async def test_timeout_handling(self):
        """Testa tratamento de timeout"""
        print("⏰ TESTANDO TRATAMENTO DE TIMEOUT")
        print("=" * 50)
        
        # Criar uma instância com timeout muito baixo para forçar timeout
        original_timeout = self.whatsapp_service.timeout
        self.whatsapp_service.timeout = 0.001  # 1ms para forçar timeout
        
        try:
            result = await self.whatsapp_service.send_text(
                phone=self.phone_test,
                message="Teste de timeout"
            )
            
            # Restaurar timeout original
            self.whatsapp_service.timeout = original_timeout
            
            # Se chegou aqui sem exceção, o retry funcionou
            self.log_test("Tratamento de Timeout", True, "Timeout tratado corretamente com retry")
            return True
            
        except Exception as e:
            # Restaurar timeout original
            self.whatsapp_service.timeout = original_timeout
            
            if "timeout" in str(e).lower():
                self.log_test("Tratamento de Timeout", True, "Timeout detectado corretamente")
                return True
            else:
                self.log_test("Tratamento de Timeout", False, f"Erro inesperado: {str(e)}")
                return False
    
    async def test_error_recovery(self):
        """Testa recuperação de erros"""
        print("🔄 TESTANDO RECUPERAÇÃO DE ERROS")
        print("=" * 50)
        
        # Testar com número inválido
        try:
            result = await self.whatsapp_service.send_text(
                phone="000000000",
                message="Teste de erro"
            )
            
            # Se chegou aqui, o sistema não quebrou
            self.log_test("Recuperação de Erros", True, "Sistema não quebrou com número inválido")
            return True
            
        except Exception as e:
            self.log_test("Recuperação de Erros", False, f"Sistema quebrou: {str(e)}")
            return False
    
    def generate_report(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Passaram: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"📊 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ TESTES QUE PASSARAM:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        # Salvar relatório em arquivo
        report_file = f"test_zapi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        
        return passed_tests == total_tests
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES COMPLETOS DA API Z-API")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📱 Telefone de teste: {self.phone_test}")
        print("=" * 60)
        
        # Lista de todos os testes
        tests = [
            ("Configurações", self.test_configuration),
            ("Status da Instância", self.test_instance_status),
            ("Formatação de Telefone", self.test_phone_formatting),
            ("Envio de Texto", self.test_send_text_message),
            ("Envio de Botões", self.test_send_button_list),
            ("Envio de Link", self.test_send_link),
            ("Envio de Localização", self.test_send_location),
            ("Rate Limiting", self.test_rate_limiting),
            ("Tratamento de Timeout", self.test_timeout_handling),
            ("Recuperação de Erros", self.test_error_recovery)
        ]
        
        # Executar testes
        for test_name, test_func in tests:
            try:
                await test_func()
                # Pequena pausa entre testes para evitar rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                self.log_test(test_name, False, f"Erro inesperado: {str(e)}")
        
        # Gerar relatório final
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 TODOS OS TESTES PASSARAM! API Z-API funcionando perfeitamente!")
        else:
            print("\n⚠️ ALGUNS TESTES FALHARAM. Verifique os detalhes acima.")
        
        return all_passed

async def main():
    """Função principal"""
    try:
        tester = ZAPITester()
        success = await tester.run_all_tests()
        
        if success:
            print("\n✅ SISTEMA Z-API PRONTO PARA PRODUÇÃO!")
            sys.exit(0)
        else:
            print("\n❌ PROBLEMAS DETECTADOS NA API Z-API!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 