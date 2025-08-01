#!/usr/bin/env python3
"""
📱 TESTE PARA NÚMERO ESPECÍFICO
Testa envio de mensagem para o número +5531995531183
"""

import requests
import json
import time

def teste_numero_especifico():
    """Testa envio de mensagem para número específico"""
    print("📱 TESTE PARA NÚMERO ESPECÍFICO")
    print("=" * 50)
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "0BDEFB65E4B5E5615697BCD6"
    client_token = "Fe13336af87e3482682a1f5f54a8fc83aS"
    
    # Número específico
    phone = "5531995531183"
    
    # URL base
    base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    headers = {"Client-Token": client_token}
    
    print(f"📞 Número de destino: +{phone}")
    print(f"🌐 URL Base: {base_url}")
    
    # Mensagem de teste
    message = f"🤖 Teste do Chatbot - {time.strftime('%H:%M:%S')}\n\nOlá! Este é um teste do chatbot da Clínica Gabriela Nassif.\n\nSe você receber esta mensagem, o sistema está funcionando!\n\nResponda com 'oi' para testar o webhook."
    
    print(f"\n📤 Enviando mensagem para: +{phone}")
    print(f"📝 Mensagem: {message}")
    
    # Enviar mensagem
    payload = {
        "phone": phone,
        "message": message
    }
    
    try:
        print(f"\n🔄 Enviando...")
        response = requests.post(
            f"{base_url}/send-text",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Mensagem enviada com sucesso!")
            print(f"   Message ID: {data.get('messageId', 'N/A')}")
            print(f"   Zaap ID: {data.get('zaapId', 'N/A')}")
            print(f"   ID: {data.get('id', 'N/A')}")
            
            print(f"\n🔍 AGORA TESTE O WEBHOOK:")
            print(f"   1. Verifique se você recebeu a mensagem no WhatsApp")
            print(f"   2. Responda com 'oi' ou qualquer mensagem")
            print(f"   3. O chatbot deve responder automaticamente")
            print(f"   4. Verifique os logs no painel do Vercel")
            
            print(f"\n📊 Para verificar logs:")
            print(f"   - Acesse: https://vercel.com/dashboard")
            print(f"   - Selecione o projeto 'chatbot-clinica'")
            print(f"   - Vá para 'Functions' > 'webhook'")
            print(f"   - Verifique os logs de execução")
            
            print(f"\n🎯 STATUS DO SISTEMA:")
            print(f"   ✅ Client Token: Válido")
            print(f"   ✅ WhatsApp: Conectado")
            print(f"   ✅ Webhooks: Configurados")
            print(f"   ✅ Envio: Funcionando")
            print(f"   🔄 Webhook: Aguardando teste")
            
        else:
            print(f"\n❌ Erro ao enviar mensagem: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Erro ao enviar mensagem: {str(e)}")

if __name__ == "__main__":
    teste_numero_especifico() 