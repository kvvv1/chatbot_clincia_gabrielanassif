#!/usr/bin/env python3
"""
Script para verificar se as variáveis de ambiente estão sendo carregadas corretamente
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório app ao path
sys.path.append(str(Path(__file__).parent / "app"))

try:
    from config import get_settings
    print("✅ Configurações carregadas com sucesso!")
    
    settings = get_settings()
    
    print("\n📋 Variáveis de Ambiente Carregadas:")
    print("=" * 50)
    
    # Z-API
    print(f"ZAPI_INSTANCE_ID: {'✅' if settings.zapi_instance_id else '❌'} {settings.zapi_instance_id[:10]}...")
    print(f"ZAPI_TOKEN: {'✅' if settings.zapi_token else '❌'} {settings.zapi_token[:10]}...")
    print(f"ZAPI_CLIENT_TOKEN: {'✅' if settings.zapi_client_token else '❌'} {settings.zapi_client_token[:10]}...")
    
    # GestãoDS
    print(f"GESTAODS_API_URL: {'✅' if settings.gestaods_api_url else '❌'} {settings.gestaods_api_url}")
    print(f"GESTAODS_TOKEN: {'✅' if settings.gestaods_token else '❌'} {settings.gestaods_token[:10]}...")
    
    # Supabase
    print(f"SUPABASE_URL: {'✅' if settings.supabase_url else '❌'} {settings.supabase_url}")
    print(f"SUPABASE_ANON_KEY: {'✅' if settings.supabase_anon_key else '❌'} {settings.supabase_anon_key[:20]}...")
    
    # App
    print(f"ENVIRONMENT: {settings.environment}")
    print(f"DEBUG: {settings.debug}")
    print(f"CLINIC_NAME: {settings.clinic_name}")
    print(f"CLINIC_PHONE: {settings.clinic_phone}")
    
    print("\n🎯 Status Geral:")
    if all([settings.zapi_instance_id, settings.zapi_token, settings.zapi_client_token]):
        print("✅ Z-API: Configurado")
    else:
        print("❌ Z-API: Faltam credenciais")
        
    if all([settings.gestaods_api_url, settings.gestaods_token]):
        print("✅ GestãoDS: Configurado")
    else:
        print("❌ GestãoDS: Faltam credenciais")
        
    if all([settings.supabase_url, settings.supabase_anon_key]):
        print("✅ Supabase: Configurado")
    else:
        print("❌ Supabase: Faltam credenciais")
        
except Exception as e:
    print(f"❌ Erro ao carregar configurações: {e}")
    sys.exit(1) 