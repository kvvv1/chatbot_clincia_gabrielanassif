#!/usr/bin/env python3
"""
TESTE SERVIÇO WHATSAPP
Testa se o serviço do WhatsApp está funcionando corretamente
"""

import asyncio
import logging
from app.services.whatsapp import WhatsAppService
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_whatsapp_service():
    """Testa o serviço do WhatsApp"""
    try:
        logger.info("🧪 Testando serviço do WhatsApp...")
        
        # Verificar configurações
        logger.info(f"📡 Base URL: {settings.zapi_base_url}")
        logger.info(f"🆔 Instance ID: {settings.zapi_instance_id}")
        logger.info(f"🔑 Token: {'Configurado' if settings.zapi_token else 'Não configurado'}")
        logger.info(f"🔐 Client Token: {'Configurado' if settings.zapi_client_token else 'Não configurado'}")
        
        # Criar instância do serviço
        whatsapp = WhatsAppService()
        
        # Testar envio de mensagem
        test_phone = "5531999999999"
        test_message = "Teste do serviço WhatsApp - " + str(asyncio.get_event_loop().time())
        
        logger.info(f"📱 Enviando mensagem para {test_phone}")
        logger.info(f"💬 Mensagem: {test_message}")
        
        result = await whatsapp.send_text(test_phone, test_message)
        
        if result:
            logger.info("✅ Mensagem enviada com sucesso!")
            logger.info(f"📊 Resultado: {result}")
            return True
        else:
            logger.error("❌ Falha ao enviar mensagem")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False

async def main():
    """Função principal"""
    sucesso = await test_whatsapp_service()
    
    if sucesso:
        logger.info("🎉 Teste do WhatsApp concluído com sucesso!")
    else:
        logger.error("💥 Teste do WhatsApp falhou!")

if __name__ == "__main__":
    asyncio.run(main()) 