#!/usr/bin/env python3
"""
Script completo para configurar todas as conexões do sistema de chatbot
Inclui: Supabase, Z-API, GestãoDS, WebSocket e Vercel
"""

import os
import sys
import json
import requests
import asyncio
import httpx
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionSetup:
    def __init__(self):
        self.config = {}
        self.test_results = {}
        
    def load_config(self):
        """Carrega configurações do arquivo .env ou variáveis de ambiente"""
        logger.info("=== CARREGANDO CONFIGURAÇÕES ===")
        
        # Configurações padrão
        self.config = {
            # Supabase
            "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
            "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", ""),
            "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
            
            # Z-API
            "ZAPI_INSTANCE_ID": os.getenv("ZAPI_INSTANCE_ID", "VARIABLE_FROM_ENV"),
            "ZAPI_TOKEN": os.getenv("ZAPI_TOKEN", "VARIABLE_FROM_ENV"),
            "ZAPI_CLIENT_TOKEN": os.getenv("ZAPI_CLIENT_TOKEN", "VARIABLE_FROM_ENV"),
            "ZAPI_BASE_URL": os.getenv("ZAPI_BASE_URL", "https://api.z-api.io"),
            
            # GestãoDS
            "GESTAODS_API_URL": os.getenv("GESTAODS_API_URL", "https://apidev.gestaods.com.br"),
            "GESTAODS_TOKEN": os.getenv("GESTAODS_TOKEN", "733a8e19a94b65d58390da380ac946b6d603a535"),
            
            # App
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
            "DEBUG": os.getenv("DEBUG", "true"),
            "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "*"),
            
            # Clinic
            "CLINIC_NAME": os.getenv("CLINIC_NAME", "Clínica Gabriela Nassif"),
            "CLINIC_PHONE": os.getenv("CLINIC_PHONE", "553198600366"),
            "REMINDER_HOUR": os.getenv("REMINDER_HOUR", "18"),
            "REMINDER_MINUTE": os.getenv("REMINDER_MINUTE", "0"),
            
            # WebSocket
            "WEBSOCKET_ENABLED": os.getenv("WEBSOCKET_ENABLED", "true"),
            "WEBSOCKET_MAX_CONNECTIONS": os.getenv("WEBSOCKET_MAX_CONNECTIONS", "50"),
            
            # Vercel
            "VERCEL": os.getenv("VERCEL", "0"),
            "VERCEL_URL": os.getenv("VERCEL_URL", "")
        }
        
        logger.info("Configurações carregadas com sucesso")
        return self.config
    
    async def test_supabase_connection(self) -> bool:
        """Testa conexão com Supabase"""
        logger.info("=== TESTANDO CONEXÃO SUPABASE ===")
        
        if not self.config["SUPABASE_URL"] or not self.config["SUPABASE_ANON_KEY"]:
            logger.warning("❌ Configurações do Supabase não encontradas")
            logger.info("Para configurar Supabase:")
            logger.info("1. Acesse: https://supabase.com")
            logger.info("2. Crie um novo projeto")
            logger.info("3. Copie as credenciais para as variáveis de ambiente")
            return False
        
        try:
            headers = {
                "apikey": self.config["SUPABASE_ANON_KEY"],
                "Authorization": f"Bearer {self.config['SUPABASE_ANON_KEY']}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Teste básico de conexão
                response = await client.get(
                    f"{self.config['SUPABASE_URL']}/rest/v1/",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Conexão com Supabase estabelecida")
                    
                    # Teste de criação de tabela se não existir
                    await self.setup_supabase_tables()
                    return True
                else:
                    logger.error(f"❌ Erro na conexão Supabase: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Supabase: {str(e)}")
            return False
    
    async def setup_supabase_tables(self):
        """Configura tabelas necessárias no Supabase"""
        logger.info("=== CONFIGURANDO TABELAS SUPABASE ===")
        
        try:
            headers = {
                "apikey": self.config["SUPABASE_SERVICE_ROLE_KEY"] or self.config["SUPABASE_ANON_KEY"],
                "Authorization": f"Bearer {self.config['SUPABASE_SERVICE_ROLE_KEY'] or self.config['SUPABASE_ANON_KEY']}",
                "Content-Type": "application/json"
            }
            
            # SQL para criar tabelas
            tables_sql = {
                "conversations": """
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    phone VARCHAR(20) NOT NULL,
                    state VARCHAR(50) DEFAULT 'inicio',
                    context JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                "appointments": """
                CREATE TABLE IF NOT EXISTS appointments (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    patient_id VARCHAR(100),
                    patient_name VARCHAR(200),
                    patient_phone VARCHAR(20),
                    appointment_date TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(50) DEFAULT 'scheduled',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                "waiting_list": """
                CREATE TABLE IF NOT EXISTS waiting_list (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    patient_name VARCHAR(200),
                    patient_phone VARCHAR(20),
                    priority INTEGER DEFAULT 1,
                    reason TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            }
            
            async with httpx.AsyncClient() as client:
                for table_name, sql in tables_sql.items():
                    try:
                        response = await client.post(
                            f"{self.config['SUPABASE_URL']}/rest/v1/rpc/exec_sql",
                            headers=headers,
                            json={"sql": sql},
                            timeout=30.0
                        )
                        
                        if response.status_code in [200, 201]:
                            logger.info(f"✅ Tabela {table_name} configurada")
                        else:
                            logger.warning(f"⚠️ Tabela {table_name} pode já existir")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao criar tabela {table_name}: {str(e)}")
            
            logger.info("✅ Configuração das tabelas concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar tabelas: {str(e)}")
    
    async def test_zapi_connection(self) -> bool:
        """Testa conexão com Z-API"""
        logger.info("=== TESTANDO CONEXÃO Z-API ===")
        
        if not self.config["ZAPI_INSTANCE_ID"] or not self.config["ZAPI_TOKEN"]:
            logger.warning("❌ Configurações do Z-API não encontradas")
            return False
        
        try:
            base_url = f"{self.config['ZAPI_BASE_URL']}/instances/{self.config['ZAPI_INSTANCE_ID']}/token/{self.config['ZAPI_TOKEN']}"
            headers = {
                "Client-Token": self.config["ZAPI_CLIENT_TOKEN"],
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Teste de status da instância
                response = await client.get(
                    f"{base_url}/status",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Z-API conectado - Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Erro na conexão Z-API: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Z-API: {str(e)}")
            return False
    
    async def test_gestaods_connection(self) -> bool:
        """Testa conexão com GestãoDS"""
        logger.info("=== TESTANDO CONEXÃO GESTÃODS ===")
        
        if not self.config["GESTAODS_TOKEN"]:
            logger.warning("❌ Token do GestãoDS não encontrado")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config['GESTAODS_TOKEN']}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Teste básico de conexão
                response = await client.get(
                    f"{self.config['GESTAODS_API_URL']}/api/v1/health",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Conexão com GestãoDS estabelecida")
                    return True
                else:
                    logger.warning(f"⚠️ GestãoDS pode estar indisponível: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar com GestãoDS: {str(e)}")
            return False
    
    async def test_websocket_connection(self) -> bool:
        """Testa configuração do WebSocket"""
        logger.info("=== TESTANDO CONFIGURAÇÃO WEBSOCKET ===")
        
        if self.config["WEBSOCKET_ENABLED"].lower() == "true":
            logger.info("✅ WebSocket habilitado")
            logger.info(f"   Máximo de conexões: {self.config['WEBSOCKET_MAX_CONNECTIONS']}")
            return True
        else:
            logger.info("⚠️ WebSocket desabilitado")
            return False
    
    def test_vercel_configuration(self) -> bool:
        """Testa configuração do Vercel"""
        logger.info("=== TESTANDO CONFIGURAÇÃO VERCEL ===")
        
        if self.config["VERCEL"] == "1":
            logger.info("✅ Ambiente Vercel detectado")
            logger.info(f"   URL: {self.config['VERCEL_URL']}")
            return True
        else:
            logger.info("⚠️ Ambiente local detectado")
            return False
    
    async def test_webhook_endpoint(self) -> bool:
        """Testa endpoint do webhook"""
        logger.info("=== TESTANDO ENDPOINT WEBHOOK ===")
        
        webhook_url = self.config.get("VERCEL_URL", "http://localhost:8000")
        if not webhook_url.startswith("http"):
            webhook_url = f"https://{webhook_url}"
        
        webhook_url = f"{webhook_url}/webhook"
        
        try:
            async with httpx.AsyncClient() as client:
                # Teste GET
                response = await client.get(webhook_url, timeout=10.0)
                if response.status_code == 200:
                    logger.info("✅ Endpoint webhook respondendo")
                    
                    # Teste POST
                    test_data = {
                        "event": "message",
                        "data": {
                            "id": "test_123",
                            "type": "text",
                            "from": "553198600366@c.us",
                            "fromMe": False,
                            "text": {"body": "teste"}
                        }
                    }
                    
                    response = await client.post(
                        webhook_url,
                        json=test_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        logger.info("✅ Webhook processando mensagens")
                        return True
                    else:
                        logger.warning(f"⚠️ Webhook retornou status: {response.status_code}")
                        return False
                else:
                    logger.warning(f"⚠️ Endpoint webhook retornou: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar webhook: {str(e)}")
            return False
    
    def create_env_file(self):
        """Cria arquivo .env com as configurações"""
        logger.info("=== CRIANDO ARQUIVO .ENV ===")
        
        env_content = f"""# Configurações do Sistema de Chatbot
# Supabase Configuration
SUPABASE_URL={self.config['SUPABASE_URL']}
SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
SUPABASE_SERVICE_ROLE_KEY={self.config['SUPABASE_SERVICE_ROLE_KEY']}

# Z-API Configuration
ZAPI_INSTANCE_ID={self.config['ZAPI_INSTANCE_ID']}
ZAPI_TOKEN={self.config['ZAPI_TOKEN']}
ZAPI_CLIENT_TOKEN={self.config['ZAPI_CLIENT_TOKEN']}
ZAPI_BASE_URL={self.config['ZAPI_BASE_URL']}

# GestãoDS Configuration
GESTAODS_API_URL={self.config['GESTAODS_API_URL']}
GESTAODS_TOKEN={self.config['GESTAODS_TOKEN']}

# App Configuration
ENVIRONMENT={self.config['ENVIRONMENT']}
DEBUG={self.config['DEBUG']}
CORS_ORIGINS={self.config['CORS_ORIGINS']}

# Clinic Information
CLINIC_NAME={self.config['CLINIC_NAME']}
CLINIC_PHONE={self.config['CLINIC_PHONE']}
REMINDER_HOUR={self.config['REMINDER_HOUR']}
REMINDER_MINUTE={self.config['REMINDER_MINUTE']}

# WebSocket Configuration
WEBSOCKET_ENABLED={self.config['WEBSOCKET_ENABLED']}
WEBSOCKET_MAX_CONNECTIONS={self.config['WEBSOCKET_MAX_CONNECTIONS']}

# Vercel Configuration
VERCEL={self.config['VERCEL']}
VERCEL_URL={self.config['VERCEL_URL']}
"""
        
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            logger.info("✅ Arquivo .env criado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo .env: {str(e)}")
            return False
    
    def generate_vercel_env(self):
        """Gera configuração para Vercel"""
        logger.info("=== GERANDO CONFIGURAÇÃO VERCEL ===")
        
        vercel_env = {
            "SUPABASE_URL": self.config["SUPABASE_URL"],
            "SUPABASE_ANON_KEY": self.config["SUPABASE_ANON_KEY"],
            "SUPABASE_SERVICE_ROLE_KEY": self.config["SUPABASE_SERVICE_ROLE_KEY"],
            "ZAPI_INSTANCE_ID": self.config["ZAPI_INSTANCE_ID"],
            "ZAPI_TOKEN": self.config["ZAPI_TOKEN"],
            "ZAPI_CLIENT_TOKEN": self.config["ZAPI_CLIENT_TOKEN"],
            "ZAPI_BASE_URL": self.config["ZAPI_BASE_URL"],
            "GESTAODS_API_URL": self.config["GESTAODS_API_URL"],
            "GESTAODS_TOKEN": self.config["GESTAODS_TOKEN"],
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "CORS_ORIGINS": "*",
            "CLINIC_NAME": self.config["CLINIC_NAME"],
            "CLINIC_PHONE": self.config["CLINIC_PHONE"],
            "REMINDER_HOUR": self.config["REMINDER_HOUR"],
            "REMINDER_MINUTE": self.config["REMINDER_MINUTE"],
            "WEBSOCKET_ENABLED": "false",
            "WEBSOCKET_MAX_CONNECTIONS": "10",
            "VERCEL": "1"
        }
        
        try:
            with open("vercel_env_vars.json", "w", encoding="utf-8") as f:
                json.dump(vercel_env, f, indent=2)
            logger.info("✅ Arquivo vercel_env_vars.json criado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo Vercel: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes de conexão"""
        logger.info("🚀 INICIANDO TESTES DE CONEXÃO COMPLETOS")
        logger.info("=" * 50)
        
        # Carregar configurações
        self.load_config()
        
        # Executar testes
        self.test_results = {
            "supabase": await self.test_supabase_connection(),
            "zapi": await self.test_zapi_connection(),
            "gestaods": await self.test_gestaods_connection(),
            "websocket": await self.test_websocket_connection(),
            "vercel": self.test_vercel_configuration(),
            "webhook": await self.test_webhook_endpoint()
        }
        
        # Criar arquivos de configuração
        self.create_env_file()
        self.generate_vercel_env()
        
        # Relatório final
        self.print_final_report()
    
    def print_final_report(self):
        """Imprime relatório final dos testes"""
        logger.info("=" * 50)
        logger.info("📊 RELATÓRIO FINAL DE CONEXÕES")
        logger.info("=" * 50)
        
        for service, status in self.test_results.items():
            icon = "✅" if status else "❌"
            logger.info(f"{icon} {service.upper()}: {'CONECTADO' if status else 'FALHOU'}")
        
        success_count = sum(self.test_results.values())
        total_count = len(self.test_results)
        
        logger.info("=" * 50)
        logger.info(f"📈 RESULTADO: {success_count}/{total_count} conexões funcionando")
        
        if success_count == total_count:
            logger.info("🎉 TODAS AS CONEXÕES ESTÃO FUNCIONANDO!")
        elif success_count >= total_count * 0.8:
            logger.info("⚠️ A maioria das conexões está funcionando")
        else:
            logger.info("❌ Muitas conexões falharam - verifique as configurações")
        
        logger.info("=" * 50)
        logger.info("📝 PRÓXIMOS PASSOS:")
        logger.info("1. Configure as variáveis de ambiente no Vercel")
        logger.info("2. Faça o deploy da aplicação")
        logger.info("3. Configure o webhook no Z-API")
        logger.info("4. Teste o sistema completo")

async def main():
    """Função principal"""
    setup = ConnectionSetup()
    await setup.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 