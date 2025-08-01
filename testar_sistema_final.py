#!/usr/bin/env python3
"""
Script para testar o sistema completo após configuração manual do webhook
"""

import asyncio
import httpx
from app.config import settings

async def testar_sistema_final():
    """Testa o sistema completo após configuração manual"""
    print("🧪 Testando sistema completo após configuração manual...")
    
    try:
        # Teste 1: Verificar Vercel
        print("\n1. Verificando Vercel...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://chatbot-clincia.vercel.app/",
                    timeout=10.0
                )
                print(f"   Status: {response.status_code}")
                if response.status_code in [200, 307]:
                    print("   ✅ Vercel funcionando!")
                else:
                    print(f"   ❌ Vercel com problema: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro ao verificar Vercel: {e}")
        
        # Teste 2: Verificar endpoints do webhook
        print("\n2. Verificando endpoints do webhook...")
        endpoints = [
            "/webhook",
            "/webhook/message",
            "/webhook/status",
            "/webhook/connected"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://chatbot-clincia.vercel.app{endpoint}",
                        timeout=5.0
                    )
                    print(f"   {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: ❌ Erro - {e}")
        
        # Teste 3: Testar webhook com dados simulados
        print("\n3. Testando webhook com dados simulados...")
        try:
            async with httpx.AsyncClient() as client:
                test_data = {
                    "event": "message",
                    "data": {
                        "id": "test_final",
                        "type": "text",
                        "from": "553198600366@c.us",
                        "fromMe": False,
                        "text": {
                            "body": "1"
                        }
                    }
                }
                
                response = await client.post(
                    "https://chatbot-clincia.vercel.app/webhook/message",
                    json=test_data,
                    timeout=15.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Webhook funcionando: {data}")
                else:
                    print(f"   ❌ Erro no webhook: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro ao testar webhook: {e}")
        
        # Teste 4: Verificar Z-API
        print("\n4. Verificando Z-API...")
        try:
            base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
            headers = {
                "Client-Token": settings.zapi_client_token,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/status",
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("connected"):
                        print("   ✅ Z-API conectado!")
                    else:
                        print(f"   ⚠️  Z-API não conectado: {data}")
                else:
                    print(f"   ❌ Erro no Z-API: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro ao verificar Z-API: {e}")
        
        # Teste 5: Testar envio de mensagem
        print("\n5. Testando envio de mensagem...")
        try:
            base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
            headers = {
                "Client-Token": settings.zapi_client_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "phone": "553198600366@c.us",
                "message": "Teste final do sistema - " + asyncio.get_event_loop().time().__str__()[:10]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/send-text",
                    json=payload,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Mensagem enviada: {data}")
                else:
                    print(f"   ❌ Erro ao enviar mensagem: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro ao testar envio: {e}")
        
        # Teste 6: Verificar Supabase
        print("\n6. Verificando Supabase...")
        try:
            from app.services.supabase_service import SupabaseService
            supabase = SupabaseService()
            
            # Testar conexão
            result = supabase.client.table("conversations").select("*").limit(1).execute()
            print(f"   ✅ Supabase conectado! {len(result.data)} registros")
        except Exception as e:
            print(f"   ❌ Erro ao verificar Supabase: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

async def instrucoes_finais():
    """Mostra instruções finais"""
    print("\n" + "="*60)
    print("🎯 INSTRUÇÕES FINAIS")
    print("="*60)
    
    print("\n📋 Para finalizar a configuração:")
    print("1. Faça o deploy: npx vercel --prod")
    print("2. Configure o webhook manualmente no Z-API:")
    print("   - Acesse: https://app.z-api.io/")
    print("   - Vá para sua instância: VARIABLE_FROM_ENV")
    print("   - Configure as URLs do webhook para apontar para o Vercel")
    print("3. Teste enviando uma mensagem para o WhatsApp da clínica")
    
    print("\n🔗 URLs do webhook para configurar:")
    print("   - Ao receber: https://chatbot-clincia.vercel.app/webhook/message")
    print("   - Ao enviar: https://chatbot-clincia.vercel.app/webhook")
    print("   - Ao conectar: https://chatbot-clincia.vercel.app/webhook/connected")
    print("   - Ao desconectar: https://chatbot-clincia.vercel.app/webhook")
    print("   - Receber status: https://chatbot-clincia.vercel.app/webhook/status")
    
    print("\n🎉 Sistema pronto para funcionar!")

async def main():
    """Função principal"""
    print("🚀 Testando sistema completo...")
    
    await testar_sistema_final()
    await instrucoes_finais()

if __name__ == "__main__":
    asyncio.run(main()) 