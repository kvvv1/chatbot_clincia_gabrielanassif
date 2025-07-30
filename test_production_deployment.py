#!/usr/bin/env python3
"""
Script para testar o deployment de produção após configuração das variáveis de ambiente
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
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Sucesso: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            except:
                print(f"✅ Sucesso: {response.text}")
                return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    # URL base do deployment de produção
    base_url = "https://chatbot-clinica.vercel.app"
    
    print("🚀 Testando deployment de produção...")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Lista de endpoints para testar
    endpoints = [
        ("/", "Root endpoint - Status básico"),
        ("/health", "Health check - Verificação de saúde"),
        ("/test", "Test endpoint - Endpoint de teste"),
        ("/debug", "Debug endpoint - Informações de debug"),
        ("/dashboard/status", "Dashboard status - Status do dashboard"),
        ("/dashboard/test", "Dashboard test - Teste do dashboard"),
        ("/dashboard/supabase/test", "Supabase test - Teste de conexão com Supabase"),
        ("/webhook/test", "Webhook test - Teste do webhook"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        success = test_endpoint(base_url, endpoint, description)
        results.append((endpoint, success))
        print("-" * 40)
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DE PRODUÇÃO")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {endpoint}")
    
    print(f"\nResultado: {passed}/{total} endpoints funcionando")
    
    if passed == total:
        print("🎉 PARABÉNS! Todos os endpoints estão funcionando!")
        print("✅ Seu chatbot está pronto para produção!")
        return 0
    elif passed >= total * 0.7:
        print("⚠️  A maioria dos endpoints está funcionando. Verifique os que falharam.")
        return 1
    else:
        print("❌ Muitos endpoints falharam. Verifique a configuração no Vercel.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 