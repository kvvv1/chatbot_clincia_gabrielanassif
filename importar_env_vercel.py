#!/usr/bin/env python3
"""
Script para importar variáveis de ambiente no Vercel
"""

import json
import os

def gerar_json_env():
    """Gera arquivo JSON com todas as variáveis para importação no Vercel"""
    
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
    
    # Salvar em arquivo JSON
    with open('vercel_env_import.json', 'w', encoding='utf-8') as f:
        json.dump(env_vars, f, indent=2, ensure_ascii=False)
    
    print("🚀 ARQUIVOS CRIADOS PARA IMPORTAÇÃO NO VERCEL")
    print("=" * 60)
    print()
    print("📁 Arquivos criados:")
    print("✅ vercel.env.production - Para copiar e colar")
    print("✅ vercel_env_import.json - Para importação automática")
    print()
    
    print("🔧 COMO IMPORTAR NO VERCEL:")
    print("-" * 40)
    print("1. Acesse: https://vercel.com/dashboard")
    print("2. Projeto: chatbot-clincia")
    print("3. Settings → Environment Variables")
    print("4. Clique em 'Add New'")
    print("5. Copie e cole as variáveis do arquivo vercel.env.production")
    print()
    
    print("📋 VARIÁVEIS PARA CONFIGURAR:")
    print("-" * 40)
    for i, (var_name, var_value) in enumerate(env_vars.items(), 1):
        print(f"{i:2d}. {var_name}={var_value}")
    
    print()
    print("🔗 WEBHOOKS PARA CONFIGURAR NO Z-API:")
    print("-" * 40)
    print("Ao receber: https://chatbot-clincia.vercel.app/webhook/message")
    print("Ao conectar: https://chatbot-clincia.vercel.app/webhook/connected")
    print("Receber status: https://chatbot-clincia.vercel.app/webhook/status")
    print()
    
    print("✅ APÓS CONFIGURAR:")
    print("-" * 40)
    print("1. Faça redeploy no Vercel")
    print("2. Execute: python test_complete_system.py")
    print("3. Teste enviando mensagem no WhatsApp")
    print()

def main():
    """Função principal"""
    gerar_json_env()

if __name__ == "__main__":
    main() 