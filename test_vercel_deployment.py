#!/usr/bin/env python3
"""
Script para testar o deployment no Vercel
"""

import requests
import json
import sys
import os

def test_endpoint(base_url, endpoint, description):
    """Testa um endpoint específico"""
    try:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testando {description}...")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    # URL base do deployment
    base_url = "https://chatbot-nassif.vercel.app"
    
    print("🚀 Testando deployment no Vercel...")
    print(f"Base URL: {base_url}")
    
    # Lista de endpoints para testar
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/test", "Test endpoint"),
        ("/debug", "Debug endpoint"),
        ("/dashboard/status", "Dashboard status"),
        ("/dashboard/test", "Dashboard test"),
        ("/dashboard/ws-test", "WebSocket test"),
        ("/dashboard/supabase/test", "Supabase test"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        success = test_endpoint(base_url, endpoint, description)
        results.append((endpoint, success))
        print("✅" if success else "❌")
    
    # Resumo dos resultados
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
        print("🎉 Todos os endpoints estão funcionando!")
        return 0
    else:
        print("⚠️  Alguns endpoints falharam. Verifique os logs do Vercel.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 