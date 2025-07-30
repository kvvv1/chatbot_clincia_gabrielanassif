#!/usr/bin/env python3
"""
Script para atualizar variáveis de ambiente no Vercel
"""

import requests
import json
import os

def atualizar_vercel_env():
    """Atualiza variáveis de ambiente no Vercel"""
    print("🔧 Atualizando variáveis de ambiente no Vercel...")
    
    # Ler configurações do arquivo
    env_file = "vercel.env.production"
    if not os.path.exists(env_file):
        print(f"❌ Arquivo {env_file} não encontrado!")
        return False
    
    # Ler variáveis do arquivo
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    print(f"📝 Variáveis encontradas: {len(env_vars)}")
    
    # Mostrar variáveis importantes
    important_vars = ['ZAPI_CLIENT_TOKEN', 'ZAPI_INSTANCE_ID', 'ZAPI_TOKEN']
    for var in important_vars:
        if var in env_vars:
            value = env_vars[var]
            if len(value) > 20:
                value = value[:20] + "..."
            print(f"   {var}: {value}")
    
    print("\n📋 INSTRUÇÕES PARA ATUALIZAR NO VERCEL:")
    print("1. Acesse: https://vercel.com/dashboard")
    print("2. Vá para o projeto: chatbot-clincia")
    print("3. Clique em 'Settings' > 'Environment Variables'")
    print("4. Atualize as seguintes variáveis:")
    
    for key, value in env_vars.items():
        print(f"   {key} = {value}")
    
    print("\n🔧 OU use o Vercel CLI:")
    print("vercel env add ZAPI_CLIENT_TOKEN production")
    print("vercel env add ZAPI_INSTANCE_ID production")
    print("vercel env add ZAPI_TOKEN production")
    
    return True

def testar_apos_atualizacao():
    """Testa o sistema após atualização"""
    print("\n🧪 Testando sistema após atualização...")
    
    try:
        import requests
        
        # Aguardar um pouco
        import time
        print("⏳ Aguardando 30 segundos...")
        time.sleep(30)
        
        # Testar endpoint
        response = requests.get("https://chatbot-clincia.vercel.app/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Sistema funcionando!")
            
            # Testar envio de mensagem
            test_message = {
                "event": "message",
                "data": {
                    "id": "test_after_update",
                    "type": "text",
                    "phone": "553198600366",
                    "message": "oi",
                    "timestamp": int(time.time())
                }
            }
            
            response = requests.post(
                "https://chatbot-clincia.vercel.app/webhook",
                json=test_message,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Mensagem processada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao processar mensagem: {response.status_code}")
                return False
        else:
            print(f"❌ Sistema com problema: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 ATUALIZAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    # Atualizar variáveis
    success = atualizar_vercel_env()
    
    if success:
        print("\n✅ Variáveis preparadas!")
        print("🔧 Agora atualize no painel do Vercel")
        
        # Perguntar se quer testar
        print("\n🧪 Deseja testar após atualização? (s/n): ", end="")
        try:
            resposta = input().lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                testar_apos_atualizacao()
        except:
            pass
    else:
        print("\n❌ Erro ao preparar variáveis!") 