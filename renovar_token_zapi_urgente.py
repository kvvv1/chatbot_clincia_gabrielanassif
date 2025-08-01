#!/usr/bin/env python3
"""
Script URGENTE para renovar token do Z-API
O problema é que o Client-Token está inválido
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Configurações atuais (que estão falhando)
CURRENT_CONFIG = {
    "instance_id": "3E4F7360B552F0C2DBCB9E6774402775",
    "token": "0BDEFB65E4B5E5615697BCD6",
    "client_token": "Fb79b25350a784c8e83d4a25213955ab5S",
    "base_url": "https://api.z-api.io"
}

async def test_current_token():
    """Testa o token atual"""
    print("🔍 Testando token atual...")
    
    url = f"{CURRENT_CONFIG['base_url']}/instances/{CURRENT_CONFIG['instance_id']}/token/{CURRENT_CONFIG['token']}/send-text"
    
    headers = {
        "Client-Token": CURRENT_CONFIG['client_token'],
        "Content-Type": "application/json"
    }
    
    data = {
        "phone": "5511999999999",
        "message": "Teste de token"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 403:
                print("❌ Token inválido - precisa renovar!")
                return False
            elif response.status_code == 200:
                print("✅ Token válido!")
                return True
            else:
                print(f"⚠️ Status inesperado: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

async def get_new_client_token():
    """Obtém novo client token"""
    print("🔄 Obtendo novo client token...")
    
    url = f"{CURRENT_CONFIG['base_url']}/instances/{CURRENT_CONFIG['instance_id']}/token/{CURRENT_CONFIG['token']}/client-token"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                new_client_token = data.get('client-token')
                if new_client_token:
                    print(f"✅ Novo client token obtido: {new_client_token}")
                    return new_client_token
                else:
                    print("❌ Client token não encontrado na resposta")
                    return None
            else:
                print(f"❌ Erro ao obter client token: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Erro ao obter client token: {str(e)}")
        return None

async def test_new_token(new_client_token):
    """Testa o novo token"""
    print("🧪 Testando novo token...")
    
    url = f"{CURRENT_CONFIG['base_url']}/instances/{CURRENT_CONFIG['instance_id']}/token/{CURRENT_CONFIG['token']}/send-text"
    
    headers = {
        "Client-Token": new_client_token,
        "Content-Type": "application/json"
    }
    
    data = {
        "phone": "5511999999999",
        "message": "Teste com novo token"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Novo token funcionando!")
                return True
            else:
                print(f"❌ Novo token ainda com problema: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste do novo token: {str(e)}")
        return False

def update_config_files(new_client_token):
    """Atualiza os arquivos de configuração"""
    print("📝 Atualizando arquivos de configuração...")
    
    # Atualizar vercel.env.production
    try:
        with open('vercel.env.production', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            f"ZAPI_CLIENT_TOKEN={CURRENT_CONFIG['client_token']}",
            f"ZAPI_CLIENT_TOKEN={new_client_token}"
        )
        
        with open('vercel.env.production', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ vercel.env.production atualizado")
    except Exception as e:
        print(f"❌ Erro ao atualizar vercel.env.production: {str(e)}")
    
    # Atualizar zapi_vercel_env.json
    try:
        with open('zapi_vercel_env.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['ZAPI_CLIENT_TOKEN'] = new_client_token
        
        with open('zapi_vercel_env.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print("✅ zapi_vercel_env.json atualizado")
    except Exception as e:
        print(f"❌ Erro ao atualizar zapi_vercel_env.json: {str(e)}")
    
    # Criar arquivo com novo token
    try:
        with open('novo_token_zapi.txt', 'w', encoding='utf-8') as f:
            f.write(f"# Token renovado em {datetime.now()}\n")
            f.write(f"ZAPI_INSTANCE_ID={CURRENT_CONFIG['instance_id']}\n")
            f.write(f"ZAPI_TOKEN={CURRENT_CONFIG['token']}\n")
            f.write(f"ZAPI_CLIENT_TOKEN={new_client_token}\n")
            f.write(f"ZAPI_BASE_URL={CURRENT_CONFIG['base_url']}\n")
        
        print("✅ novo_token_zapi.txt criado")
    except Exception as e:
        print(f"❌ Erro ao criar novo_token_zapi.txt: {str(e)}")

async def main():
    """Função principal"""
    print("🚨 RENOVAÇÃO URGENTE DE TOKEN Z-API")
    print("=" * 50)
    
    # 1. Testar token atual
    current_works = await test_current_token()
    
    if current_works:
        print("✅ Token atual está funcionando!")
        return
    
    print("\n" + "=" * 50)
    
    # 2. Obter novo client token
    new_client_token = await get_new_client_token()
    
    if not new_client_token:
        print("❌ Não foi possível obter novo client token")
        return
    
    print("\n" + "=" * 50)
    
    # 3. Testar novo token
    new_works = await test_new_token(new_client_token)
    
    if not new_works:
        print("❌ Novo token também não funcionou")
        return
    
    print("\n" + "=" * 50)
    
    # 4. Atualizar arquivos
    update_config_files(new_client_token)
    
    print("\n" + "=" * 50)
    print("🎉 RENOVAÇÃO CONCLUÍDA!")
    print(f"📋 Novo Client Token: {new_client_token}")
    print("📝 Arquivos atualizados:")
    print("   - vercel.env.production")
    print("   - zapi_vercel_env.json")
    print("   - novo_token_zapi.txt")
    print("\n⚠️ IMPORTANTE: Atualize as variáveis no Vercel!")

if __name__ == "__main__":
    asyncio.run(main()) 