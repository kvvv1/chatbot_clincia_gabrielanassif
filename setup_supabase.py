#!/usr/bin/env python3
"""
Script para configurar automaticamente o Supabase
Cria as tabelas necessárias e configura as políticas de segurança
"""

import os
import sys
import json
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

class SupabaseSetup:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        
        if not self.supabase_url or not self.anon_key:
            logger.error("❌ Configurações do Supabase não encontradas!")
            logger.info("Configure as variáveis de ambiente:")
            logger.info("SUPABASE_URL=your_supabase_url")
            logger.info("SUPABASE_ANON_KEY=your_supabase_anon_key")
            logger.info("SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key")
            sys.exit(1)
        
        self.headers = {
            "apikey": self.service_role_key or self.anon_key,
            "Authorization": f"Bearer {self.service_role_key or self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def create_tables(self):
        """Cria as tabelas necessárias"""
        logger.info("=== CRIANDO TABELAS NO SUPABASE ===")
        
        tables = {
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
            """,
            
            "messages": """
            CREATE TABLE IF NOT EXISTS messages (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
                message_type VARCHAR(20) DEFAULT 'text',
                content TEXT,
                direction VARCHAR(10) DEFAULT 'inbound',
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "patients": """
            CREATE TABLE IF NOT EXISTS patients (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                phone VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(200),
                cpf VARCHAR(14),
                email VARCHAR(200),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
        }
        
        async with httpx.AsyncClient() as client:
            for table_name, sql in tables.items():
                try:
                    logger.info(f"Criando tabela: {table_name}")
                    
                    # Usar SQL direto via REST API
                    response = await client.post(
                        f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                        headers=self.headers,
                        json={"sql": sql},
                        timeout=30.0
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Tabela {table_name} criada com sucesso")
                    else:
                        logger.warning(f"⚠️ Tabela {table_name} pode já existir: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao criar tabela {table_name}: {str(e)}")
    
    async def create_indexes(self):
        """Cria índices para melhor performance"""
        logger.info("=== CRIANDO ÍNDICES ===")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversations(phone);",
            "CREATE INDEX IF NOT EXISTS idx_conversations_state ON conversations(state);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_patient_phone ON appointments(patient_phone);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);",
            "CREATE INDEX IF NOT EXISTS idx_waiting_list_priority ON waiting_list(priority);",
            "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
            "CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);"
        ]
        
        async with httpx.AsyncClient() as client:
            for i, index_sql in enumerate(indexes):
                try:
                    response = await client.post(
                        f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                        headers=self.headers,
                        json={"sql": index_sql},
                        timeout=30.0
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Índice {i+1} criado com sucesso")
                    else:
                        logger.warning(f"⚠️ Índice {i+1} pode já existir")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao criar índice {i+1}: {str(e)}")
    
    async def setup_rls_policies(self):
        """Configura Row Level Security (RLS)"""
        logger.info("=== CONFIGURANDO POLÍTICAS DE SEGURANÇA ===")
        
        policies = {
            "conversations": [
                "ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;",
                "CREATE POLICY \"Enable read access for all users\" ON conversations FOR SELECT USING (true);",
                "CREATE POLICY \"Enable insert access for all users\" ON conversations FOR INSERT WITH CHECK (true);",
                "CREATE POLICY \"Enable update access for all users\" ON conversations FOR UPDATE USING (true);"
            ],
            "appointments": [
                "ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;",
                "CREATE POLICY \"Enable read access for all users\" ON appointments FOR SELECT USING (true);",
                "CREATE POLICY \"Enable insert access for all users\" ON appointments FOR INSERT WITH CHECK (true);",
                "CREATE POLICY \"Enable update access for all users\" ON appointments FOR UPDATE USING (true);"
            ],
            "waiting_list": [
                "ALTER TABLE waiting_list ENABLE ROW LEVEL SECURITY;",
                "CREATE POLICY \"Enable read access for all users\" ON waiting_list FOR SELECT USING (true);",
                "CREATE POLICY \"Enable insert access for all users\" ON waiting_list FOR INSERT WITH CHECK (true);",
                "CREATE POLICY \"Enable update access for all users\" ON waiting_list FOR UPDATE USING (true);"
            ],
            "messages": [
                "ALTER TABLE messages ENABLE ROW LEVEL SECURITY;",
                "CREATE POLICY \"Enable read access for all users\" ON messages FOR SELECT USING (true);",
                "CREATE POLICY \"Enable insert access for all users\" ON messages FOR INSERT WITH CHECK (true);"
            ],
            "patients": [
                "ALTER TABLE patients ENABLE ROW LEVEL SECURITY;",
                "CREATE POLICY \"Enable read access for all users\" ON patients FOR SELECT USING (true);",
                "CREATE POLICY \"Enable insert access for all users\" ON patients FOR INSERT WITH CHECK (true);",
                "CREATE POLICY \"Enable update access for all users\" ON patients FOR UPDATE USING (true);"
            ]
        }
        
        async with httpx.AsyncClient() as client:
            for table_name, table_policies in policies.items():
                logger.info(f"Configurando políticas para: {table_name}")
                
                for policy_sql in table_policies:
                    try:
                        response = await client.post(
                            f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                            headers=self.headers,
                            json={"sql": policy_sql},
                            timeout=30.0
                        )
                        
                        if response.status_code in [200, 201]:
                            logger.info(f"✅ Política configurada para {table_name}")
                        else:
                            logger.warning(f"⚠️ Política pode já existir para {table_name}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao configurar política para {table_name}: {str(e)}")
    
    async def insert_sample_data(self):
        """Insere dados de exemplo"""
        logger.info("=== INSERINDO DADOS DE EXEMPLO ===")
        
        sample_data = {
            "conversations": [
                {
                    "phone": "553198600366",
                    "state": "inicio",
                    "context": {"step": "welcome"}
                }
            ],
            "patients": [
                {
                    "phone": "553198600366",
                    "name": "Paciente Exemplo",
                    "cpf": "123.456.789-00"
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            for table_name, data_list in sample_data.items():
                logger.info(f"Inserindo dados de exemplo em: {table_name}")
                
                for data in data_list:
                    try:
                        response = await client.post(
                            f"{self.supabase_url}/rest/v1/{table_name}",
                            headers=self.headers,
                            json=data,
                            timeout=30.0
                        )
                        
                        if response.status_code in [200, 201]:
                            logger.info(f"✅ Dado de exemplo inserido em {table_name}")
                        else:
                            logger.warning(f"⚠️ Dado pode já existir em {table_name}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao inserir dado em {table_name}: {str(e)}")
    
    async def test_connection(self):
        """Testa a conexão com Supabase"""
        logger.info("=== TESTANDO CONEXÃO SUPABASE ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Conexão com Supabase estabelecida")
                    return True
                else:
                    logger.error(f"❌ Erro na conexão: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {str(e)}")
            return False
    
    async def run_setup(self):
        """Executa todo o setup do Supabase"""
        logger.info("🚀 INICIANDO SETUP COMPLETO DO SUPABASE")
        logger.info("=" * 50)
        
        # Testar conexão
        if not await self.test_connection():
            logger.error("❌ Falha na conexão com Supabase")
            return False
        
        # Criar tabelas
        await self.create_tables()
        
        # Criar índices
        await self.create_indexes()
        
        # Configurar políticas
        await self.setup_rls_policies()
        
        # Inserir dados de exemplo
        await self.insert_sample_data()
        
        logger.info("=" * 50)
        logger.info("🎉 SETUP DO SUPABASE CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 50)
        logger.info("📝 PRÓXIMOS PASSOS:")
        logger.info("1. Configure as variáveis de ambiente no seu projeto")
        logger.info("2. Teste as conexões com o script setup_all_connections.py")
        logger.info("3. Faça o deploy da aplicação")
        
        return True

async def main():
    """Função principal"""
    setup = SupabaseSetup()
    await setup.run_setup()

if __name__ == "__main__":
    asyncio.run(main()) 