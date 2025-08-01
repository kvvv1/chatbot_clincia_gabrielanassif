#!/usr/bin/env python3
"""
Script para atualizar o token correto do Z-API
"""

import json
import os
from datetime import datetime

# Token correto fornecido pelo usuário
NEW_CLIENT_TOKEN = "Fe13336af87e3482682a1f5f54a8fc83aS"
OLD_CLIENT_TOKEN = "Fb79b25350a784c8e83d4a25213955ab5S"

def update_vercel_env_production():
    """Atualiza vercel.env.production"""
    print("📝 Atualizando vercel.env.production...")
    
    try:
        with open('vercel.env.production', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            f"ZAPI_CLIENT_TOKEN={OLD_CLIENT_TOKEN}",
            f"ZAPI_CLIENT_TOKEN={NEW_CLIENT_TOKEN}"
        )
        
        with open('vercel.env.production', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ vercel.env.production atualizado")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar vercel.env.production: {str(e)}")
        return False

def update_zapi_vercel_env_json():
    """Atualiza zapi_vercel_env.json"""
    print("📝 Atualizando zapi_vercel_env.json...")
    
    try:
        with open('zapi_vercel_env.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['ZAPI_CLIENT_TOKEN'] = NEW_CLIENT_TOKEN
        
        with open('zapi_vercel_env.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print("✅ zapi_vercel_env.json atualizado")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar zapi_vercel_env.json: {str(e)}")
        return False

def update_vercel_env_example():
    """Atualiza vercel.env.example"""
    print("📝 Atualizando vercel.env.example...")
    
    try:
        with open('vercel.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            f"ZAPI_CLIENT_TOKEN={OLD_CLIENT_TOKEN}",
            f"ZAPI_CLIENT_TOKEN={NEW_CLIENT_TOKEN}"
        )
        
        with open('vercel.env.example', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ vercel.env.example atualizado")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar vercel.env.example: {str(e)}")
        return False

def create_token_file():
    """Cria arquivo com o token atualizado"""
    print("📝 Criando arquivo com token atualizado...")
    
    try:
        with open('token_atualizado.txt', 'w', encoding='utf-8') as f:
            f.write(f"# Token atualizado em {datetime.now()}\n")
            f.write(f"ZAPI_INSTANCE_ID=3E4F7360B552F0C2DBCB9E6774402775\n")
            f.write(f"ZAPI_TOKEN=0BDEFB65E4B5E5615697BCD6\n")
            f.write(f"ZAPI_CLIENT_TOKEN={NEW_CLIENT_TOKEN}\n")
            f.write(f"ZAPI_BASE_URL=https://api.z-api.io\n")
        
        print("✅ token_atualizado.txt criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar token_atualizado.txt: {str(e)}")
        return False

def test_token():
    """Testa o novo token"""
    print("🧪 Testando novo token...")
    
    import asyncio
    import httpx
    
    async def test():
        url = "https://api.z-api.io/instances/3E4F7360B552F0C2DBCB9E6774402775/token/0BDEFB65E4B5E5615697BCD6/send-text"
        
        headers = {
            "Client-Token": NEW_CLIENT_TOKEN,
            "Content-Type": "application/json"
        }
        
        data = {
            "phone": "5511999999999",
            "message": "Teste com token atualizado"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=data)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Token funcionando!")
                    return True
                else:
                    print(f"❌ Token ainda com problema: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
            return False
    
    return asyncio.run(test())

def main():
    """Função principal"""
    print("🔄 ATUALIZANDO TOKEN Z-API")
    print("=" * 50)
    print(f"Token antigo: {OLD_CLIENT_TOKEN}")
    print(f"Token novo: {NEW_CLIENT_TOKEN}")
    print()
    
    # Atualizar arquivos
    success_count = 0
    
    if update_vercel_env_production():
        success_count += 1
    
    if update_zapi_vercel_env_json():
        success_count += 1
    
    if update_vercel_env_example():
        success_count += 1
    
    if create_token_file():
        success_count += 1
    
    print("\n" + "=" * 50)
    
    # Testar token
    if test_token():
        success_count += 1
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DA ATUALIZAÇÃO")
    print(f"✅ Arquivos atualizados: {success_count}/5")
    
    if success_count >= 4:
        print("🎉 ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n📋 Próximos passos:")
        print("1. Faça commit das alterações")
        print("2. Faça deploy no Vercel")
        print("3. Atualize as variáveis de ambiente no Vercel se necessário")
        print("4. Teste o chatbot enviando 'oi'")
    else:
        print("⚠️ Alguns arquivos não foram atualizados")
        print("Verifique os erros acima")

if __name__ == "__main__":
    main() 