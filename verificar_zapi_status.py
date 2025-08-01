#!/usr/bin/env python3
"""
Script para verificar o status da Z-API e identificar problemas
"""

import httpx
import asyncio
import json

async def verificar_zapi_status():
    print("🔍 VERIFICANDO STATUS Z-API")
    print("=" * 50)
    
    # Credenciais Z-API
    instance_id = os.getenv("ZAPI_INSTANCE_ID", "")
    token = os.getenv("ZAPI_TOKEN", "")
    client_token = os.getenv("ZAPI_TOKEN", "")
    
    print(f"📱 Instance ID: {instance_id}")
    print(f"🔑 Token: {token[:10]}...")
    print(f"🔑 Client Token: {client_token[:10]}...")
    
    # Testar diferentes combinações de credenciais
    test_configs = [
        {
            "name": "Configuração Principal",
            "instance": instance_id,
            "token": token,
            "url": f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        },
        {
            "name": "Com Client Token",
            "instance": instance_id,
            "token": client_token,
            "url": f"https://api.z-api.io/instances/{instance_id}/token/{client_token}"
        }
    ]
    
    for config in test_configs:
        print(f"\n🧪 Testando: {config['name']}")
        print(f"   URL: {config['url']}")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Teste 1: Status da instância
                response = await client.get(f"{config['url']}/status")
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Instância ativa!")
                    print(f"   📋 Dados: {status_data}")
                    
                    # Verificar se WhatsApp está conectado
                    if 'connected' in str(status_data).lower():
                        print(f"   📱 WhatsApp conectado!")
                    else:
                        print(f"   ⚠️ WhatsApp pode não estar conectado")
                        
                elif response.status_code == 400:
                    print(f"   ❌ Instance not found")
                    print(f"   📝 Resposta: {response.text}")
                else:
                    print(f"   ❌ Erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                
                # Teste 2: Informações da instância
                try:
                    response = await client.get(f"{config['url']}/info")
                    print(f"   📋 Info: {response.status_code}")
                    if response.status_code == 200:
                        info_data = response.json()
                        print(f"   📊 Informações: {info_data}")
                except:
                    print(f"   ⚠️ Info endpoint não disponível")
                    
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print("\n🔧 DIAGNÓSTICO:")
    print("=" * 50)
    
    print("Possíveis problemas:")
    print("1. ❌ Instance ID incorreto")
    print("2. ❌ Token incorreto")
    print("3. ❌ Instância desativada")
    print("4. ❌ Credenciais expiradas")
    
    print("\n💡 SOLUÇÕES:")
    print("1. Verifique as credenciais no painel Z-API")
    print("2. Confirme se a instância está ativa")
    print("3. Gere novos tokens se necessário")
    print("4. Verifique se o WhatsApp está conectado")
    
    print("\n🔗 Links úteis:")
    print("- Painel Z-API: https://app.z-api.io/")
    print("- Documentação: https://z-api.io/docs")
    print("- Suporte: https://z-api.io/support")

async def testar_credenciais_alternativas():
    """Testa credenciais alternativas que podem estar corretas"""
    print("\n🧪 TESTANDO CREDENCIAIS ALTERNATIVAS")
    print("=" * 50)
    
    # Possíveis variações das credenciais
    possible_instances = [
        "VARIABLE_FROM_ENV",
        "VARIABLE_FROM_ENV".lower(),
        "VARIABLE_FROM_ENV".upper()
    ]
    
    possible_tokens = [
        "VARIABLE_FROM_ENV",
        "VARIABLE_FROM_ENV".lower(),
        "VARIABLE_FROM_ENV".upper(),
        "VARIABLE_FROM_ENV",
        "VARIABLE_FROM_ENV".lower(),
        "VARIABLE_FROM_ENV".upper()
    ]
    
    print("Testando combinações de credenciais...")
    
    for instance in possible_instances[:1]:  # Testar apenas a primeira para não sobrecarregar
        for token in possible_tokens[:2]:    # Testar apenas as primeiras
            url = f"https://api.z-api.io/instances/{instance}/token/{token}"
            
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{url}/status")
                    
                    if response.status_code == 200:
                        print(f"✅ ENCONTRADO! Instance: {instance[:8]}... Token: {token[:8]}...")
                        print(f"   URL: {url}")
                        return True
                    elif response.status_code == 400:
                        print(f"❌ Instance not found: {instance[:8]}... {token[:8]}...")
                    else:
                        print(f"⚠️ Status {response.status_code}: {instance[:8]}... {token[:8]}...")
                        
            except Exception as e:
                print(f"❌ Erro: {instance[:8]}... {token[:8]}... - {str(e)}")
    
    return False

if __name__ == "__main__":
    async def main():
        await verificar_zapi_status()
        await testar_credenciais_alternativas()
    
    asyncio.run(main()) 