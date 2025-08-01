#!/usr/bin/env python3
"""
Script para atualizar o Client Token do Z-API
"""

import os
from dotenv import load_dotenv

def atualizar_client_token():
    """Atualiza o Client Token do Z-API"""
    print("🔑 Atualizando Client Token do Z-API...")
    
    # Client Token fornecido pelo usuário
    client_token = os.getenv("ZAPI_TOKEN", "")
    
    # Carregar .env atual
    load_dotenv()
    
    # Ler conteúdo atual do .env
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # Atualizar ou adicionar ZAPI_CLIENT_TOKEN
    lines = content.split('\n')
    updated_lines = []
    token_updated = False
    
    for line in lines:
        if line.startswith('ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")ZAPI_CLIENT_TOKEN={client_token}')
            token_updated = True
        else:
            updated_lines.append(line)
    
    # Se não encontrou a linha, adicionar
    if not token_updated:
        updated_lines.append(f'ZAPI_CLIENT_TOKEN={client_token}')
    
    # Salvar arquivo atualizado
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ Client Token atualizado: {client_token}")
    print(f"✅ Arquivo .env salvo em: {os.path.abspath(env_path)}")
    
    # Verificar se foi salvo corretamente
    load_dotenv(override=True)
    saved_token = os.getenv('ZAPI_CLIENT_TOKEN')
    
    if saved_token == client_token:
        print("✅ Verificação: Token salvo corretamente!")
    else:
        print(f"❌ Erro: Token não foi salvo corretamente")
        print(f"   Esperado: {client_token}")
        print(f"   Encontrado: {saved_token}")

if __name__ == "__main__":
    atualizar_client_token() 