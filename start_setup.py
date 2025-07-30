#!/usr/bin/env python3
"""
Script de inicialização rápida para configurar todo o sistema de chatbot
Este é o script principal que você deve executar primeiro
"""

import os
import sys
import asyncio
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Imprime banner do sistema"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 SISTEMA DE CHATBOT                     ║
║                    Clínica Gabriela Nassif                   ║
║                                                              ║
║  Este script irá configurar automaticamente:                ║
║  ✅ Supabase (banco de dados)                               ║
║  ✅ Z-API (WhatsApp Business)                               ║
║  ✅ Webhook (recebimento de mensagens)                      ║
║  ✅ Testes de conexão                                       ║
║  ✅ Arquivos de configuração                                ║
║  ✅ Guia de deploy                                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 ou superior é necessário")
        sys.exit(1)
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_dependencies():
    """Verifica dependências necessárias"""
    logger.info("=== VERIFICANDO DEPENDÊNCIAS ===")
    
    required_packages = [
        "httpx",
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} não encontrado")
    
    if missing_packages:
        logger.error("❌ Dependências faltando!")
        logger.info("Instale as dependências com:")
        logger.info("pip install -r requirements.txt")
        return False
    
    logger.info("✅ Todas as dependências estão instaladas")
    return True

def setup_environment_variables():
    """Configura variáveis de ambiente se não existirem"""
    logger.info("=== CONFIGURANDO VARIÁVEIS DE AMBIENTE ===")
    
    # Verificar se já existem
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "WEBHOOK_URL"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning("⚠️ Algumas variáveis de ambiente não estão configuradas:")
        for var in missing_vars:
            logger.warning(f"   - {var}")
        
        logger.info("")
        logger.info("📝 Configure as variáveis de ambiente:")
        logger.info("")
        logger.info("Para Windows (PowerShell):")
        logger.info("$env:SUPABASE_URL='sua_url_do_supabase'")
        logger.info("$env:SUPABASE_ANON_KEY='sua_chave_anonima'")
        logger.info("$env:SUPABASE_SERVICE_ROLE_KEY='sua_chave_service_role'")
        logger.info("$env:WEBHOOK_URL='https://seu-app.vercel.app/webhook'")
        logger.info("")
        logger.info("Para Linux/Mac:")
        logger.info("export SUPABASE_URL=sua_url_do_supabase")
        logger.info("export SUPABASE_ANON_KEY=sua_chave_anonima")
        logger.info("export SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role")
        logger.info("export WEBHOOK_URL=https://seu-app.vercel.app/webhook")
        logger.info("")
        
        # Perguntar se quer continuar
        response = input("Deseja continuar mesmo sem todas as variáveis? (s/N): ")
        if response.lower() not in ['s', 'sim', 'y', 'yes']:
            logger.info("Setup cancelado pelo usuário")
            sys.exit(0)
    else:
        logger.info("✅ Todas as variáveis de ambiente estão configuradas")

def run_setup():
    """Executa o setup completo"""
    logger.info("")
    logger.info("🚀 INICIANDO SETUP COMPLETO...")
    logger.info("=" * 50)
    
    try:
        # Importar e executar o setup completo
        from setup_complete_system import CompleteSystemSetup
        
        async def main():
            setup = CompleteSystemSetup()
            await setup.run_complete_setup()
        
        asyncio.run(main())
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {str(e)}")
        logger.info("Verifique se todos os arquivos estão presentes")
        return False
    except Exception as e:
        logger.error(f"❌ Erro durante o setup: {str(e)}")
        return False
    
    return True

def print_next_steps():
    """Imprime próximos passos"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("🎯 PRÓXIMOS PASSOS")
    logger.info("=" * 60)
    logger.info("")
    logger.info("1. 📚 LEIA O GUIA DE DEPLOY")
    logger.info("   Abra o arquivo DEPLOYMENT_GUIDE.md")
    logger.info("")
    logger.info("2. 🌐 CONFIGURE O VERCEL")
    logger.info("   - Acesse: https://vercel.com")
    logger.info("   - Importe seu repositório")
    logger.info("   - Configure as variáveis de ambiente")
    logger.info("")
    logger.info("3. 🔗 CONFIGURE O WEBHOOK")
    logger.info("   - Acesse o painel do Z-API")
    logger.info("   - Configure a URL do webhook")
    logger.info("")
    logger.info("4. 🧪 TESTE O SISTEMA")
    logger.info("   - Envie uma mensagem para o WhatsApp")
    logger.info("   - Verifique se o chatbot responde")
    logger.info("")
    logger.info("5. 📊 MONITORE OS LOGS")
    logger.info("   - Verifique os logs no Vercel")
    logger.info("   - Monitore o dashboard do Supabase")
    logger.info("")
    logger.info("📞 SUPORTE:")
    logger.info("   - Verifique os logs de erro")
    logger.info("   - Execute: python setup_all_connections.py")
    logger.info("   - Consulte a documentação")
    logger.info("=" * 60)

def main():
    """Função principal"""
    print_banner()
    
    # Verificações iniciais
    check_python_version()
    
    if not check_dependencies():
        logger.error("❌ Setup cancelado - dependências não atendidas")
        sys.exit(1)
    
    setup_environment_variables()
    
    # Executar setup
    if run_setup():
        print_next_steps()
        logger.info("🎉 Setup concluído com sucesso!")
    else:
        logger.error("❌ Setup falhou - verifique os erros acima")
        sys.exit(1)

if __name__ == "__main__":
    main() 