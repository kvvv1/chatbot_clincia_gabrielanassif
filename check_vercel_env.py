#!/usr/bin/env python3
"""
Script para verificar se as variáveis de ambiente estão configuradas no Vercel
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

def check_vercel_env():
    """Verifica as variáveis de ambiente no Vercel"""
    
    # Variáveis obrigatórias
    required_vars = [
        "ZAPI_INSTANCE_ID",
        "ZAPI_TOKEN", 
        "ZAPI_CLIENT_TOKEN",
        "CLINIC_NAME",
        "CLINIC_PHONE",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "GESTAODS_API_URL",
        "GESTAODS_TOKEN",
        "ENVIRONMENT",
        "DEBUG"
    ]
    
    print("🔍 Verificando variáveis de ambiente no Vercel...")
    print("=" * 50)
    
    # Verificar se está logado
    success, stdout, stderr = run_command("vercel whoami")
    if not success:
        print("❌ Não está logado no Vercel")
        print("Execute: vercel login")
        return False
    
    print(f"✅ Logado como: {stdout.strip()}")
    
    # Listar variáveis de ambiente
    success, stdout, stderr = run_command("vercel env ls")
    if not success:
        print("❌ Erro ao listar variáveis de ambiente")
        print(stderr)
        return False
    
    print("\n📋 Variáveis configuradas:")
    print(stdout)
    
    # Verificar variáveis obrigatórias
    print("\n🔍 Verificando variáveis obrigatórias:")
    missing_vars = []
    
    for var in required_vars:
        if var in stdout:
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - FALTANDO")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ {len(missing_vars)} variáveis estão faltando:")
        for var in missing_vars:
            print(f"   - {var}")
        
        print("\n📝 Para configurar, execute:")
        print("   python vercel_setup_env.py")
        return False
    else:
        print("\n✅ Todas as variáveis obrigatórias estão configuradas!")
        return True

def main():
    """Função principal"""
    print("🚀 Verificador de Variáveis de Ambiente Vercel")
    print("=" * 50)
    
    # Verificar Vercel CLI
    success, stdout, stderr = run_command("vercel --version")
    if not success:
        print("❌ Vercel CLI não encontrado!")
        print("Instale com: npm i -g vercel")
        sys.exit(1)
    
    print(f"✅ Vercel CLI: {stdout.strip()}")
    
    # Verificar variáveis
    if check_vercel_env():
        print("\n🎉 Tudo configurado! Faça um deploy:")
        print("   vercel --prod")
    else:
        print("\n⚠️  Configure as variáveis antes de fazer deploy")

if __name__ == "__main__":
    main() 