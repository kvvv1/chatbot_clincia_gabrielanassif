#!/usr/bin/env python3
"""
🔄 SCRIPT PARA RENOVAR CLIENT TOKEN Z-API
Ajuda a renovar o client token que está inválido
"""

import os
import requests
import json

def renovar_client_token():
    """Guia para renovar o client token"""
    print("🔄 RENOVAR CLIENT TOKEN Z-API")
    print("=" * 50)
    
    print("❌ PROBLEMA IDENTIFICADO:")
    print("   Client Token atual está inválido")
    print("   Erro: 'Client-Token not allowed'")
    print()
    
    print("🔧 SOLUÇÃO:")
    print("   1. Acesse: https://app.z-api.io/")
    print("   2. Faça login na sua conta")
    print("   3. Vá para 'Instâncias'")
    print("   4. Clique na sua instância")
    print("   5. Vá para a aba 'Segurança' ou 'Tokens'")
    print("   6. Procure por 'Renovar Client Token' ou 'Regenerate Client Token'")
    print("   7. Clique em renovar")
    print("   8. Copie o novo Client Token")
    print()
    
    print("📝 ATUALIZAR NO VERCEL:")
    print("   1. Acesse: https://vercel.com/dashboard")
    print("   2. Selecione seu projeto 'chatbot-clinica'")
    print("   3. Vá para Settings > Environment Variables")
    print("   4. Encontre ZAPI_CLIENT_TOKEN")
    print("   5. Clique em editar")
    print("   6. Cole o novo Client Token")
    print("   7. Salve")
    print()
    
    print("🧪 TESTAR APÓS RENOVAR:")
    print("   Execute: python verificar_whatsapp_status.py")
    print()
    
    print("⚠️ IMPORTANTE:")
    print("   - O Client Token é diferente do Token normal")
    print("   - Ambos podem expirar independentemente")
    print("   - Renove apenas o Client Token por enquanto")
    print()
    
    # Verificar configuração atual
    print("📋 CONFIGURAÇÃO ATUAL:")
    instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
    token = os.getenv("ZAPI_TOKEN", "")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN", "")
    
    print(f"   Instance ID: {instance_id[:10]}..." if instance_id else "❌ Não configurado")
    print(f"   Token: {'✅ Configurado' if token else '❌ Não configurado'}")
    print(f"   Client Token: {'❌ INVÁLIDO' if client_token else '❌ Não configurado'}")
    
    if client_token:
        print(f"   Client Token atual: {client_token}")
        print("   ⚠️ Este token está inválido e precisa ser renovado!")

if __name__ == "__main__":
    renovar_client_token() 