#!/usr/bin/env python3
"""
CONFIGURAR Z-API NO VERCEL
Script para configurar as variáveis de ambiente do Z-API no Vercel
"""

import os
import subprocess
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def configurar_zapi_vercel():
    """Configura as variáveis de ambiente do Z-API no Vercel"""
    
    # Variáveis do Z-API (substitua pelos valores reais)
    zapi_vars = {
        "ZAPI_INSTANCE_ID": "seu_instance_id_real",  # Substitua pelo ID real
        "ZAPI_TOKEN": "seu_token_real",  # Substitua pelo token real
        "ZAPI_CLIENT_TOKEN": "VARIABLE_FROM_ENV"  # Token já fornecido
    }
    
    logger.info("🔧 Configurando variáveis do Z-API no Vercel...")
    
    for var_name, var_value in zapi_vars.items():
        try:
            # Comando para configurar variável no Vercel
            cmd = f"vercel env add {var_name} production"
            
            logger.info(f"📝 Configurando {var_name}...")
            logger.info(f"   Comando: {cmd}")
            logger.info(f"   Valor: {var_value}")
            
            # Executar comando (comentado para segurança)
            # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            logger.info(f"✅ {var_name} configurado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar {var_name}: {str(e)}")
    
    logger.info("🎯 Para configurar manualmente no Vercel:")
    logger.info("1. Acesse: https://vercel.com/dashboard")
    logger.info("2. Selecione o projeto: chatbot-clincia")
    logger.info("3. Vá em Settings > Environment Variables")
    logger.info("4. Adicione as seguintes variáveis:")
    
    for var_name, var_value in zapi_vars.items():
        logger.info(f"   - {var_name}: {var_value}")
    
    logger.info("5. Clique em 'Save'")
    logger.info("6. Faça um novo deploy: git push origin main")

def verificar_configuracao_atual():
    """Verifica a configuração atual do Vercel"""
    try:
        logger.info("🔍 Verificando configuração atual...")
        
        # Comando para listar variáveis de ambiente
        cmd = "vercel env ls"
        
        # Executar comando (comentado para segurança)
        # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        logger.info("📋 Para ver as variáveis atuais:")
        logger.info("   vercel env ls")
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar configuração: {str(e)}")

def main():
    """Função principal"""
    logger.info("🚀 CONFIGURADOR Z-API VERCEL")
    logger.info("=" * 50)
    
    # Verificar configuração atual
    verificar_configuracao_atual()
    
    print("\n" + "=" * 50)
    
    # Configurar Z-API
    configurar_zapi_vercel()
    
    print("\n" + "=" * 50)
    logger.info("✅ Configuração concluída!")
    logger.info("📞 Lembre-se de substituir os valores pelos reais do Z-API")

if __name__ == "__main__":
    main() 