from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.conversation import ConversationManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

conversation_manager = ConversationManager()

@router.post("/webhook/message")
async def webhook_message(request: Request, db: Session = Depends(get_db)):
    """Recebe mensagens do WhatsApp via Z-API"""
    try:
        data = await request.json()

        # Log para debug
        logger.info(f"Webhook recebido: {data}")

        # Extrair dados da mensagem
        if data.get("type") == "ReceivedCallback":
            phone = data.get("phone", "").replace("@c.us", "")

            # Verificar se é mensagem de texto
            text_data = data.get("text", {})
            if text_data and "message" in text_data:
                message = text_data["message"]
                message_id = data.get("messageId", "")

                # Processar mensagem
                await conversation_manager.processar_mensagem(
                    phone, message, message_id, db
                )

                return {"status": "success"}

        return {"status": "ignored", "reason": "not_text_message"}

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/status")
async def webhook_status(request: Request):
    """Recebe atualizações de status das mensagens"""
    try:
        data = await request.json()

        # Log status para monitoramento
        logger.info(f"Status update: {data}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Erro no webhook status: {str(e)}")
        return {"status": "error"}

@router.post("/webhook/connected")
async def webhook_connected(request: Request):
    """Notificação quando WhatsApp conecta/desconecta"""
    try:
        data = await request.json()

        connected = data.get("connected", False)

        if connected:
            logger.info("WhatsApp conectado com sucesso!")
        else:
            logger.warning("WhatsApp desconectado!")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Erro no webhook connected: {str(e)}")
        return {"status": "error"} 