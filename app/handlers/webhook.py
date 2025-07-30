from fastapi import APIRouter, Request, HTTPException
import logging
import json
from datetime import datetime
import httpx
from app.services.conversation import ConversationManager
from app.models.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def webhook_health():
    """Endpoint de saúde do webhook"""
    try:
        return {
            "status": "ok",
            "message": "Webhook endpoint funcionando",
            "service": "WhatsApp Webhook",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro no webhook health: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/health")
async def webhook_health_alt():
    """Endpoint alternativo de saúde do webhook"""
    return await webhook_health()

@router.post("/")
async def webhook_handler(request: Request):
    """Handler principal do webhook - Processa eventos do Z-API"""
    try:
        # Log da requisição
        logger.info("Webhook recebido do Z-API")
        
        # Obter corpo da requisição
        body = await request.body()
        data = await request.json()
        
        logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        
        # Verificar se é um evento de mensagem
        if data.get("event") == "message":
            await process_message_event(data)
        elif data.get("event") == "connection":
            logger.info(f"Evento de conexão: {data}")
        elif data.get("event") == "disconnection":
            logger.info(f"Evento de desconexão: {data}")
        else:
            logger.info(f"Evento não processado: {data.get('event')}")
        
        # Sempre retornar sucesso para o Z-API
        return {
            "status": "success",
            "message": "Webhook processado com sucesso",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook handler: {str(e)}")
        # Mesmo com erro, retornar sucesso para não quebrar o webhook
        return {
            "status": "success",
            "message": "Webhook processado",
            "error": str(e)
        }

async def process_message_event(data: dict):
    """Processa evento de mensagem recebida"""
    try:
        logger.info("=== INÍCIO DO PROCESSAMENTO DE MENSAGEM ===")
        
        # Extrair dados da mensagem
        message_data = data.get("data", {})
        logger.info(f"Dados da mensagem: {json.dumps(message_data, indent=2)}")
        
        # Verificar se é uma mensagem de texto
        if message_data.get("type") != "text":
            logger.info(f"Mensagem não é texto: {message_data.get('type')}")
            return
        
        # Extrair informações da mensagem
        phone = message_data.get("from", "")
        message_text = message_data.get("text", {}).get("body", "")
        message_id = message_data.get("id", "")
        
        # Remover sufixo @c.us do telefone
        if phone.endswith("@c.us"):
            phone = phone[:-5]
        
        logger.info(f"Telefone: {phone}")
        logger.info(f"Texto da mensagem: {message_text}")
        logger.info(f"ID da mensagem: {message_id}")
        
        # Verificar se não é uma mensagem enviada por nós
        if message_data.get("fromMe", False):
            logger.info("Mensagem enviada por nós, ignorando")
            return
        
        logger.info("Iniciando processamento com ConversationManager...")
        
        # Processar mensagem com o ConversationManager
        db = next(get_db())
        conversation_manager = ConversationManager()
        
        logger.info("Chamando processar_mensagem...")
        await conversation_manager.processar_mensagem(
            phone=phone,
            message=message_text,
            message_id=message_id,
            db=db
        )
        
        logger.info(f"Mensagem processada com sucesso: {phone}")
        logger.info("=== FIM DO PROCESSAMENTO DE MENSAGEM ===")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        logger.error(f"Traceback completo: ", exc_info=True)

@router.get("/configure")
async def configure_webhook():
    """Configura o webhook no Z-API"""
    try:
        webhook_url = f"https://{settings.app_host}/webhook"
        
        # Configurar webhook no Z-API
        success = await set_zapi_webhook(webhook_url)
        
        if success:
            return {
                "status": "success",
                "message": "Webhook configurado com sucesso",
                "webhook_url": webhook_url,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao configurar webhook no Z-API")
            
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/status")
async def webhook_status():
    """Verifica o status do webhook no Z-API"""
    try:
        webhook_info = await get_zapi_webhook_status()
        
        return {
            "status": "success",
            "webhook_info": webhook_info,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar status do webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

async def set_zapi_webhook(webhook_url: str) -> bool:
    """Configura webhook no Z-API"""
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        payload = {
            "webhook": webhook_url,
            "webhookByEvents": True,
            "webhookBase64": False
        }
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/webhook",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook configurado: {webhook_url}")
                return True
            else:
                logger.error(f"Erro ao configurar webhook: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Erro na comunicação com Z-API: {str(e)}")
        return False

async def get_zapi_webhook_status() -> dict:
    """Obtém informações do webhook configurado no Z-API"""
    try:
        base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        
        headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/webhook",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter status do webhook: {response.text}")
                return {"error": "Erro ao obter status"}
                
    except Exception as e:
        logger.error(f"Erro na comunicação com Z-API: {str(e)}")
        return {"error": str(e)}

@router.get("/test")
async def webhook_test():
    """Endpoint de teste do webhook"""
    try:
        return {
            "status": "ok",
            "message": "Webhook test funcionando",
            "timestamp": datetime.now().isoformat() + "Z",
            "webhook_url": f"https://{settings.app_host}/webhook"
        }
    except Exception as e:
        logger.error(f"Erro no webhook test: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/test-message")
async def test_message():
    """Endpoint para testar processamento de mensagem"""
    try:
        # Simular uma mensagem de teste
        test_data = {
            "event": "message",
            "data": {
                "id": "test_123",
                "type": "text",
                "from": "553198600366@c.us",
                "fromMe": False,
                "text": {
                    "body": "1"
                }
            }
        }
        
        await process_message_event(test_data)
        
        return {
            "status": "success",
            "message": "Mensagem de teste processada",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno") 