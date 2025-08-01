#!/usr/bin/env python3
"""
Script para ajudar a obter o Client-Token do Z-API
"""

import os
from dotenv import load_dotenv

def obter_client_token():
    """Ajuda a obter o Client-Token do Z-API"""
    print("🔑 Como obter o Client-Token do Z-API:")
    print("\n📋 Passos:")
    print("1. Acesse o painel do Z-API: https://app.z-api.io/")
    print("2. Faça login na sua conta")
    print("3. Vá para 'Instâncias' no menu lateral")
    print("4. Clique na sua instância: VARIABLE_FROM_ENV")
    print("5. Na aba 'Configurações' ou 'API', procure por 'Client-Token'")
    print("6. Copie o valor do Client-Token")
    print("\n💡 O Client-Token geralmente começa com algo como:")
    print("   - $2b$10$...")
    print("   - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print("   - Ou uma string alfanumérica longa")
    
    print("\n🔧 Para configurar:")
    print("1. Abra o arquivo .env")
    print("2. Encontre a linha: ZAPI_CLIENT_TOKEN=seu_client_token_aqui")
    print("3. Substitua 'seu_client_token_aqui' pelo token real")
    print("4. Salve o arquivo")
    print("5. Reinicie o servidor")
    
    print("\n⚠️  IMPORTANTE:")
    print("- O Client-Token é diferente do Token da instância")
    print("- É uma credencial de API separada")
    print("- Mantenha-o seguro e não compartilhe")
    
    # Verificar se já está configurado
    load_dotenv()
    current_token = os.getenv('ZAPI_CLIENT_TOKEN', '')
    
    if current_token and current_token != 'seu_client_token_aqui':
        print(f"\n✅ Client-Token já configurado: {current_token[:20]}...")
    else:
        print("\n❌ Client-Token ainda não configurado!")
        print("   Configure-o no arquivo .env")

if __name__ == "__main__":
    obter_client_token() 