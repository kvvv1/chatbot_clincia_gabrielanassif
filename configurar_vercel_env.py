#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente no Vercel
"""

import os
import json
import subprocess
import sys

def check_vercel_cli():
    """Verifica se o Vercel CLI está instalado"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI não encontrado")
        return False

def configurar_variaveis_vercel():
    """Configura as variáveis de ambiente no Vercel"""
    
    print("🔧 CONFIGURANDO VARIÁVEIS DE AMBIENTE NO VERCEL")
    print("=" * 60)
    
    # Verificar se Vercel CLI está instalado
    if not check_vercel_cli():
        print("\n📦 Instalando Vercel CLI...")
        try:
            subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
            print("✅ Vercel CLI instalado com sucesso!")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar Vercel CLI")
            print("💡 Instale manualmente: npm install -g vercel")
            return False
    
    # Credenciais Z-API (do arquivo de configuração)
    zapi_config = {
        'ZAPI_INSTANCE_ID': 'VARIABLE_FROM_ENV',
        'ZAPI_TOKEN': 'VARIABLE_FROM_ENV',
        'ZAPI_CLIENT_TOKEN': 'VARIABLE_FROM_ENV',
        'ZAPI_BASE_URL': 'https://api.z-api.io'
    }
    
    # Configuração Supabase
    supabase_config = {
        'SUPABASE_URL': 'https://feqylqrphdpeeusdyeyw.supabase.co',
        'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI',
        'SUPABASE_SERVICE_ROLE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8'
    }
    
    # Configuração GestãoDS
    gestaods_config = {
        'GESTAODS_API_URL': 'https://apidev.gestaods.com.br',
        'GESTAODS_TOKEN': '733a8e19a94b65d58390da380ac946b6d603a535'
    }
    
    # Configuração da aplicação
    app_config = {
        'APP_HOST': '0.0.0.0',
        'APP_PORT': '8000',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'WEBSOCKET_ENABLED': 'false',
        'WEBSOCKET_MAX_CONNECTIONS': '10',
        'CORS_ORIGINS': '*',
        'CORS_ALLOW_CREDENTIALS': 'false'
    }
    
    # Configuração da clínica
    clinic_config = {
        'CLINIC_NAME': 'Clínica Gabriela Nassif',
        'CLINIC_PHONE': '+553198600366',
        'REMINDER_HOUR': '18',
        'REMINDER_MINUTE': '0'
    }
    
    # Combinar todas as configurações
    all_vars = {**zapi_config, **supabase_config, **gestaods_config, **app_config, **clinic_config}
    
    print(f"📋 Configurando {len(all_vars)} variáveis de ambiente...")
    
    # Fazer login no Vercel (se necessário)
    print("\n1. 🔐 Verificando login no Vercel...")
    try:
        result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Logado como: {result.stdout.strip()}")
        else:
            print("   ⚠️ Não logado, fazendo login...")
            subprocess.run(['vercel', 'login'], check=True)
    except subprocess.CalledProcessError:
        print("   ❌ Erro no login do Vercel")
        return False
    
    # Configurar cada variável
    print("\n2. ⚙️ Configurando variáveis...")
    
    for var_name, var_value in all_vars.items():
        try:
            print(f"   🔧 {var_name}...")
            
            # Usar vercel env add para adicionar a variável
            cmd = ['vercel', 'env', 'add', var_name, 'production']
            
            # Executar o comando e fornecer o valor via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=var_value)
            
            if process.returncode == 0:
                print(f"      ✅ {var_name} configurada")
            else:
                print(f"      ❌ Erro ao configurar {var_name}: {stderr}")
                
        except Exception as e:
            print(f"      ❌ Erro: {str(e)}")
    
    print("\n3. 🚀 Fazendo redeploy...")
    try:
        subprocess.run(['vercel', '--prod'], check=True)
        print("   ✅ Redeploy realizado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro no redeploy: {str(e)}")
    
    print("\n4. 🎯 Resumo da configuração:")
    print("=" * 60)
    print("✅ Variáveis Z-API configuradas")
    print("✅ Variáveis Supabase configuradas") 
    print("✅ Variáveis GestãoDS configuradas")
    print("✅ Variáveis da aplicação configuradas")
    print("✅ Variáveis da clínica configuradas")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Configure o webhook no painel Z-API:")
    print("   URL: https://chatbot-clincia.vercel.app/webhook")
    print("2. Teste o bot enviando uma mensagem")
    print("3. Verifique os logs no Vercel")
    
    return True

def configuracao_manual():
    """Mostra instruções para configuração manual"""
    print("\n📋 CONFIGURAÇÃO MANUAL NO VERCEL")
    print("=" * 60)
    print("1. Acesse: https://vercel.com/dashboard")
    print("2. Vá para seu projeto: chatbot-clincia")
    print("3. Clique em 'Settings' → 'Environment Variables'")
    print("4. Adicione as seguintes variáveis:")
    
    configs = {
        'Z-API': {
            'ZAPI_INSTANCE_ID': 'VARIABLE_FROM_ENV',
            'ZAPI_TOKEN': 'VARIABLE_FROM_ENV',
            'ZAPI_CLIENT_TOKEN': 'VARIABLE_FROM_ENV',
            'ZAPI_BASE_URL': 'https://api.z-api.io'
        },
        'Supabase': {
            'SUPABASE_URL': 'https://feqylqrphdpeeusdyeyw.supabase.co',
            'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI'
        },
        'GestãoDS': {
            'GESTAODS_API_URL': 'https://apidev.gestaods.com.br',
            'GESTAODS_TOKEN': '733a8e19a94b65d58390da380ac946b6d603a535'
        }
    }
    
    for category, vars_dict in configs.items():
        print(f"\n{category}:")
        for var_name, var_value in vars_dict.items():
            print(f"   {var_name} = {var_value}")
    
    print("\n5. Clique em 'Save'")
    print("6. Faça um novo deploy")

if __name__ == "__main__":
    print("🔧 CONFIGURADOR DE VARIÁVEIS VERCEL")
    print("=" * 60)
    
    # Perguntar se quer configuração automática ou manual
    print("Escolha o método de configuração:")
    print("1. Automática (requer Vercel CLI)")
    print("2. Manual (instruções)")
    
    try:
        choice = input("\nDigite sua escolha (1 ou 2): ").strip()
        
        if choice == "1":
            configurar_variaveis_vercel()
        elif choice == "2":
            configuracao_manual()
        else:
            print("❌ Escolha inválida")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        sys.exit(1) 