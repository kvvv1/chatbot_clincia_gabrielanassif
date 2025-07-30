#!/usr/bin/env python3
"""
Script principal para configurar todo o sistema de chatbot
Executa todos os setups necessários: Supabase, Z-API, Webhook, etc.
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteSystemSetup:
    def __init__(self):
        self.setup_results = {}
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, str]:
        """Carrega configurações do ambiente"""
        return {
            "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
            "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", ""),
            "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
            "ZAPI_INSTANCE_ID": os.getenv("ZAPI_INSTANCE_ID", "3E4F7360B552F0C2DBCB9E6774402775"),
            "ZAPI_TOKEN": os.getenv("ZAPI_TOKEN", "17829E98BB59E9ADD55BBBA9"),
            "ZAPI_CLIENT_TOKEN": os.getenv("ZAPI_CLIENT_TOKEN", "F909fc109aad54566bf42a6d09f00a8dbS"),
            "WEBHOOK_URL": os.getenv("WEBHOOK_URL", ""),
            "VERCEL_URL": os.getenv("VERCEL_URL", "")
        }
    
    def check_requirements(self) -> bool:
        """Verifica se todos os requisitos estão atendidos"""
        logger.info("=== VERIFICANDO REQUISITOS ===")
        
        missing_configs = []
        
        if not self.config["SUPABASE_URL"]:
            missing_configs.append("SUPABASE_URL")
        if not self.config["SUPABASE_ANON_KEY"]:
            missing_configs.append("SUPABASE_ANON_KEY")
        if not self.config["SUPABASE_SERVICE_ROLE_KEY"]:
            missing_configs.append("SUPABASE_SERVICE_ROLE_KEY")
        if not self.config["WEBHOOK_URL"]:
            missing_configs.append("WEBHOOK_URL")
        
        if missing_configs:
            logger.error("❌ Configurações faltando:")
            for config in missing_configs:
                logger.error(f"   - {config}")
            logger.info("")
            logger.info("📝 Configure as variáveis de ambiente:")
            logger.info("   export SUPABASE_URL=sua_url_do_supabase")
            logger.info("   export SUPABASE_ANON_KEY=sua_chave_anonima")
            logger.info("   export SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role")
            logger.info("   export WEBHOOK_URL=https://seu-app.vercel.app/webhook")
            return False
        
        logger.info("✅ Todas as configurações necessárias estão presentes")
        return True
    
    async def run_supabase_setup(self) -> bool:
        """Executa setup do Supabase"""
        logger.info("")
        logger.info("🔄 EXECUTANDO SETUP DO SUPABASE")
        logger.info("=" * 40)
        
        try:
            result = subprocess.run(
                [sys.executable, "setup_supabase.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                logger.info("✅ Setup do Supabase concluído com sucesso")
                return True
            else:
                logger.error(f"❌ Erro no setup do Supabase: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no setup do Supabase")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao executar setup do Supabase: {str(e)}")
            return False
    
    async def run_webhook_setup(self) -> bool:
        """Executa setup do webhook"""
        logger.info("")
        logger.info("🔄 EXECUTANDO SETUP DO WEBHOOK")
        logger.info("=" * 40)
        
        try:
            result = subprocess.run(
                [sys.executable, "setup_webhook.py"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutos
            )
            
            if result.returncode == 0:
                logger.info("✅ Setup do webhook concluído com sucesso")
                return True
            else:
                logger.error(f"❌ Erro no setup do webhook: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no setup do webhook")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao executar setup do webhook: {str(e)}")
            return False
    
    async def run_connection_tests(self) -> bool:
        """Executa testes de conexão"""
        logger.info("")
        logger.info("🔄 EXECUTANDO TESTES DE CONEXÃO")
        logger.info("=" * 40)
        
        try:
            result = subprocess.run(
                [sys.executable, "setup_all_connections.py"],
                capture_output=True,
                text=True,
                timeout=180  # 3 minutos
            )
            
            if result.returncode == 0:
                logger.info("✅ Testes de conexão concluídos com sucesso")
                return True
            else:
                logger.error(f"❌ Erro nos testes de conexão: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout nos testes de conexão")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao executar testes de conexão: {str(e)}")
            return False
    
    def create_deployment_guide(self):
        """Cria guia de deploy"""
        logger.info("")
        logger.info("📝 CRIANDO GUIA DE DEPLOY")
        logger.info("=" * 40)
        
        guide_content = f"""# Guia de Deploy - Sistema de Chatbot

## Configurações Atuais

### Supabase
- URL: {self.config['SUPABASE_URL']}
- Status: {'✅ Configurado' if self.setup_results.get('supabase') else '❌ Falhou'}

### Z-API
- Instance ID: {self.config['ZAPI_INSTANCE_ID']}
- Status: {'✅ Configurado' if self.setup_results.get('zapi') else '❌ Falhou'}

### Webhook
- URL: {self.config['WEBHOOK_URL']}
- Status: {'✅ Configurado' if self.setup_results.get('webhook') else '❌ Falhou'}

## Variáveis de Ambiente para Vercel

Configure as seguintes variáveis no seu projeto Vercel:

```bash
SUPABASE_URL={self.config['SUPABASE_URL']}
SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
SUPABASE_SERVICE_ROLE_KEY={self.config['SUPABASE_SERVICE_ROLE_KEY']}
ZAPI_INSTANCE_ID={self.config['ZAPI_INSTANCE_ID']}
ZAPI_TOKEN={self.config['ZAPI_TOKEN']}
ZAPI_CLIENT_TOKEN={self.config['ZAPI_CLIENT_TOKEN']}
ZAPI_BASE_URL=https://api.z-api.io
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=733a8e19a94b65d58390da380ac946b6d603a535
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=*
CLINIC_NAME=Clínica Gabriela Nassif
CLINIC_PHONE=553198600366
REMINDER_HOUR=18
REMINDER_MINUTE=0
WEBSOCKET_ENABLED=false
WEBSOCKET_MAX_CONNECTIONS=10
VERCEL=1
```

## Passos para Deploy

1. **Faça push do código para o GitHub**
   ```bash
   git add .
   git commit -m "Setup completo do sistema"
   git push origin main
   ```

2. **Configure o projeto no Vercel**
   - Acesse: https://vercel.com
   - Importe o repositório do GitHub
   - Configure as variáveis de ambiente listadas acima

3. **Configure o webhook no Z-API**
   - Acesse o painel do Z-API
   - Configure a URL do webhook: {self.config['WEBHOOK_URL']}
   - Ative os eventos: message, message-status, connection-status

4. **Teste o sistema**
   - Envie uma mensagem para o WhatsApp da clínica
   - Verifique se o chatbot responde
   - Monitore os logs no Vercel

## Monitoramento

- **Logs do Vercel**: Acesse o dashboard do projeto no Vercel
- **Logs do Supabase**: Acesse o dashboard do Supabase
- **Status do Z-API**: Acesse o painel do Z-API

## Suporte

Em caso de problemas:
1. Verifique os logs do Vercel
2. Teste as conexões com: `python setup_all_connections.py`
3. Verifique as configurações do webhook
4. Monitore o status da instância do Z-API

---
Gerado automaticamente em: {asyncio.get_event_loop().time()}
"""
        
        try:
            with open("DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
                f.write(guide_content)
            logger.info("✅ Guia de deploy criado: DEPLOYMENT_GUIDE.md")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar guia de deploy: {str(e)}")
            return False
    
    def create_vercel_env_file(self):
        """Cria arquivo de variáveis para Vercel"""
        logger.info("")
        logger.info("📝 CRIANDO ARQUIVO DE VARIÁVEIS VERCEL")
        logger.info("=" * 40)
        
        vercel_env = {
            "SUPABASE_URL": self.config["SUPABASE_URL"],
            "SUPABASE_ANON_KEY": self.config["SUPABASE_ANON_KEY"],
            "SUPABASE_SERVICE_ROLE_KEY": self.config["SUPABASE_SERVICE_ROLE_KEY"],
            "ZAPI_INSTANCE_ID": self.config["ZAPI_INSTANCE_ID"],
            "ZAPI_TOKEN": self.config["ZAPI_TOKEN"],
            "ZAPI_CLIENT_TOKEN": self.config["ZAPI_CLIENT_TOKEN"],
            "ZAPI_BASE_URL": "https://api.z-api.io",
            "GESTAODS_API_URL": "https://apidev.gestaods.com.br",
            "GESTAODS_TOKEN": "733a8e19a94b65d58390da380ac946b6d603a535",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "CORS_ORIGINS": "*",
            "CLINIC_NAME": "Clínica Gabriela Nassif",
            "CLINIC_PHONE": "553198600366",
            "REMINDER_HOUR": "18",
            "REMINDER_MINUTE": "0",
            "WEBSOCKET_ENABLED": "false",
            "WEBSOCKET_MAX_CONNECTIONS": "10",
            "VERCEL": "1"
        }
        
        try:
            with open("vercel_env_vars.json", "w", encoding="utf-8") as f:
                json.dump(vercel_env, f, indent=2)
            logger.info("✅ Arquivo vercel_env_vars.json criado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo Vercel: {str(e)}")
            return False
    
    async def run_complete_setup(self):
        """Executa setup completo do sistema"""
        logger.info("🚀 INICIANDO SETUP COMPLETO DO SISTEMA")
        logger.info("=" * 60)
        logger.info("Este script irá configurar:")
        logger.info("✅ Supabase (banco de dados)")
        logger.info("✅ Z-API (WhatsApp)")
        logger.info("✅ Webhook (recebimento de mensagens)")
        logger.info("✅ Testes de conexão")
        logger.info("✅ Arquivos de configuração")
        logger.info("=" * 60)
        
        # Verificar requisitos
        if not self.check_requirements():
            logger.error("❌ Setup interrompido - requisitos não atendidos")
            return False
        
        # Executar setups
        self.setup_results = {
            "supabase": await self.run_supabase_setup(),
            "webhook": await self.run_webhook_setup(),
            "connections": await self.run_connection_tests()
        }
        
        # Criar arquivos de configuração
        self.create_deployment_guide()
        self.create_vercel_env_file()
        
        # Relatório final
        self.print_final_report()
        
        return True
    
    def print_final_report(self):
        """Imprime relatório final"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 RELATÓRIO FINAL DO SETUP")
        logger.info("=" * 60)
        
        success_count = sum(self.setup_results.values())
        total_count = len(self.setup_results)
        
        for service, status in self.setup_results.items():
            icon = "✅" if status else "❌"
            logger.info(f"{icon} {service.upper()}: {'CONCLUÍDO' if status else 'FALHOU'}")
        
        logger.info("=" * 60)
        logger.info(f"📈 RESULTADO: {success_count}/{total_count} setups funcionando")
        
        if success_count == total_count:
            logger.info("🎉 SETUP COMPLETO CONCLUÍDO COM SUCESSO!")
            logger.info("")
            logger.info("📝 PRÓXIMOS PASSOS:")
            logger.info("1. Configure as variáveis no Vercel usando vercel_env_vars.json")
            logger.info("2. Faça o deploy da aplicação")
            logger.info("3. Teste o sistema completo")
            logger.info("4. Monitore os logs")
        elif success_count >= total_count * 0.7:
            logger.info("⚠️ A maioria dos setups foi concluída")
            logger.info("Verifique os erros e tente novamente")
        else:
            logger.info("❌ Muitos setups falharam")
            logger.info("Verifique as configurações e tente novamente")
        
        logger.info("=" * 60)
        logger.info("📚 ARQUIVOS CRIADOS:")
        logger.info("   - DEPLOYMENT_GUIDE.md (guia completo)")
        logger.info("   - vercel_env_vars.json (variáveis do Vercel)")
        logger.info("   - .env (configurações locais)")
        logger.info("=" * 60)

async def main():
    """Função principal"""
    setup = CompleteSystemSetup()
    await setup.run_complete_setup()

if __name__ == "__main__":
    asyncio.run(main()) 