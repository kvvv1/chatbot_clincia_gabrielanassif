#!/usr/bin/env python3
"""
Script para testar a implantação no Vercel
"""
import requests
import json
import sys
import os

def test_vercel_deployment():
    """Testa a implantação no Vercel"""
    
    # URL base do Vercel (substitua pela sua URL)
    base_url = "https://chatbot-nassif.vercel.app"
    
    # Endpoints para testar
    endpoints = [
        "/",
        "/test", 
        "/health",
        "/dashboard/test",
        "/dashboard/conversations",
        "/dashboard/analytics/summary"
    ]
    
    print("🧪 Testando implantação no Vercel...")
    print(f"URL base: {base_url}")
    print("-" * 50)
    
    results = []
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testando: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK (Status: {response.status_code})")
                try:
                    data = response.json()
                    print(f"   Resposta: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Resposta: {response.text[:200]}...")
            else:
                print(f"❌ {endpoint} - ERRO (Status: {response.status_code})")
                print(f"   Erro: {response.text}")
            
            results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - ERRO DE CONEXÃO")
            print(f"   Erro: {str(e)}")
            results.append({
                "endpoint": endpoint,
                "status_code": None,
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Resumo
    print("📊 RESUMO DOS TESTES")
    print("-" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Sucessos: {successful}/{total}")
    print(f"❌ Falhas: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        return False

def test_environment_variables():
    """Testa se as variáveis de ambiente estão configuradas"""
    print("\n🔧 VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("-" * 50)
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    optional_vars = [
        "ZAPI_INSTANCE_ID",
        "ZAPI_TOKEN",
        "GESTAODS_TOKEN"
    ]
    
    print("Variáveis obrigatórias:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configurada")
        else:
            print(f"❌ {var}: NÃO CONFIGURADA")
    
    print("\nVariáveis opcionais:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configurada")
        else:
            print(f"⚠️  {var}: Não configurada (opcional)")

if __name__ == "__main__":
    print("🚀 TESTE DE IMPLANTAÇÃO VERCEL")
    print("=" * 50)
    
    # Testar variáveis de ambiente
    test_environment_variables()
    
    # Testar endpoints
    success = test_vercel_deployment()
    
    if success:
        print("\n🎉 Implantação funcionando corretamente!")
        sys.exit(0)
    else:
        print("\n❌ Implantação com problemas!")
        sys.exit(1) 