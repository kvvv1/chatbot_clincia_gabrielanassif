#!/usr/bin/env python3
"""
Script para verificar tabelas e colunas no Supabase
"""

import os
import asyncio
from supabase import create_client, Client
from app.config import settings

async def verificar_supabase():
    """Verifica as tabelas e colunas no Supabase"""
    print("🔍 Verificando tabelas e colunas no Supabase...")
    
    try:
        # Criar cliente Supabase
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        
        print(f"✅ Conectado ao Supabase: {settings.supabase_url}")
        
        # 1. Verificar tabelas existentes
        print("\n📋 Tabelas existentes:")
        try:
            # Tentar listar tabelas (pode não funcionar dependendo das permissões)
            result = supabase.table('conversations').select('*').limit(1).execute()
            print("   ✅ Tabela 'conversations' existe")
        except Exception as e:
            print(f"   ❌ Erro ao acessar 'conversations': {e}")
        
        try:
            result = supabase.table('appointments').select('*').limit(1).execute()
            print("   ✅ Tabela 'appointments' existe")
        except Exception as e:
            print(f"   ❌ Erro ao acessar 'appointments': {e}")
        
        try:
            result = supabase.table('waiting_list').select('*').limit(1).execute()
            print("   ✅ Tabela 'waiting_list' existe")
        except Exception as e:
            print(f"   ❌ Erro ao acessar 'waiting_list': {e}")
        
        # 2. Verificar estrutura das tabelas
        print("\n🏗️  Estrutura das tabelas:")
        
        # Conversations
        print("\n   📝 Tabela 'conversations':")
        try:
            result = supabase.table('conversations').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                print(f"      Colunas: {', '.join(columns)}")
            else:
                print("      Tabela vazia - não é possível inferir colunas")
        except Exception as e:
            print(f"      ❌ Erro: {e}")
        
        # Appointments
        print("\n   📅 Tabela 'appointments':")
        try:
            result = supabase.table('appointments').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                print(f"      Colunas: {', '.join(columns)}")
            else:
                print("      Tabela vazia - não é possível inferir colunas")
        except Exception as e:
            print(f"      ❌ Erro: {e}")
        
        # Waiting List
        print("\n   ⏳ Tabela 'waiting_list':")
        try:
            result = supabase.table('waiting_list').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                print(f"      Colunas: {', '.join(columns)}")
            else:
                print("      Tabela vazia - não é possível inferir colunas")
        except Exception as e:
            print(f"      ❌ Erro: {e}")
        
        # 3. Verificar dados existentes
        print("\n📊 Dados existentes:")
        
        try:
            result = supabase.table('conversations').select('count').execute()
            print(f"   Conversations: {len(result.data)} registros")
        except Exception as e:
            print(f"   ❌ Erro ao contar conversations: {e}")
        
        try:
            result = supabase.table('appointments').select('count').execute()
            print(f"   Appointments: {len(result.data)} registros")
        except Exception as e:
            print(f"   ❌ Erro ao contar appointments: {e}")
        
        try:
            result = supabase.table('waiting_list').select('count').execute()
            print(f"   Waiting List: {len(result.data)} registros")
        except Exception as e:
            print(f"   ❌ Erro ao contar waiting_list: {e}")
        
        # 4. Teste de inserção
        print("\n🧪 Teste de inserção:")
        try:
            test_data = {
                'phone': 'test_phone',
                'state': 'test_state',
                'context': {}
            }
            result = supabase.table('conversations').insert(test_data).execute()
            print("   ✅ Inserção em conversations funcionou")
            
            # Limpar dados de teste
            supabase.table('conversations').delete().eq('phone', 'test_phone').execute()
            print("   ✅ Limpeza de dados de teste funcionou")
            
        except Exception as e:
            print(f"   ❌ Erro no teste de inserção: {e}")
        
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        print("Verifique as variáveis de ambiente:")
        print(f"   SUPABASE_URL: {settings.supabase_url}")
        print(f"   SUPABASE_ANON_KEY: {'***' if settings.supabase_anon_key else 'NÃO CONFIGURADO'}")

if __name__ == "__main__":
    asyncio.run(verificar_supabase()) 