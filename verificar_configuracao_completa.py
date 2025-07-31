#!/usr/bin/env python3
"""
Verificar configuração completa do sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx
from datetime import datetime

def verificar_variaveis_ambiente():
    print("🔧 VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # Verificar Z-API
        print("1. 📡 Z-API:")
        if settings.zapi_instance_id:
            print(f"   ✅ Instance ID: {settings.zapi_instance_id[:10]}...")
        else:
            print("   ❌ Instance ID: VAZIO")
            
        if settings.zapi_token:
            print(f"   ✅ Token: {settings.zapi_token[:10]}...")
        else:
            print("   ❌ Token: VAZIO")
            
        if settings.zapi_client_token:
            print(f"   ✅ Client Token: {settings.zapi_client_token[:10]}...")
        else:
            print("   ❌ Client Token: VAZIO")
        
        # Verificar Supabase
        print("\n2. 🗄️ Supabase:")
        if settings.supabase_url:
            print(f"   ✅ URL: {settings.supabase_url}")
        else:
            print("   ❌ URL: VAZIO")
            
        if settings.supabase_anon_key:
            print(f"   ✅ Anon Key: {settings.supabase_anon_key[:20]}...")
        else:
            print("   ❌ Anon Key: VAZIO")
        
        # Verificar App
        print("\n3. 🏗️ Aplicação:")
        print(f"   Host: {settings.app_host}")
        print(f"   Port: {settings.app_port}")
        print(f"   Environment: {settings.environment}")
        
        # Construir webhook URL
        if settings.environment == "production":
            webhook_url = f"https://{settings.app_host}/webhook"
        else:
            webhook_url = f"http://{settings.app_host}:{settings.app_port}/webhook"
        
        print(f"   📡 Webhook URL: {webhook_url}")
        
        # Verificar problemas críticos
        problemas = []
        
        if not settings.zapi_instance_id or not settings.zapi_token:
            problemas.append("❌ Credenciais Z-API incompletas")
        
        if not settings.supabase_url or not settings.supabase_anon_key:
            problemas.append("⚠️ Supabase não configurado (usará mock)")
        
        if settings.app_host == "0.0.0.0" and settings.environment == "production":
            problemas.append("⚠️ Host 0.0.0.0 pode não funcionar em produção")
        
        if problemas:
            print(f"\n🚨 PROBLEMAS ENCONTRADOS:")
            for problema in problemas:
                print(f"   {problema}")
        else:
            print(f"\n✅ CONFIGURAÇÃO BÁSICA OK!")
            
        return len(problemas) == 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {str(e)}")
        return False

async def testar_conectividade_local():
    print("\n\n🌐 TESTANDO CONECTIVIDADE LOCAL")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # URL local
        if settings.environment == "production":
            base_url = f"https://{settings.app_host}"
        else:
            base_url = f"http://{settings.app_host}:{settings.app_port}"
        
        print(f"1. 🔗 URL base: {base_url}")
        
        # Testar health check
        print("\n2. 🏥 Testando health check...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{base_url}/webhook/health")
                
                if response.status_code == 200:
                    print("   ✅ Health check OK!")
                    data = response.json()
                    print(f"   📊 Status: {data.get('status')}")
                    print(f"   🕐 Timestamp: {data.get('timestamp')}")
                else:
                    print(f"   ❌ Health check falhou: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro no health check: {str(e)}")
            print("   💡 Aplicação pode não estar rodando")
            return False
        
        # Testar webhook endpoint
        print("\n3. 📨 Testando webhook endpoint...")
        
        webhook_data = {
            "type": "ReceivedCallback",
            "phone": "5531999999999@c.us",
            "text": {"message": "teste"},
            "messageId": "test_connectivity",
            "fromMe": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{base_url}/webhook",
                    json=webhook_data
                )
                
                if response.status_code == 200:
                    print("   ✅ Webhook endpoint respondendo!")
                    return True
                else:
                    print(f"   ❌ Webhook endpoint erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro no webhook: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

async def verificar_zapi_webhook():
    print("\n\n📱 VERIFICANDO CONFIGURAÇÃO Z-API")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        if not settings.zapi_instance_id or not settings.zapi_token:
            print("❌ Credenciais Z-API não configuradas!")
            return False
        
        print("1. 📡 Testando conexão com Z-API...")
        
        # URL da Z-API
        zapi_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        # Testar status da instância
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_url}/status")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Instância Z-API conectada!")
                    print(f"   📊 Status: {data}")
                else:
                    print(f"   ❌ Erro ao conectar Z-API: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro na conexão Z-API: {str(e)}")
            return False
        
        print("\n2. 🔗 Verificando webhook configurado...")
        
        # Verificar webhook atual
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{zapi_url}/webhook")
                
                if response.status_code == 200:
                    webhook_info = response.json()
                    print(f"   📋 Webhook atual: {webhook_info}")
                    
                    # Verificar se está configurado corretamente
                    webhook_url = webhook_info.get('webhook', '')
                    
                    if 'webhook' in webhook_url:
                        print("   ✅ Webhook configurado!")
                        return True
                    else:
                        print("   ⚠️ Webhook não configurado ou incorreto")
                        return False
                else:
                    print(f"   ❌ Erro ao verificar webhook: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Erro ao verificar webhook: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral Z-API: {str(e)}")
        return False

def gerar_comandos_correcao(config_ok, conectividade_ok, zapi_ok):
    print("\n\n🛠️ COMANDOS PARA CORREÇÃO")
    print("=" * 50)
    
    if not config_ok:
        print("1. 🔧 Configurar variáveis de ambiente:")
        print("   # Copie o arquivo de exemplo:")
        print("   cp .env.example .env")
        print("   # Edite o arquivo .env com suas credenciais:")
        print("   nano .env")
        print()
    
    if not conectividade_ok:
        print("2. 🚀 Subir aplicação:")
        print("   # Local:")
        print("   python run.py")
        print("   # Ou Vercel:")
        print("   vercel dev")
        print()
    
    if not zapi_ok:
        print("3. 📱 Configurar webhook Z-API:")
        print("   python configurar_webhook_zapi_correto.py")
        print()
    
    print("4. 🧪 Testar sistema completo:")
    print("   python test_sistema_completo.py")
    print()
    
    print("5. 📱 Teste manual WhatsApp:")
    print("   - Envie: 'oi'")
    print("   - Deve receber: Menu com opções 1-5")
    print("   - Envie: '1'")
    print("   - Deve receber: 'Digite seu CPF'")

if __name__ == "__main__":
    try:
        print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA")
        print("=" * 70)
        
        # Executar verificações
        config_ok = verificar_variaveis_ambiente()
        conectividade_ok = asyncio.run(testar_conectividade_local())
        zapi_ok = asyncio.run(verificar_zapi_webhook())
        
        # Resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DO DIAGNÓSTICO:")
        print(f"   🔧 Configuração: {'✅ OK' if config_ok else '❌ PROBLEMA'}")
        print(f"   🌐 Conectividade: {'✅ OK' if conectividade_ok else '❌ PROBLEMA'}")
        print(f"   📱 Z-API Webhook: {'✅ OK' if zapi_ok else '❌ PROBLEMA'}")
        
        if config_ok and conectividade_ok and zapi_ok:
            print("\n🎉 SISTEMA TOTALMENTE CONFIGURADO!")
            print("✅ Seu chatbot deve estar funcionando perfeitamente!")
            print("📱 Teste enviando uma mensagem pelo WhatsApp")
        else:
            print("\n⚠️ SISTEMA PRECISA DE AJUSTES")
            gerar_comandos_correcao(config_ok, conectividade_ok, zapi_ok)
            
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()