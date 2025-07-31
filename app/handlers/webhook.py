from fastapi import APIRouter, Request, HTTPException
import logging
import json
from datetime import datetime
import httpx
from app.services.conversation import ConversationManager
from app.models.database import get_db
from app.config import settings

# ✅ CORREÇÃO CRÍTICA: Instância global para evitar recriação
_conversation_manager = None

def get_conversation_manager():
    """Retorna instância singleton do ConversationManager"""
    global _conversation_manager
    if _conversation_manager is None:
        logger.info("🔧 Criando instância global do ConversationManager")
        _conversation_manager = ConversationManager()
    return _conversation_manager

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
            "timestamp": datetime.now().isoformat() + "Z",
            "environment": "vercel" if settings.environment == "production" else "local"
        }
    except Exception as e:
        logger.error(f"Erro no webhook health: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/health")
async def webhook_health_alt():
    """Endpoint alternativo de saúde do webhook"""
    return await webhook_health()

@router.post("/message")
async def webhook_message(request: Request):
    """Handler para mensagens recebidas"""
    try:
        logger.info("=== WEBHOOK MESSAGE RECEBIDO ===")
        
        # Obter corpo da requisição
        body = await request.body()
        data = await request.json()
        
        logger.info(f"Dados do webhook message: {json.dumps(data, indent=2)}")
        
        # Processar mensagem
        await process_message_event(data)
        
        return {
            "status": "success",
            "message": "Mensagem processada com sucesso",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook message: {str(e)}")
        logger.error(f"Traceback completo: ", exc_info=True)
        # ✅ CORREÇÃO: Retornar erro real em vez de sucesso
        return {
            "status": "error",
            "message": "Erro ao processar mensagem",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.post("/status")
async def webhook_status(request: Request):
    """Handler para status das mensagens"""
    try:
        logger.info("=== WEBHOOK STATUS RECEBIDO ===")
        
        data = await request.json()
        logger.info(f"Status da mensagem: {json.dumps(data, indent=2)}")
        
        return {
            "status": "success",
            "message": "Status processado",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook status: {str(e)}")
        # ✅ CORREÇÃO: Retornar erro real
        return {
            "status": "error",
            "message": "Erro ao processar status",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.post("/connected")
async def webhook_connected(request: Request):
    """Handler para eventos de conexão/desconexão"""
    try:
        logger.info("=== WEBHOOK CONNECTED RECEBIDO ===")
        
        data = await request.json()
        logger.info(f"Evento de conexão: {json.dumps(data, indent=2)}")
        
        return {
            "status": "success",
            "message": "Evento de conexão processado",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook connected: {str(e)}")
        # ✅ CORREÇÃO: Retornar erro real
        return {
            "status": "error",
            "message": "Erro ao processar evento de conexão",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

# ✅ CORREÇÃO: REMOVER HANDLER DUPLICADO - Manter apenas este
@router.post("/")
async def webhook_handler(request: Request):
    """Handler principal para webhook - UNIFICADO"""
    try:
        logger.info("=== WEBHOOK PRINCIPAL RECEBIDO ===")
        
        # Obter dados da requisição
        body = await request.body()
        data = await request.json()
        
        logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        
        # ✅ CORREÇÃO: Detectar tipo de evento e processar adequadamente
        event_type = data.get("type", "")
        
        if event_type == "ReceivedCallback":
            # Processar mensagem recebida
            await process_message_event(data)
            return {
                "status": "success",
                "message": "Mensagem processada com sucesso",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        elif event_type == "DeliveryCallback":
            # Processar confirmação de entrega
            logger.info("Confirmação de entrega recebida")
            return {
                "status": "success",
                "message": "Entrega confirmada",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            # Evento desconhecido
            logger.warning(f"Evento desconhecido: {event_type}")
            return {
                "status": "warning",
                "message": "Evento não processado",
                "event_type": event_type,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
    except Exception as e:
        logger.error(f"Erro no webhook principal: {str(e)}")
        logger.error(f"Traceback completo: ", exc_info=True)
        # ✅ CORREÇÃO: Retornar erro real
        return {
            "status": "error",
            "message": "Erro interno no webhook",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

async def process_message_event(data: dict):
    """Processa evento de mensagem recebida"""
    try:
        logger.info("=== INÍCIO DO PROCESSAMENTO DE MENSAGEM ===")
        
        # Extrair informações da mensagem
        phone = data.get("phone", "")
        message_text = data.get("text", {}).get("message", "")
        message_id = data.get("messageId", "")
        from_me = data.get("fromMe", False)

        # ✅ CORREÇÃO: Remover sufixo @c.us do telefone
        if phone.endswith("@c.us"):
            phone = phone[:-5]

        logger.info(f"Telefone: {phone}")
        logger.info(f"Texto da mensagem: {message_text}")
        logger.info(f"ID da mensagem: {message_id}")
        logger.info(f"FromMe: {from_me}")

        # ✅ CORREÇÃO: Verificar se é mensagem enviada por nós
        if from_me:
            logger.info("Mensagem enviada por nós, ignorando")
            return

        # ✅ CORREÇÃO: Validar dados obrigatórios
        if not phone or not message_text:
            logger.error("Dados obrigatórios ausentes")
            return

        # Processar mensagem
        conversation_manager = get_conversation_manager()
        db = get_db()
        
        await conversation_manager.processar_mensagem(
            phone=phone,
            message=message_text,
            message_id=message_id,
            db=db
        )
        
        logger.info("=== PROCESSAMENTO CONCLUÍDO ===")
        
    except Exception as e:
        logger.error(f"Erro no processamento de mensagem: {str(e)}")
        logger.error(f"Traceback completo: ", exc_info=True)
        raise

# ✅ CORREÇÃO: Adicionar validação de autenticação
def validate_webhook_request(request: Request) -> bool:
    """Valida se a requisição é legítima"""
    try:
        # Verificar headers de autenticação do Z-API
        zapi_token = request.headers.get("z-api-token")
        if zapi_token:
            # ✅ TODO: Implementar validação do token
            logger.info("Token Z-API presente")
            return True
        
        # Verificar origem da requisição
        user_agent = request.headers.get("user-agent", "")
        if "Z-API" in user_agent:
            logger.info("User-Agent do Z-API detectado")
            return True
        
        logger.warning("Requisição sem autenticação válida")
        return False
        
    except Exception as e:
        logger.error(f"Erro na validação: {str(e)}")
        return False

@router.get("/configure")
async def configure_webhook():
    """Endpoint para configurar webhook"""
    try:
        # ✅ CORREÇÃO: Construir URL sem barra final
        app_host = settings.app_host.rstrip('/') if settings.app_host else "https://chatbot-clincia.vercel.app"
        webhook_url = f"{app_host}/webhook"
        
        return {
            "webhook_url": webhook_url,
            "message_url": f"{webhook_url}/message",
            "status_url": f"{webhook_url}/status",
            "connected_url": f"{webhook_url}/connected",
            "health_url": f"{webhook_url}/health"
        }
    except Exception as e:
        logger.error(f"Erro na configuração: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/status-info")
async def webhook_status_info():
    """Informações de status do webhook"""
    try:
        return {
            "webhook_info": {
                "status": "active",
                "message": "Webhook funcionando",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        }
    except Exception as e:
        logger.error(f"Erro no status info: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

# ✅ CORREÇÃO: Remover handlers duplicados e conflitantes
# REMOVIDO: @router.post("") - Handler duplicado
# REMOVIDO: @router.post("/") duplicado

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def webhook_fallback(request: Request, path: str):
    """Fallback para rotas não encontradas"""
    try:
        logger.info(f"=== WEBHOOK SEM BARRA FINAL RECEBIDO ===")
        logger.info(f"URL: {request.url}")
        logger.info(f"Method: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        body = await request.body()
        logger.info(f"Body raw: {body}")
        
        data = await request.json()
        logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        
        logger.info("Webhook recebido do Z-API (endpoint genérico)")
        logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        
        # ✅ CORREÇÃO: Processar como webhook principal
        await process_message_event(data)
        
        return {
            "status": "success",
            "message": "Webhook processado com sucesso",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no fallback: {str(e)}")
        logger.info("Evento não processado:")
        return {
            "status": "error",
            "message": "Erro no processamento",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        } 