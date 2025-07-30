#!/usr/bin/env python3
"""
Script para configurar as tabelas necessárias no Supabase
"""

import os
import json
from supabase import create_client, Client
from typing import Dict, Any

def setup_supabase_tables():
    """Configura as tabelas necessárias no Supabase"""
    
    # Configurações do Supabase
    supabase_url = "https://feqylqrphdpeeusdyeyw.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc"
    
    print("🗄️ Configurando Tabelas no Supabase")
    print("=" * 50)
    print()
    
    try:
        # Conectar ao Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Conectado ao Supabase")
        
        # SQL para criar as tabelas
        tables_sql = {
            "conversations": """
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20) NOT NULL,
                state VARCHAR(50) DEFAULT 'inicio',
                context JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversations(phone);
            CREATE INDEX IF NOT EXISTS idx_conversations_state ON conversations(state);
            """,
            
            "appointments": """
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id),
                patient_cpf VARCHAR(14),
                patient_name VARCHAR(255),
                appointment_date TIMESTAMP WITH TIME ZONE,
                appointment_time VARCHAR(10),
                status VARCHAR(20) DEFAULT 'agendado',
                gestaods_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_appointments_cpf ON appointments(patient_cpf);
            CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
            CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
            """,
            
            "waiting_list": """
            CREATE TABLE IF NOT EXISTS waiting_list (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id),
                patient_cpf VARCHAR(14),
                patient_name VARCHAR(255),
                preferred_date DATE,
                preferred_time VARCHAR(10),
                status VARCHAR(20) DEFAULT 'aguardando',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_waiting_list_cpf ON waiting_list(patient_cpf);
            CREATE INDEX IF NOT EXISTS idx_waiting_list_status ON waiting_list(status);
            """,
            
            "message_logs": """
            CREATE TABLE IF NOT EXISTS message_logs (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id),
                message_id VARCHAR(100),
                direction VARCHAR(10) CHECK (direction IN ('in', 'out')),
                message_type VARCHAR(20),
                content TEXT,
                status VARCHAR(20),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_message_logs_conversation ON message_logs(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);
            """
        }
        
        # Executar criação das tabelas
        for table_name, sql in tables_sql.items():
            print(f"📝 Criando tabela: {table_name}")
            
            try:
                # Executar SQL via RPC (função personalizada)
                result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
                print(f"✅ Tabela {table_name} criada com sucesso")
                
            except Exception as e:
                print(f"⚠️ Erro ao criar tabela {table_name}: {str(e)}")
                print("📋 Execute manualmente no SQL Editor do Supabase:")
                print(f"SQL: {sql}")
                print()
        
        # Criar função para executar SQL (se não existir)
        create_function_sql = """
        CREATE OR REPLACE FUNCTION exec_sql(sql_query TEXT)
        RETURNS VOID AS $$
        BEGIN
            EXECUTE sql_query;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        try:
            supabase.rpc('exec_sql', {'sql_query': create_function_sql}).execute()
            print("✅ Função exec_sql criada")
        except:
            print("⚠️ Função exec_sql já existe ou erro na criação")
        
        print("\n🎉 Configuração das tabelas concluída!")
        print("📋 Próximos passos:")
        print("1. Verifique as tabelas no painel do Supabase")
        print("2. Teste o chatbot")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        print("📋 Verifique as credenciais e tente novamente")

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    print("\n🧪 Testando Conexão com Supabase...")
    
    try:
        supabase_url = "https://feqylqrphdpeeusdyeyw.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc"
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Testar conexão fazendo uma query simples
        result = supabase.table('conversations').select('count').limit(1).execute()
        
        print("✅ Conexão com Supabase funcionando!")
        print("📊 Tabelas acessíveis")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")

def main():
    """Função principal"""
    setup_supabase_tables()
    test_supabase_connection()

if __name__ == "__main__":
    main() 