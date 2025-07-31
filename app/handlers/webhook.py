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
        return {
            "status": "success",
            "message": "Mensagem processada",
            "error": str(e)
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
        return {
            "status": "success",
            "message": "Status processado",
            "error": str(e)
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
        return {
            "status": "success",
            "message": "Evento processado",
            "error": str(e)
        }

# Endpoint de fallback para compatibilidade
@router.post("")
async def webhook_handler_no_slash(request: Request):
    """Handler para webhook sem barra final - compatibilidade com Z-API"""
    try:
        logger.info("=== WEBHOOK SEM BARRA FINAL RECEBIDO ===")
        logger.info(f"URL: {request.url}")
        logger.info(f"Method: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Obter corpo da requisição
        body = await request.body()
        logger.info(f"Body raw: {body}")
        
        try:
            data = await request.json()
            logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        except Exception as json_error:
            logger.error(f"Erro ao parsear JSON: {str(json_error)}")
            logger.error(f"Body recebido: {body}")
            return {
                "status": "success",
                "message": "Webhook recebido (erro no JSON)",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
        return await webhook_handler(request)
        
    except Exception as e:
        logger.error(f"Erro no webhook sem barra: {str(e)}")
        return {
            "status": "success",
            "message": "Webhook processado",
            "error": str(e)
        }

@router.post("/")
async def webhook_handler(request: Request):
    """Handler principal do webhook - Processa eventos do Z-API"""
    try:
        logger.info("Webhook recebido do Z-API (endpoint genérico)")
        
        data = await request.json()
        logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        
        # Verificar tipo de evento
        event_type = data.get("event", "")
        
        if event_type == "message":
            await process_message_event(data)
        elif event_type in ["connection", "disconnection"]:
            logger.info(f"Evento de {event_type}: {data}")
        else:
            logger.info(f"Evento não processado: {event_type}")
        
        return {
            "status": "success",
            "message": "Webhook processado com sucesso",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook handler: {str(e)}")
        return {
            "status": "success",
            "message": "Webhook processado",
            "error": str(e)
        }

async def process_message_event(data: dict):
    """Processa evento de mensagem recebida"""
    try:
        logger.info("=== INÍCIO DO PROCESSAMENTO DE MENSAGEM ===")
        
        # Verificar se é um ReceivedCallback (formato Z-API)
        if data.get("type") == "ReceivedCallback":
            logger.info("Processando ReceivedCallback do Z-API")
            
            # Extrair informações da mensagem
            phone = data.get("phone", "")
            message_text = data.get("text", {}).get("message", "")
            message_id = data.get("messageId", "")
            from_me = data.get("fromMe", False)
            
            # Remover sufixo @c.us do telefone
            if phone.endswith("@c.us"):
                phone = phone[:-5]
            
            logger.info(f"Telefone: {phone}")
            logger.info(f"Texto da mensagem: {message_text}")
            logger.info(f"ID da mensagem: {message_id}")
            logger.info(f"FromMe: {from_me}")
            
            # Verificar se não é uma mensagem enviada por nós
            if from_me:
                logger.info("Mensagem enviada por nós, ignorando")
                return
            
            # Verificar se é uma mensagem de texto
            if not message_text:
                logger.info("Mensagem sem texto, ignorando")
                return
            
            logger.info("Iniciando processamento com ConversationManager...")
            
            # Processar mensagem com o ConversationManager
            db = get_db()
            conversation_manager = get_conversation_manager()
            
            logger.info("Chamando processar_mensagem...")
            await conversation_manager.processar_mensagem(
                phone=phone,
                message=message_text,
                message_id=message_id,
                db=db
            )
            
            logger.info(f"Mensagem processada com sucesso: {phone}")
            logger.info("=== FIM DO PROCESSAMENTO DE MENSAGEM ===")
            
        else:
            # Formato antigo (compatibilidade)
            logger.info("Processando formato antigo")
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
            db = get_db()
            conversation_manager = get_conversation_manager()
            
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

@router.get("/status-info")
async def webhook_status_info():
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
            "webhook_url": f"https://{settings.app_host}/webhook",
            "environment": "vercel" if settings.environment == "production" else "local"
        }
    except Exception as e:
        logger.error(f"Erro no webhook test: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/test-message")
async def test_message():
    """Endpoint para testar envio de mensagem"""
    try:
        # Simular processamento de mensagem
        return {
            "status": "success",
            "message": "Mensagem de teste processada",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro no test message: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def webhook_fallback(request: Request, path: str):
    """Endpoint de fallback para capturar rotas não mapeadas"""
    method = request.method
    logger.warning(f"Rota não mapeada: {method} /webhook/{path}")
    
    try:
        # Tentar obter dados da requisição
        body = await request.body()
        data = {}
        
        if body:
            try:
                data = await request.json()
            except:
                data = {"raw_body": body.decode()}
        
        logger.info(f"Dados da requisição: {json.dumps(data, indent=2)}")
        
        # Retornar resposta genérica
        return {
            "status": "warning",
            "message": f"Rota /webhook/{path} não mapeada",
            "method": method,
            "data_received": data,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no fallback: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao processar requisição para /webhook/{path}",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        } 