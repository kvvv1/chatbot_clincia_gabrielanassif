#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente no Vercel
"""

import json
import os

def gerar_instrucoes_vercel():
    """Gera instruções para configurar variáveis no Vercel"""
    
    # Variáveis de ambiente necessárias
    env_vars = {
        # Z-API Configuration
        "ZAPI_INSTANCE_ID": "3E4F7360B552F0C2DBCB9E6774402775",
        "ZAPI_TOKEN": "17829E98BB59E9ADD55BBBA9",
        "ZAPI_CLIENT_TOKEN": "F909fc109aad54566bf42a6d09f00a8dbS",
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
    
    print("🚀 CONFIGURAÇÃO DAS VARIÁVEIS DE AMBIENTE NO VERCEL")
    print("=" * 70)
    print()
    
    print("📋 PASSO A PASSO:")
    print("1. Acesse: https://vercel.com/dashboard")
    print("2. Selecione o projeto: chatbot-clincia")
    print("3. Vá em: Settings → Environment Variables")
    print("4. Clique em: Add New")
    print("5. Configure cada variável abaixo:")
    print()
    
    print("🔧 VARIÁVEIS PARA CONFIGURAR:")
    print("-" * 50)
    
    for i, (var_name, var_value) in enumerate(env_vars.items(), 1):
        print(f"{i:2d}. Nome: {var_name}")
        print(f"    Valor: {var_value}")
        print(f"    Ambientes: ✅ Production ✅ Preview ✅ Development")
        print()
    
    print("📝 INSTRUÇÕES DETALHADAS:")
    print("-" * 50)
    print("Para cada variável:")
    print("1. Clique em 'Add New'")
    print("2. Digite o Nome da variável")
    print("3. Digite o Valor da variável")
    print("4. Marque todos os ambientes (Production, Preview, Development)")
    print("5. Clique em 'Save'")
    print()
    
    print("✅ APÓS CONFIGURAR TODAS:")
    print("-" * 50)
    print("1. Vá em: Deployments")
    print("2. Clique em 'Redeploy' no último deployment")
    print("3. Aguarde o deploy terminar")
    print("4. Teste: https://chatbot-clincia.vercel.app/")
    print()
    
    # Salvar em arquivo JSON
    with open('vercel_env_vars.json', 'w', encoding='utf-8') as f:
        json.dump(env_vars, f, indent=2, ensure_ascii=False)
    
    print("💾 Arquivo 'vercel_env_vars.json' criado!")
    print("Você pode copiar e colar os valores deste arquivo.")
    print()
    
    print("🔗 URLs DOS WEBHOOKS PARA CONFIGURAR NO Z-API:")
    print("-" * 50)
    print("Ao receber: https://chatbot-clincia.vercel.app/webhook/message")
    print("Ao conectar: https://chatbot-clincia.vercel.app/webhook/connected")
    print("Receber status: https://chatbot-clincia.vercel.app/webhook/status")
    print()
    
    print("🧪 TESTE APÓS CONFIGURAÇÃO:")
    print("-" * 50)
    print("1. Execute: python test_complete_system.py")
    print("2. Envie uma mensagem para o WhatsApp")
    print("3. Verifique os logs no Vercel")
    print()

def main():
    """Função principal"""
    gerar_instrucoes_vercel()

if __name__ == "__main__":
    main() 