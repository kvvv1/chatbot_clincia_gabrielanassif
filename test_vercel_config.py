#!/usr/bin/env python3
"""
Script para testar a configuração do Vercel e verificar variáveis de ambiente
"""

import os
import httpx
import asyncio
import json

async def test_vercel_config():
    print("🔍 TESTANDO CONFIGURAÇÃO VERCEL")
    print("=" * 50)
    
    # URL da aplicação Vercel
    vercel_url = "https://chatbot-clincia.vercel.app"
    
    print(f"1. 🌐 Testando aplicação Vercel: {vercel_url}")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Teste 1: Health check
            response = await client.get(f"{vercel_url}/health")
            print(f"   ✅ Health check: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Status: {data.get('status', 'N/A')}")
                print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
            
            # Teste 2: Webhook endpoint
            response = await client.get(f"{vercel_url}/webhook")
            print(f"   ✅ Webhook endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📡 Webhook: {data.get('message', 'N/A')}")
            
            # Teste 3: Config endpoint (se existir)
            try:
                response = await client.get(f"{vercel_url}/config")
                print(f"   ✅ Config endpoint: {response.status_code}")
            except:
                print("   ⚠️ Config endpoint não disponível")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar Vercel: {str(e)}")
        return False
    
    print("\n2. 🔧 Verificando variáveis de ambiente...")
    
    # Lista de variáveis importantes
    important_vars = [
        'ZAPI_INSTANCE_ID',
        'ZAPI_TOKEN', 
        'ZAPI_CLIENT_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'GESTAODS_TOKEN'
    ]
    
    missing_vars = []
    for var in important_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:10]}...")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADA")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Variáveis faltando: {', '.join(missing_vars)}")
        print("💡 Configure no painel do Vercel:")
        print("   https://vercel.com/dashboard")
        print("   → Seu projeto → Settings → Environment Variables")
    else:
        print("\n✅ Todas as variáveis importantes estão configuradas!")
    
    print("\n3. 📱 Testando Z-API...")
    
    # Testar Z-API com as credenciais
    zapi_instance = os.getenv('ZAPI_INSTANCE_ID')
    zapi_token = os.getenv('ZAPI_TOKEN')
    
    if zapi_instance and zapi_token:
        zapi_base = f"https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_base}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Z-API conectado!")
                    print(f"   📊 Status: {status_data}")
                else:
                    print(f"   ❌ Z-API erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Erro Z-API: {str(e)}")
    else:
        print("   ❌ Credenciais Z-API não configuradas")
    
    print("\n4. 🎯 Resumo do diagnóstico:")
    print("=" * 50)
    
    if missing_vars:
        print("❌ PROBLEMAS ENCONTRADOS:")
        print("   - Variáveis de ambiente faltando")
        print("   - Z-API pode não estar configurado")
        print("\n🔧 SOLUÇÃO:")
        print("   1. Configure as variáveis no Vercel")
        print("   2. Configure o webhook no Z-API")
        print("   3. Teste novamente")
    else:
        print("✅ CONFIGURAÇÃO APARENTEMENTE OK")
        print("   - Aplicação Vercel funcionando")
        print("   - Variáveis configuradas")
        print("\n🔧 PRÓXIMO PASSO:")
        print("   - Configure webhook no painel Z-API")
        print("   - URL: https://chatbot-clincia.vercel.app/webhook")

if __name__ == "__main__":
    asyncio.run(test_vercel_config()) 