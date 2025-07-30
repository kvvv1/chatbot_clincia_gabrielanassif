#!/usr/bin/env python3
"""
Script para testar o deployment no Vercel
"""
import requests
import json
import time
import sys

def test_vercel_deployment():
    """Testa o deployment no Vercel"""
    
    # URL do deployment
    base_url = "https://chatbot-clincia.vercel.app"
    
    print("🧪 Testando deployment no Vercel...")
    print(f"URL: {base_url}")
    print("-" * 50)
    
    # Lista de endpoints para testar
    endpoints = [
        "/",
        "/test", 
        "/health",
        "/debug",
        "/dashboard/test",
        "/webhook/test"
    ]
    
    results = []
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"🔍 Testando: {endpoint}")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            duration = round((end_time - start_time) * 1000, 2)
            
            if response.status_code == 200:
                print(f"✅ Sucesso ({response.status_code}) - {duration}ms")
                try:
                    data = response.json()
                    print(f"   📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   📄 Resposta: {response.text[:200]}...")
            else:
                print(f"❌ Erro ({response.status_code}) - {duration}ms")
                print(f"   📄 Resposta: {response.text[:200]}...")
                
            results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "success": response.status_code == 200
            })
            
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout - {endpoint}")
            results.append({
                "endpoint": endpoint,
                "status_code": "TIMEOUT",
                "duration": 30000,
                "success": False
            })
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erro de conexão - {endpoint}")
            results.append({
                "endpoint": endpoint,
                "status_code": "CONNECTION_ERROR",
                "duration": 0,
                "success": False
            })
        except Exception as e:
            print(f"💥 Erro inesperado - {endpoint}: {str(e)}")
            results.append({
                "endpoint": endpoint,
                "status_code": "ERROR",
                "duration": 0,
                "success": False
            })
        
        print()
        time.sleep(1)  # Pausa entre requests
    
    # Resumo dos resultados
    print("=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Sucessos: {successful}/{total}")
    print(f"❌ Falhas: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("⚠️  Alguns testes falharam")
        
        # Mostrar falhas
        print("\n❌ Endpoints com falha:")
        for result in results:
            if not result["success"]:
                print(f"   - {result['endpoint']} ({result['status_code']})")
        
        return False

if __name__ == "__main__":
    success = test_vercel_deployment()
    sys.exit(0 if success else 1) 