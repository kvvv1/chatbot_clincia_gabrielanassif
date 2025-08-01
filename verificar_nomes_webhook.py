#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE NOMES DOS WEBHOOKS
Verifica como estão configurados os nomes dos webhooks no Z-API
"""

import requests
import json

def verificar_nomes_webhook():
    """Verifica os nomes dos webhooks configurados"""
    print("🔍 VERIFICANDO NOMES DOS WEBHOOKS")
    print("=" * 50)
    
    # Credenciais Z-API
    instance_id = "3E4F7360B552F0C2DBCB9E6774402775"
    token = "0BDEFB65E4B5E5615697BCD6"
    client_token = "Fe13336af87e3482682a1f5f54a8fc83aS"
    
    # URL base
    base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    headers = {"Client-Token": client_token}
    
    print("📋 WEBHOOKS NECESSÁRIOS:")
    print("   Baseado na imagem que você mostrou:")
    print()
    print("   COLUNA ESQUERDA:")
    print("   - 'Ao enviar': https://chatbot-clincia.vercel.app/webhook/status")
    print("   - 'Ao desconectar': https://chatbot-clincia.vercel.app/webhook/connected")
    print("   - 'Ao receber': https://chatbot-clincia.vercel.app/webhook/message")
    print()
    print("   COLUNA DIREITA:")
    print("   - 'Presença do chat': (vazio)")
    print("   - 'Receber status da mensagem': https://chatbot-clincia.vercel.app/webhook/status")
    print("   - 'Ao conectar': https://chatbot-clincia.vercel.app/webhook/connected")
    print()
    print("   CONFIGURAÇÕES:")
    print("   - 'Notificar as enviadas por mim também': ATIVADO")
    print()
    
    print("🔍 PROBLEMA IDENTIFICADO:")
    print("   Na imagem, vejo que as URLs estão com 'chatbot-clinca' (sem 'i')")
    print("   Mas deveria ser 'chatbot-clincia' (com 'i')")
    print()
    print("   URLs INCORRETAS (na imagem):")
    print("   - https://chatbot-clinca.vercel.app/webhook/status")
    print("   - https://chatbot-clinca.vercel.app/webhook/connected")
    print("   - https://chatbot-clinca.vercel.app/webhook/message")
    print()
    print("   URLs CORRETAS (deveriam ser):")
    print("   - https://chatbot-clincia.vercel.app/webhook/status")
    print("   - https://chatbot-clincia.vercel.app/webhook/connected")
    print("   - https://chatbot-clincia.vercel.app/webhook/message")
    print()
    
    print("🔧 SOLUÇÃO:")
    print("   1. Acesse: https://app.z-api.io/")
    print("   2. Vá para sua instância: 3E4F7360B552F0C2DBCB9E6774402775")
    print("   3. Vá para a aba 'Webhook'")
    print("   4. Corrija as URLs:")
    print("      - 'Ao enviar': https://chatbot-clincia.vercel.app/webhook/status")
    print("      - 'Ao desconectar': https://chatbot-clincia.vercel.app/webhook/connected")
    print("      - 'Ao receber': https://chatbot-clincia.vercel.app/webhook/message")
    print("      - 'Receber status da mensagem': https://chatbot-clincia.vercel.app/webhook/status")
    print("      - 'Ao conectar': https://chatbot-clincia.vercel.app/webhook/connected")
    print("   5. Salve as configurações")
    print("   6. Teste novamente enviando 'oi'")
    print()
    
    print("🎯 RESUMO:")
    print("   O problema é que as URLs estão com 'chatbot-clinca' em vez de 'chatbot-clincia'")
    print("   Por isso o Z-API não consegue enviar eventos para o webhook correto")

if __name__ == "__main__":
    verificar_nomes_webhook() 