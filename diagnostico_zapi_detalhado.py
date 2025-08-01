#!/usr/bin/env python3
"""
Diagnóstico Detalhado Z-API
===========================

Script para diagnosticar problemas com a API Z-API de forma detalhada.
Testa diferentes endpoints e fornece informações úteis para debug.

Uso: python diagnostico_zapi_detalhado.py
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

class ZAPIDiagnostico:
    """Classe para diagnóstico detalhado da API Z-API"""
    
    def __init__(self):
        self.base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        self.headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        self.timeout = 30
        
    def log_info(self, title: str, data: dict = None):
        """Registra informação de diagnóstico"""
        print(f"\n🔍 {title}")
        print("-" * 50)
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
    
    async def test_connection_basic(self):
        """Testa conexão básica com a API"""
        print("🔌 TESTE DE CONEXÃO BÁSICA")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Teste 1: Verificar se a URL está acessível
                print("1️⃣ Testando acessibilidade da URL...")
                response = await client.get(settings.zapi_base_url)
                print(f"   Status: {response.status_code}")
                print(f"   URL: {settings.zapi_base_url}")
                
                if response.status_code == 200:
                    print("   ✅ URL acessível")
                else:
                    print(f"   ❌ URL não acessível: {response.status_code}")
                
                # Teste 2: Verificar endpoint de status
                print("\n2️⃣ Testando endpoint de status...")
                status_url = f"{self.base_url}/status"
                print(f"   URL: {status_url}")
                
                response = await client.get(status_url, headers=self.headers)
                print(f"   Status: {response.status_code}")
                print(f"   Headers enviados: {self.headers}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_info("Resposta de Status", data)
                    return True
                elif response.status_code == 403:
                    print("   ❌ Erro 403 - Forbidden")
                    print("   📝 Possíveis causas:")
                    print("      - Token inválido ou expirado")
                    print("      - Instance ID incorreto")
                    print("      - Client-Token incorreto")
                    print("      - Permissões insuficientes")
                    return False
                else:
                    print(f"   ❌ Erro {response.status_code}")
                    print(f"   📄 Resposta: {response.text}")
                    return False
                    
        except httpx.ConnectError as e:
            print(f"   ❌ Erro de conexão: {str(e)}")
            return False
        except httpx.TimeoutException as e:
            print(f"   ❌ Timeout: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)}")
            return False
    
    async def test_credentials_validation(self):
        """Testa validação das credenciais"""
        print("\n🔐 TESTE DE VALIDAÇÃO DE CREDENCIAIS")
        print("=" * 50)
        
        # Verificar formato das credenciais
        print("1️⃣ Verificando formato das credenciais...")
        
        instance_id = settings.zapi_instance_id
        token = settings.zapi_token
        client_token = settings.zapi_client_token
        
        print(f"   Instance ID: {instance_id[:10]}... (tamanho: {len(instance_id)})")
        print(f"   Token: {token[:10]}... (tamanho: {len(token)})")
        print(f"   Client Token: {client_token[:10]}... (tamanho: {len(client_token)})")
        
        # Verificar se são válidos
        if len(instance_id) < 10:
            print("   ⚠️  Instance ID parece muito curto")
        if len(token) < 10:
            print("   ⚠️  Token parece muito curto")
        if len(client_token) < 10:
            print("   ⚠️  Client Token parece muito curto")
        
        # Teste 2: Tentar diferentes combinações de headers
        print("\n2️⃣ Testando diferentes combinações de headers...")
        
        test_headers = [
            {"Client-Token": client_token, "Content-Type": "application/json"},
            {"client-token": client_token, "content-type": "application/json"},
            {"Client-Token": client_token},
            {"Authorization": f"Bearer {client_token}"},
            {"X-Client-Token": client_token}
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for i, headers in enumerate(test_headers, 1):
                try:
                    response = await client.get(f"{self.base_url}/status", headers=headers)
                    print(f"   Teste {i}: Status {response.status_code}")
                    if response.status_code == 200:
                        print(f"   ✅ Sucesso com headers: {list(headers.keys())}")
                        return True
                except Exception as e:
                    print(f"   Teste {i}: Erro - {str(e)}")
        
        return False
    
    async def test_different_endpoints(self):
        """Testa diferentes endpoints da API"""
        print("\n🌐 TESTE DE DIFERENTES ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            "/status",
            "/connection",
            "/qr-code",
            "/webhook",
            "/messages"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for endpoint in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = await client.get(url, headers=self.headers)
                    print(f"   {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ {endpoint} funcionando")
                    elif response.status_code == 403:
                        print(f"   ❌ {endpoint} - Forbidden")
                    elif response.status_code == 404:
                        print(f"   ⚠️  {endpoint} - Not Found")
                    else:
                        print(f"   ❓ {endpoint} - {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint} - Erro: {str(e)}")
    
    async def test_webhook_configuration(self):
        """Testa configuração de webhook"""
        print("\n🔗 TESTE DE CONFIGURAÇÃO DE WEBHOOK")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Verificar webhook atual
                response = await client.get(f"{self.base_url}/webhook", headers=self.headers)
                
                if response.status_code == 200:
                    webhook_data = response.json()
                    self.log_info("Webhook Atual", webhook_data)
                else:
                    print(f"   ❌ Erro ao obter webhook: {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Erro no teste de webhook: {str(e)}")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos testes"""
        print("\n💡 RECOMENDAÇÕES")
        print("=" * 50)
        
        print("1️⃣ Verificar credenciais:")
        print("   - Acesse o painel do Z-API")
        print("   - Verifique se as credenciais estão corretas")
        print("   - Confirme se a instância está ativa")
        
        print("\n2️⃣ Verificar status da instância:")
        print("   - Verifique se o WhatsApp está conectado")
        print("   - Confirme se não há bloqueios")
        
        print("\n3️⃣ Verificar permissões:")
        print("   - Confirme se o Client-Token tem permissões adequadas")
        print("   - Verifique se a instância permite acesso via API")
        
        print("\n4️⃣ Testar manualmente:")
        print("   - Use o painel do Z-API para testar envio de mensagens")
        print("   - Verifique se há erros no painel")
        
        print("\n5️⃣ Contatar suporte:")
        print("   - Se os problemas persistirem, contate o suporte do Z-API")
        print("   - Forneça os logs de erro para análise")
    
    async def run_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        print("🚀 DIAGNÓSTICO DETALHADO Z-API")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Informações básicas
        self.log_info("Configurações Atuais", {
            "base_url": settings.zapi_base_url,
            "instance_id": settings.zapi_instance_id[:10] + "...",
            "token": settings.zapi_token[:10] + "...",
            "client_token": settings.zapi_client_token[:10] + "..."
        })
        
        # Executar testes
        await self.test_connection_basic()
        await self.test_credentials_validation()
        await self.test_different_endpoints()
        await self.test_webhook_configuration()
        
        # Gerar recomendações
        self.generate_recommendations()
        
        print("\n🎯 DIAGNÓSTICO CONCLUÍDO!")
        print("Verifique as informações acima para identificar o problema.")

async def main():
    """Função principal"""
    try:
        diagnostico = ZAPIDiagnostico()
        await diagnostico.run_diagnostico_completo()
        
    except KeyboardInterrupt:
        print("\n⏹️ Diagnóstico interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 