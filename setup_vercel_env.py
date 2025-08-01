#!/usr/bin/env python3
"""
Script para configurar automaticamente as variáveis de ambiente no Vercel
"""

import os
import json
import requests
from typing import Dict, Any

def setup_vercel_environment():
    """Configura as variáveis de ambiente no Vercel"""
    
    # Variáveis de ambiente necessárias
    env_vars = {
        # Z-API Configuration
        "ZAPI_INSTANCE_ID": "VARIABLE_FROM_ENV",
        "ZAPI_TOKEN": "VARIABLE_FROM_ENV",
        "ZAPI_CLIENT_TOKEN": "VARIABLE_FROM_ENV",
        "ZAPI_BASE_URL": "https://api.z-api.io",
        
        # Supabase Configuration
        "SUPABASE_URL": "https://feqylqrphdpeeusdyeyw.supabase.co",
        "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc",
        
        # GestãoDS Configuration
        "GESTAODS_API_URL": "https://apidev.gestaods.com.br",
        "GESTAODS_TOKEN": "733a8e19a94b65d58390da380ac946b6d603a535",
        
        # App Configuration
        "ENVIRONMENT": "production",
        "DEBUG": "false",
        "CORS_ORIGINS": "*",
        "CORS_ALLOW_CREDENTIALS": "true",
        
        # Clinic Information
        "CLINIC_NAME": "Clínica Gabriela Nassif",
        "CLINIC_PHONE": "+553198600366",
        "REMINDER_HOUR": "18",
        "REMINDER_MINUTE": "0",
        
        # WebSocket Configuration
        "WEBSOCKET_ENABLED": "true",
        "WEBSOCKET_MAX_CONNECTIONS": "50"
    }
    
    print("🚀 Configurando Variáveis de Ambiente no Vercel")
    print("=" * 60)
    print()
    
    # Verificar se o Vercel CLI está instalado
    if not os.path.exists(os.path.expanduser("~/.vercel")):
        print("❌ Vercel CLI não encontrado!")
        print("📋 Instruções manuais:")
        print("1. Acesse: https://vercel.com/dashboard")
        print("2. Projeto: chatbot-clincia")
        print("3. Settings → Environment Variables")
        print("4. Configure as variáveis abaixo:")
        print()
        
        for var_name, var_value in env_vars.items():
            print(f"📝 {var_name}: {var_value}")
        
        # Salvar em arquivo para facilitar
        with open('vercel_env_vars.json', 'w', encoding='utf-8') as f:
            json.dump(env_vars, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Variáveis salvas em: vercel_env_vars.json")
        return
    
    # Tentar usar Vercel CLI
    try:
        import subprocess
        
        print("🔧 Configurando via Vercel CLI...")
        
        for var_name, var_value in env_vars.items():
            print(f"📝 Configurando: {var_name}")
            
            # Comando para adicionar variável
            cmd = [
                "vercel", "env", "add", var_name, 
                "production", "preview", "development"
            ]
            
            # Executar comando
            result = subprocess.run(
                cmd, 
                input=var_value.encode(), 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {var_name} configurado com sucesso")
            else:
                print(f"❌ Erro ao configurar {var_name}: {result.stderr}")
        
        print("\n🎉 Configuração concluída!")
        print("📋 Próximos passos:")
        print("1. Faça redeploy: vercel --prod")
        print("2. Teste: https://chatbot-clincia.vercel.app/")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print("📋 Use as instruções manuais acima")

def test_deployment():
    """Testa se o deploy está funcionando"""
    print("\n🧪 Testando Deploy...")
    
    try:
        response = requests.get("https://chatbot-clincia.vercel.app/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Deploy funcionando!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Ambiente: {data.get('environment')}")
            print(f"📦 Versão: {data.get('version')}")
        else:
            print(f"❌ Erro no deploy: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar deploy: {str(e)}")

def main():
    """Função principal"""
    setup_vercel_environment()
    test_deployment()

if __name__ == "__main__":
    main() 