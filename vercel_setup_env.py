#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente no Vercel
Execute este script para configurar todas as variáveis necessárias
"""

import os
import subprocess
import sys

def run_command(command):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_vercel_cli():
    """Verifica se o Vercel CLI está instalado"""
    success, stdout, stderr = run_command("vercel --version")
    if not success:
        print("❌ Vercel CLI não encontrado!")
        print("Instale com: npm i -g vercel")
        return False
    print(f"✅ Vercel CLI encontrado: {stdout.strip()}")
    return True

def get_project_info():
    """Obtém informações do projeto Vercel"""
    success, stdout, stderr = run_command("vercel ls")
    if not success:
        print("❌ Erro ao listar projetos Vercel")
        print("Certifique-se de estar logado: vercel login")
        return None
    
    print("📋 Projetos Vercel encontrados:")
    print(stdout)
    return stdout

def set_environment_variables():
    """Configura as variáveis de ambiente no Vercel"""
    
    # Variáveis de ambiente necessárias
    env_vars = {
        # Z-API Configuration
        "ZAPI_INSTANCE_ID": "VARIABLE_FROM_ENV",
        "ZAPI_TOKEN": "VARIABLE_FROM_ENV",
        "ZAPI_CLIENT_TOKEN": "VARIABLE_FROM_ENV",
        "ZAPI_BASE_URL": "https://api.z-api.io",
        
        # Supabase Configuration
        "SUPABASE_URL": "https://feqylqrphdpeeusdyeyw.supabase.co",
        "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc",
        
        # GestãoDS Configuration
        "GESTAODS_API_URL": "https://apidev.gestaods.com.br",
        "GESTAODS_TOKEN": "733a8e19a94b65d58390da380ac946b6d603a535",
        
        # App Configuration
        "ENVIRONMENT": "production",
        "DEBUG": "false",
        "CORS_ORIGINS": "*",
        "CORS_ALLOW_CREDENTIALS": "true",
        
        # Clinic Information
        "CLINIC_NAME": "Clínica Gabriela Nassif",
        "CLINIC_PHONE": "5531999999999",
        "REMINDER_HOUR": "18",
        "REMINDER_MINUTE": "0",
        
        # WebSocket Configuration
        "WEBSOCKET_ENABLED": "true",
        "WEBSOCKET_MAX_CONNECTIONS": "50"
    }
    
    print("🔧 Configurando variáveis de ambiente...")
    
    for var_name, var_value in env_vars.items():
        print(f"📝 Configurando {var_name}...")
        
        # Comando para configurar variável de ambiente
        command = f'vercel env add {var_name} production'
        
        # Simular entrada do usuário
        try:
            # Usar subprocess.Popen para interagir com o processo
            process = subprocess.Popen(
                command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Enviar o valor da variável
            stdout, stderr = process.communicate(input=var_value + '\n')
            
            if process.returncode == 0:
                print(f"✅ {var_name} configurado com sucesso")
            else:
                print(f"❌ Erro ao configurar {var_name}: {stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao configurar {var_name}: {str(e)}")

def main():
    """Função principal"""
    print("🚀 Configurador de Variáveis de Ambiente Vercel")
    print("=" * 50)
    
    # Verificar Vercel CLI
    if not check_vercel_cli():
        sys.exit(1)
    
    # Verificar se está logado
    success, stdout, stderr = run_command("vercel whoami")
    if not success:
        print("❌ Não está logado no Vercel")
        print("Execute: vercel login")
        sys.exit(1)
    
    print(f"✅ Logado como: {stdout.strip()}")
    
    # Mostrar projetos
    get_project_info()
    
    # Perguntar se quer continuar
    response = input("\n🤔 Deseja configurar as variáveis de ambiente? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operação cancelada")
        sys.exit(0)
    
    # Configurar variáveis
    set_environment_variables()
    
    print("\n✅ Configuração concluída!")
    print("🔄 Faça um novo deploy: vercel --prod")

if __name__ == "__main__":
    main() 