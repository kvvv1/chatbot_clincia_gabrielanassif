#!/usr/bin/env python3
"""
Script completo para testar todo o sistema do chatbot
"""

import requests
import json
import time
from typing import Dict, Any

def test_vercel_deployment():
    """Testa se o deploy no Vercel está funcionando"""
    print("🌐 Testando Deploy no Vercel...")
    print("-" * 40)
    
    try:
        response = requests.get("https://chatbot-clincia.vercel.app/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Deploy funcionando!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Ambiente: {data.get('environment')}")
            print(f"📦 Versão: {data.get('version')}")
            return True
        else:
            print(f"❌ Erro no deploy: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar deploy: {str(e)}")
        return False

def test_webhook_endpoint():
    """Testa se o endpoint de webhook está funcionando"""
    print("\n🔗 Testando Endpoint de Webhook...")
    print("-" * 40)
    
    try:
        response = requests.get("https://chatbot-clincia.vercel.app/webhook", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook endpoint funcionando!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Serviço: {data.get('service')}")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {str(e)}")
        return False

def test_zapi_connection():
    """Testa conexão com Z-API"""
    print("\n📱 Testando Conexão Z-API...")
    print("-" * 40)
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "17829E98BB59E9ADD55BBBA9"
    client_token = "17829E98BB59E9ADD55BBBA9"
    
    try:
        # Testar status da instância
        url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/status"
        headers = {"Client-Token": client_token}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexão Z-API funcionando!")
            print(f"📊 Status da instância: {data.get('status')}")
            print(f"🔧 Conectado: {data.get('connected', False)}")
            return True
        else:
            print(f"❌ Erro na Z-API: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Z-API: {str(e)}")
        return False

def test_gestaods_api():
    """Testa conexão com API GestãoDS"""
    print("\n🏥 Testando API GestãoDS...")
    print("-" * 40)
    
    try:
        url = "https://apidev.gestaods.com.br/api/pacientes/"
        headers = {
            "Authorization": "Bearer 733a8e19a94b65d58390da380ac946b6d603a535",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API GestãoDS funcionando!")
            print(f"📊 Status: {response.status_code}")
            return True
        elif response.status_code == 401:
            print("⚠️ Token GestãoDS pode estar inválido")
            print(f"📄 Resposta: {response.text}")
            return False
        else:
            print(f"❌ Erro na API GestãoDS: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar GestãoDS: {str(e)}")
        return False

def test_webhook_message():
    """Testa envio de mensagem de teste via webhook"""
    print("\n📨 Testando Envio de Mensagem...")
    print("-" * 40)
    
    # Simular mensagem recebida do WhatsApp
    test_message = {
        "event": "message",
        "data": {
            "id": "test_message_123",
            "type": "text",
            "phone": "553198600366",
            "message": "oi",
            "timestamp": int(time.time())
        }
    }
    
    try:
        response = requests.post(
            "https://chatbot-clincia.vercel.app/webhook",
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mensagem processada com sucesso!")
            print(f"📊 Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Erro ao processar mensagem: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar mensagem: {str(e)}")
        return False

def generate_test_report(results: Dict[str, bool]):
    """Gera relatório de teste"""
    print("\n📋 RELATÓRIO DE TESTE")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Total de testes: {total_tests}")
    print(f"✅ Passou: {passed_tests}")
    print(f"❌ Falhou: {failed_tests}")
    print(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    print("🔍 DETALHES:")
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print()
    
    if failed_tests == 0:
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("📱 O chatbot está pronto para uso!")
    else:
        print("⚠️ ALGUNS PROBLEMAS DETECTADOS")
        print("🔧 Verifique os itens com ❌ acima")
        
        if not results.get("vercel_deployment", False):
            print("\n🚨 PRIORIDADE ALTA:")
            print("- Configure as variáveis de ambiente no Vercel")
            print("- Faça redeploy da aplicação")
            
        if not results.get("zapi_connection", False):
            print("\n🚨 PRIORIDADE ALTA:")
            print("- Verifique as credenciais Z-API")
            print("- Confirme se o WhatsApp está conectado")

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DO SISTEMA CHATBOT")
    print("=" * 60)
    print()
    
    # Executar todos os testes
    results = {
        "vercel_deployment": test_vercel_deployment(),
        "webhook_endpoint": test_webhook_endpoint(),
        "zapi_connection": test_zapi_connection(),
        "gestaods_api": test_gestaods_api(),
        "webhook_message": test_webhook_message()
    }
    
    # Gerar relatório
    generate_test_report(results)
    
    # Salvar resultados em arquivo
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.time(),
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(results.values()),
                "failed": len(results) - sum(results.values())
            }
        }, f, indent=2, ensure_ascii=False)
    
    print("💾 Resultados salvos em: test_results.json")

if __name__ == "__main__":
    main() 