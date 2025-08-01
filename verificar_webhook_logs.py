#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE LOGS DO WEBHOOK
Verifica se o webhook está recebendo e processando mensagens
"""

import requests
import json
import time

def verificar_webhook_logs():
    """Verifica os logs do webhook"""
    print("🔍 VERIFICANDO LOGS DO WEBHOOK")
    print("=" * 50)
    
    # URLs do webhook
    webhook_urls = [
        "https://chatbot-clincia.vercel.app/webhook",
        "https://chatbot-clincia.vercel.app/webhook/message",
        "https://chatbot-clincia.vercel.app/webhook/status",
        "https://chatbot-clincia.vercel.app/webhook/connected",
        "https://chatbot-clincia.vercel.app/webhook/health"
    ]
    
    print("📋 TESTANDO ENDPOINTS DO WEBHOOK:")
    
    for url in webhook_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   {url}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Resposta: {json.dumps(data, indent=2)}")
                except:
                    print(f"      ✅ Resposta: {response.text[:100]}...")
            else:
                print(f"      ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   {url}: ❌ Erro - {str(e)}")
    
    print(f"\n🔧 DIAGNÓSTICO DO PROBLEMA:")
    print(f"   ✅ Mensagem enviada com sucesso")
    print(f"   ❌ Webhook não processa mensagens recebidas")
    print(f"   🔍 Possíveis causas:")
    print(f"      1. Webhook não está recebendo eventos do Z-API")
    print(f"      2. Configuração de webhook incorreta")
    print(f"      3. Problema no código do webhook")
    print(f"      4. Eventos não ativados no Z-API")
    
    print(f"\n🔍 VERIFICAÇÕES NECESSÁRIAS:")
    print(f"   1. Verificar se o webhook está configurado corretamente no Z-API")
    print(f"   2. Verificar se todos os eventos estão ativados")
    print(f"   3. Verificar logs no painel do Vercel")
    print(f"   4. Testar com uma mensagem simples")
    
    print(f"\n📊 PRÓXIMOS PASSOS:")
    print(f"   1. Acesse: https://vercel.com/dashboard")
    print(f"   2. Selecione o projeto 'chatbot-clinica'")
    print(f"   3. Vá para 'Functions' > 'webhook'")
    print(f"   4. Verifique se há logs de execução")
    print(f"   5. Se não há logs, o webhook não está sendo chamado")
    
    print(f"\n🔧 SOLUÇÃO RÁPIDA:")
    print(f"   1. Verifique se o webhook está configurado no Z-API:")
    print(f"      - URL: https://chatbot-clincia.vercel.app/webhook")
    print(f"      - Evento: 'Ao receber'")
    print(f"   2. Ative 'Notificar as enviadas por mim também'")
    print(f"   3. Teste novamente enviando 'oi'")

if __name__ == "__main__":
    verificar_webhook_logs() 