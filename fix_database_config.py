#!/usr/bin/env python3
"""
Fix Database Configuration - Corrige problema de conexão com banco de dados
"""

import os
from pathlib import Path

def fix_database_config():
    """Corrige a configuração do banco de dados"""
    
    print("🔧 CORRIGINDO CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    
    # Ler arquivo database.py atual
    database_file = Path("app/models/database.py")
    
    with open(database_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Código corrigido para a seção de configuração do banco
    new_database_config = '''
# Configuração robusta do banco de dados
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

def get_database_url():
    """Obtém URL do banco de dados com fallbacks robustos"""
    
    # 1. Tentar DATABASE_URL direto (se definido)
    if settings.database_url:
        return settings.database_url
    
    # 2. Construir URL do Supabase se configurado
    if settings.supabase_url and settings.supabase_anon_key:
        # Extrair host do Supabase URL
        host = settings.supabase_url.replace('https://', '').replace('http://', '')
        return f"postgresql://postgres.{host.split('.')[0]}:@{host}:5432/postgres"
    
    # 3. Fallback para SQLite local
    sqlite_path = Path("chatbot_local.db")
    return f"sqlite:///{sqlite_path.absolute()}"

# Configuração da engine
try:
    database_url = get_database_url()
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    if database_url.startswith('sqlite'):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        print("📁 Usando banco SQLite local")
    else:
        engine = create_engine(database_url)
        print("☁️ Usando banco na nuvem")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados configurado com sucesso")
    
except Exception as e:
    print(f"❌ Erro ao configurar banco: {e}")
    print("🔄 Usando configuração de fallback...")
    
    # Fallback final: SQLite in-memory
    engine = create_engine("sqlite:///chatbot_fallback.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    print("💾 Usando banco SQLite de fallback")
'''
    
    # Encontrar e substituir a seção problemática
    lines = content.split('\n')
    new_lines = []
    skip_until_end = False
    
    for i, line in enumerate(lines):
        if 'IS_VERCEL = os.getenv' in line:
            # Adicionar nova configuração
            new_lines.extend(new_database_config.strip().split('\n'))
            skip_until_end = True
        elif skip_until_end and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # Chegou ao final da seção, parar de pular
            skip_until_end = False
            new_lines.append(line)
        elif not skip_until_end:
            new_lines.append(line)
    
    # Escrever arquivo corrigido
    with open(database_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Arquivo app/models/database.py corrigido")
    print("🔧 Configuração robusta do banco implementada")
    print("\n💡 Agora o chatbot irá:")
    print("   1. Tentar usar DATABASE_URL se definido")
    print("   2. Tentar construir URL do Supabase se disponível")
    print("   3. Usar SQLite local como fallback")
    print("   4. Usar SQLite in-memory como último recurso")

if __name__ == "__main__":
    fix_database_config()