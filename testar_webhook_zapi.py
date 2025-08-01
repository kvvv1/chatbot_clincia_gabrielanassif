#!/usr/bin/env python3
"""
🧪 TESTE DE WEBHOOK Z-API
Testa se o Z-API está enviando eventos para o webhook
"""

import requests
import json
import time

def testar_webhook_zapi():
    """Testa se o Z-API está enviando eventos"""
    print("🧪 TESTE DE WEBHOOK Z-API")
    print("=" * 50)
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "0BDEFB65E4B5E5615697BCD6"
    client_token = "Fe13336af87e3482682a1f5f54a8fc83aS"
    
    # URL base
    base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    headers = {"Client-Token": client_token}
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO WEBHOOK NO Z-API...")
    
    # 1. Verificar se o webhook está configurado
    webhook_url = "https://chatbot-clincia.vercel.app/webhook"
    
    try:
        # Tentar obter configuração do webhook
        response = requests.get(f"{base_url}/webhook", headers=headers, timeout=10)
        print(f"   Status webhook: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Configuração: {json.dumps(data, indent=2)}")
        else:
            print(f"   Erro: {response.text}")
            
    except Exception as e:
        print(f"   Erro ao verificar webhook: {str(e)}")
    
    print(f"\n🔧 PROBLEMA IDENTIFICADO:")
    print(f"   O Z-API não está enviando eventos para o webhook")
    print(f"   Isso pode ser causado por:")
    print(f"   1. Webhook não configurado corretamente no painel Z-API")
    print(f"   2. URL do webhook incorreta")
    print(f"   3. Eventos não ativados")
    print(f"   4. Problema de conectividade")
    
    print(f"\n🔧 SOLUÇÃO:")
    print(f"   1. Acesse: https://app.z-api.io/")
    print(f"   2. Vá para sua instância: {instance_id}")
    print(f"   3. Vá para a aba 'Webhook'")
    print(f"   4. Verifique se está configurado:")
    print(f"      - 'Ao receber': {webhook_url}")
    print(f"      - 'Notificar as enviadas por mim também': ATIVADO")
    print(f"   5. Salve as configurações")
    print(f"   6. Teste novamente enviando 'oi'")
    
    print(f"\n📊 TESTE ALTERNATIVO:")
    print(f"   Se o problema persistir, vamos testar com uma URL de webhook simples")
    print(f"   para verificar se o Z-API está funcionando")

if __name__ == "__main__":
    testar_webhook_zapi() 