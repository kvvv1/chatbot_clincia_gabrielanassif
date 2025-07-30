from fastapi import APIRouter, Request, HTTPException
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def webhook_health():
    """Endpoint de saúde do webhook"""
    try:
        return {
            "status": "ok",
            "message": "Webhook endpoint funcionando",
            "service": "WhatsApp Webhook"
        }
    except Exception as e:
        logger.error(f"Erro no webhook health: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/")
async def webhook_handler(request: Request):
    """Handler principal do webhook"""
    try:
        # Log da requisição
        logger.info("Webhook recebido")
        
        # Para desenvolvimento, retornar sucesso
        return {
            "status": "success",
            "message": "Webhook processado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro no webhook handler: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/test")
async def webhook_test():
    """Endpoint de teste do webhook"""
    try:
        return {
            "status": "ok",
            "message": "Webhook test funcionando",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro no webhook test: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno") 