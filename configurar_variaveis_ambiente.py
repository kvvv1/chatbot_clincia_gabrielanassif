#!/usr/bin/env python3
"""
Script para configurar todas as variáveis de ambiente necessárias para o chatbot
"""

import os
import json
from pathlib import Path

def print_banner():
    """Exibe o banner do script"""
    print("=" * 60)
    print("🔧 CONFIGURADOR DE VARIÁVEIS DE AMBIENTE")
    print("=" * 60)
    print("Este script irá configurar todas as variáveis necessárias")
    print("para o funcionamento do chatbot.")
    print()

def get_input(prompt, default="", required=True, secret=False):
    """Função para obter entrada do usuário com validação"""
    while True:
        if secret:
            import getpass
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)
        
        if not value and default:
            value = default
            print(f"Usando valor padrão: {default}")
        
        if required and not value:
            print("❌ Este campo é obrigatório!")
            continue
        
        return value

def create_env_file(variables):
    """Cria o arquivo .env com as variáveis configuradas"""
    env_content = "# Configurações do Chatbot\n"
    env_content += "# Gerado automaticamente pelo configurador\n\n"
    
    for key, value in variables.items():
        env_content += f"{key}={value}\n"
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")

def create_vercel_env_file(variables):
    """Cria o arquivo vercel_env_vars.json para deploy no Vercel"""
    vercel_vars = {}
    
    # Mapeia as variáveis para o formato do Vercel
    for key, value in variables.items():
        vercel_vars[key] = value
    
    with open('vercel_env_vars.json', 'w', encoding='utf-8') as f:
        json.dump(vercel_vars, f, indent=2, ensure_ascii=False)
    
    print("✅ Arquivo vercel_env_vars.json criado com sucesso!")

def main():
    """Função principal do configurador"""
    print_banner()
    
    print("📋 Vamos configurar as variáveis de ambiente necessárias:")
    print()
    
    variables = {}
    
    # 1. SUPABASE
    print("🔵 CONFIGURAÇÃO DO SUPABASE")
    print("-" * 30)
    variables['SUPABASE_URL'] = get_input(
        "URL do Supabase (ex: https://seu-projeto.supabase.co): ",
        required=True
    )
    variables['SUPABASE_ANON_KEY'] = get_input(
        "Chave anônima do Supabase: ",
        required=True,
        secret=True
    )
    variables['SUPABASE_SERVICE_ROLE_KEY'] = get_input(
        "Chave de serviço do Supabase: ",
        required=True,
        secret=True
    )
    print()
    
    # 2. Z-API (WhatsApp)
    print("🟢 CONFIGURAÇÃO DO Z-API (WHATSAPP)")
    print("-" * 30)
    variables['ZAPI_TOKEN'] = get_input(
        "Token do Z-API: ",
        required=True,
        secret=True
    )
    variables['WEBHOOK_URL'] = get_input(
        "URL do Webhook (ex: https://seu-app.vercel.app/webhook): ",
        required=True
    )
    print()
    
    # 3. GESTÃODS
    print("🟡 CONFIGURAÇÃO DO GESTÃODS")
    print("-" * 30)
    variables['GESTAODS_URL'] = get_input(
        "URL do GestãoDS (ex: https://api.gestaods.com.br): ",
        default="https://api.gestaods.com.br"
    )
    variables['GESTAODS_TOKEN'] = get_input(
        "Token do GestãoDS: ",
        secret=True
    )
    variables['GESTAODS_CLINIC_ID'] = get_input(
        "ID da Clínica no GestãoDS: "
    )
    print()
    
    # 4. CONFIGURAÇÕES GERAIS
    print("⚙️ CONFIGURAÇÕES GERAIS")
    print("-" * 30)
    variables['APP_NAME'] = get_input(
        "Nome da aplicação: ",
        default="Chatbot Clínica"
    )
    variables['DEBUG'] = get_input(
        "Modo debug (true/false): ",
        default="false"
    )
    variables['LOG_LEVEL'] = get_input(
        "Nível de log (DEBUG/INFO/WARNING/ERROR): ",
        default="INFO"
    )
    print()
    
    # 5. WEBSOCKET
    print("🔌 CONFIGURAÇÃO DO WEBSOCKET")
    print("-" * 30)
    variables['WEBSOCKET_URL'] = get_input(
        "URL do WebSocket (ex: wss://seu-app.vercel.app/ws): ",
        default="wss://localhost:8000/ws"
    )
    print()
    
    # 6. CORS
    print("🌐 CONFIGURAÇÃO DO CORS")
    print("-" * 30)
    variables['CORS_ORIGINS'] = get_input(
        "Origins permitidos (separados por vírgula): ",
        default="http://localhost:3000,https://seu-app.vercel.app"
    )
    print()
    
    # 7. INFORMAÇÕES DA CLÍNICA
    print("🏥 INFORMAÇÕES DA CLÍNICA")
    print("-" * 30)
    variables['CLINIC_NAME'] = get_input(
        "Nome da clínica: ",
        default="Clínica Exemplo"
    )
    variables['CLINIC_PHONE'] = get_input(
        "Telefone da clínica: ",
        default="+5531999999999"
    )
    variables['CLINIC_ADDRESS'] = get_input(
        "Endereço da clínica: ",
        default="Rua Exemplo, 123 - Cidade"
    )
    print()
    
    # 8. CONFIGURAÇÕES AVANÇADAS
    print("🔧 CONFIGURAÇÕES AVANÇADAS")
    print("-" * 30)
    variables['MAX_RETRIES'] = get_input(
        "Máximo de tentativas para APIs: ",
        default="3"
    )
    variables['REQUEST_TIMEOUT'] = get_input(
        "Timeout das requisições (segundos): ",
        default="30"
    )
    variables['VERCEL'] = get_input(
        "Executando no Vercel (true/false): ",
        default="true"
    )
    print()
    
    # Salvar arquivos
    print("💾 Salvando configurações...")
    create_env_file(variables)
    create_vercel_env_file(variables)
    
    print()
    print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("✅ Arquivos criados:")
    print("   - .env (para desenvolvimento local)")
    print("   - vercel_env_vars.json (para deploy no Vercel)")
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python start_setup.py")
    print("2. Configure as variáveis no Vercel usando o arquivo vercel_env_vars.json")
    print("3. Faça o deploy da aplicação")
    print()
    print("🔍 Para verificar as configurações:")
    print("   - python setup_all_connections.py")
    print()

if __name__ == "__main__":
    main() 