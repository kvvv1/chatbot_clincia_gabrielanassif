#!/usr/bin/env python3
"""
Script para configurar as variáveis de ambiente corretas
"""

import os
from dotenv import load_dotenv

def configurar_variaveis():
    """Configura as variáveis de ambiente corretas"""
    print("🔧 Configurando variáveis de ambiente...")
    
    # Carregar .env se existir
    load_dotenv()
    
    # Configurações do Supabase
    supabase_url = "https://feqylqrphdpeeusdyeyw.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI"
    
    # Configurações do Z-API
    zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
    zapi_token = os.getenv("ZAPI_TOKEN", "")
    
    # Configurações que precisam ser verificadas
    zapi_client_token = os.getenv('ZAPI_CLIENT_TOKEN', 'seu_client_token_aqui')
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Supabase Anon Key: {supabase_anon_key[:20]}...")
    print(f"✅ Z-API Instance ID: {zapi_instance_id}")
    print(f"✅ Z-API Token: {zapi_token}")
    print(f"⚠️  Z-API Client Token: {zapi_client_token}")
    
    # Criar/atualizar arquivo .env
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={supabase_anon_key}

# Z-API Configuration
ZAPI_BASE_URL=https://api.z-api.io
ZAPI_INSTANCE_ID={zapi_instance_id}
ZAPI_TOKEN={zapi_token}
ZAPI_CLIENT_TOKEN={zapi_client_token}

# App Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
ENVIRONMENT=development
DEBUG=true

# GestãoDS Configuration
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=733a8e19a94b65d58390da380ac946b6d603a535

# Clinic Configuration
CLINIC_NAME=Clínica Gabriela Nassif
CLINIC_PHONE=+553198600366
REMINDER_HOUR=18
REMINDER_MINUTE=0
"""
    
    # Salvar no arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ Arquivo .env atualizado!")
    print("📝 Variáveis configuradas:")
    print("   - SUPABASE_URL e SUPABASE_ANON_KEY")
    print("   - ZAPI_INSTANCE_ID e ZAPI_TOKEN")
    print("   - Outras configurações padrão")
    
    print("\n⚠️  IMPORTANTE: Você ainda precisa configurar o ZAPI_CLIENT_TOKEN!")
    print("   Obtenha no painel do Z-API e atualize o arquivo .env")
    
    return {
        'supabase_url': supabase_url,
        'supabase_anon_key': supabase_anon_key,
        'zapi_instance_id': zapi_instance_id,
        'zapi_token': zapi_token,
        'zapi_client_token': zapi_client_token
    }

if __name__ == "__main__":
    configurar_variaveis() 