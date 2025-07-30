#!/usr/bin/env python3
"""
Script para deploy e teste no Vercel
"""

import subprocess
import requests
import time
import json
import sys

def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔧 {description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Comando executado com sucesso")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ Erro no comando: {result.stderr}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def test_endpoint(url, description):
    """Testa um endpoint específico"""
    print(f"\n🔍 Testando {description}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ {description} - OK")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            except:
                print(f"✅ {description} - OK (não-JSON)")
                print(f"Response: {response.text}")
                return True
        else:
            print(f"❌ {description} - ERRO (Status: {response.status_code})")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    print("🚀 Script de Deploy e Teste - Vercel")
    print("=" * 50)
    
    # Verificar se o Vercel CLI está instalado
    if not run_command("vercel --version", "Verificando Vercel CLI"):
        print("❌ Vercel CLI não encontrado. Instale com: npm i -g vercel")
        return 1
    
    # Verificar se estamos logados no Vercel
    if not run_command("vercel whoami", "Verificando login no Vercel"):
        print("❌ Não logado no Vercel. Execute: vercel login")
        return 1
    
    # Fazer deploy
    print("\n📦 Fazendo deploy...")
    deploy_success = run_command("vercel --prod", "Deploy para produção")
    
    if not deploy_success:
        print("❌ Deploy falhou!")
        return 1
    
    # Aguardar um pouco para o deploy terminar
    print("\n⏳ Aguardando deploy terminar...")
    time.sleep(10)
    
    # Testar endpoints
    print("\n🧪 Testando endpoints...")
    
    base_url = "https://chatbot-nassif.vercel.app"
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/test", "Test endpoint"),
        ("/debug", "Debug endpoint"),
        ("/dashboard/status", "Dashboard status"),
        ("/dashboard/test", "Dashboard test"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        success = test_endpoint(f"{base_url}{endpoint}", description)
        results.append((endpoint, success))
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {endpoint}")
    
    print(f"\nResultado: {passed}/{total} endpoints funcionando")
    
    if passed == total:
        print("🎉 Deploy e testes bem-sucedidos!")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs do Vercel.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 