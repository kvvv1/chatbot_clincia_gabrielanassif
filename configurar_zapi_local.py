#!/usr/bin/env python3
"""
Configurador Local Z-API
========================

Script para configurar as variáveis de ambiente do Z-API localmente
para permitir testes da API.

Uso: python configurar_zapi_local.py
"""

import os
import sys
from datetime import datetime

def configurar_zapi_local():
    """Configura as variáveis do Z-API localmente"""
    print("🔧 CONFIGURANDO Z-API LOCALMENTE")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Credenciais do Z-API (do arquivo vercel.env.example)
    zapi_config = {
        'ZAPI_INSTANCE_ID': 'VARIABLE_FROM_ENV',
        'ZAPI_TOKEN': 'VARIABLE_FROM_ENV',
        'ZAPI_CLIENT_TOKEN': 'VARIABLE_FROM_ENV',
        'ZAPI_BASE_URL': 'https://api.z-api.io'
    }
    
    # Configurar variáveis de ambiente
    for key, value in zapi_config.items():
        os.environ[key] = value
        print(f"✅ {key}: {'*' * len(value[:10])}...")
    
    print()
    print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("As variáveis do Z-API foram configuradas para esta sessão.")
    print()
    print("📋 Para testar, execute:")
    print("   python test_zapi_rapido.py")
    print()
    print("⚠️  NOTA: Estas configurações são apenas para esta sessão.")
    print("   Para configuração permanente, crie um arquivo .env")
    
    return True

def criar_arquivo_env():
    """Cria arquivo .env com as configurações"""
    print("📄 CRIANDO ARQUIVO .env")
    print("=" * 30)
    
    env_content = """# Configurações Z-API
ZAPI_INSTANCE_ID=VARIABLE_FROM_ENV
ZAPI_TOKEN=VARIABLE_FROM_ENV
ZAPI_CLIENT_TOKEN=VARIABLE_FROM_ENV
ZAPI_BASE_URL=https://api.z-api.io

# Outras configurações
ENVIRONMENT=development
DEBUG=True
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado com sucesso!")
        print("📁 Localização: .env")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURADOR Z-API")
    print("=" * 30)
    print("1. Configurar para esta sessão")
    print("2. Criar arquivo .env permanente")
    print("3. Ambos")
    print()
    
    try:
        opcao = input("Escolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            configurar_zapi_local()
        elif opcao == "2":
            criar_arquivo_env()
        elif opcao == "3":
            configurar_zapi_local()
            print()
            criar_arquivo_env()
        else:
            print("❌ Opção inválida!")
            return False
        
        print()
        print("🎉 Configuração concluída!")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada")
        return False
    except Exception as e:
        print(f"\n💥 Erro: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 