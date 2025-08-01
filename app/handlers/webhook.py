from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# 🔧 CORREÇÃO CRÍTICA: Instância global singleton
_conversation_manager: Optional[object] = None

def get_conversation_manager():
    """Retorna instância singleton do ConversationManager"""
    global _conversation_manager
    if _conversation_manager is None:
        try:
            logger.info("🔧 Criando instância global do ConversationManager")
            from app.services.conversation import ConversationManager
            _conversation_manager = ConversationManager()
            logger.info("✅ ConversationManager criado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao criar ConversationManager: {str(e)}")
            raise
    return _conversation_manager

@router.get("/")
async def webhook_health():
    """Endpoint de saúde do webhook"""
    try:
        return {
            "status": "ok",
            "message": "Webhook endpoint funcionando",
            "service": "WhatsApp Webhook",
            "timestamp": datetime.now().isoformat() + "Z",
            "environment": settings.environment,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"❌ Erro no webhook health: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/health")
async def webhook_health_check():
    """Health check detalhado do webhook"""
    try:
        # Verificar ConversationManager
        manager_status = "healthy"
        try:
            manager = get_conversation_manager()
            manager_status = "healthy" if manager else "unhealthy"
        except Exception as e:
            manager_status = f"error: {str(e)}"
        
        return {
            "status": "healthy" if manager_status == "healthy" else "degraded",
            "webhook": "active",
            "conversation_manager": manager_status,
            "environment": settings.environment,
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.post("/message")
async def webhook_message(request: Request, db: Session = Depends(get_db)):
    """Handler principal para mensagens recebidas"""
    try:
        logger.info("=== WEBHOOK MESSAGE RECEBIDO ===")
        
        # Obter dados da requisição
        try:
            data = await request.json()
            logger.info(f"Dados do webhook message: {json.dumps(data, indent=2)}")
        except Exception as json_error:
            logger.error(f"❌ Erro ao parsear JSON: {json_error}")
            raise HTTPException(status_code=400, detail="JSON inválido")
        
        # Validar dados básicos
        if not _validate_webhook_data(data):
            logger.warning("❌ Dados do webhook inválidos")
            raise HTTPException(status_code=400, detail="Dados do webhook inválidos")
        
        # Processar mensagem com timeout
        try:
            await asyncio.wait_for(
                process_message_event(data, db),
                timeout=30.0
            )
            
            return {
                "status": "success",
                "message": "Mensagem processada com sucesso",
                "timestamp": datetime.now().isoformat() + "Z"
            }
            
        except asyncio.TimeoutError:
            logger.error("❌ Timeout no processamento da mensagem")
            return {
                "status": "timeout",
                "message": "Processamento demorou mais que 30 segundos",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro crítico no webhook message: {str(e)}")
        logger.exception("Stack trace completo:")
        
        if settings.is_production():
            return {
                "status": "error",
                "message": "Erro interno do servidor",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            return {
                "status": "error",
                "message": "Erro ao processar mensagem",
                "error": str(e),
                "timestamp": datetime.now().isoformat() + "Z"
            }

@router.post("/status")
async def webhook_status(request: Request):
    """Handler para status das mensagens (entregue, lido, etc.)"""
    try:
        logger.info("=== WEBHOOK STATUS RECEBIDO ===")
        
        data = await request.json()
        logger.debug(f"Status da mensagem: {json.dumps(data, indent=2)}")
        
        # Por enquanto, apenas loggar o status
        message_id = data.get("messageId", "")
        status = data.get("status", "")
        phone = data.get("phone", "")
        
        logger.info(f"📱 Status update - Phone: {phone}, Message: {message_id}, Status: {status}")
        
        return {
            "status": "success",
            "message": "Status processado",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook status: {str(e)}")
        return {
            "status": "error",
            "message": "Erro ao processar status",
            "error": str(e) if not settings.is_production() else "Erro interno",
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
        logger.error(f"❌ Erro no webhook connected: {str(e)}")
        return {
            "status": "error",
            "message": "Erro ao processar evento de conexão",
            "error": str(e) if not settings.is_production() else "Erro interno",
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.post("/")
async def webhook_handler_root(request: Request, db: Session = Depends(get_db)):
    """Handler principal para webhook - endpoint raiz"""
    try:
        logger.info("=== WEBHOOK PRINCIPAL RECEBIDO ===")
        
        # Obter dados da requisição
        try:
            data = await request.json()
            logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
        except Exception as json_error:
            logger.error(f"❌ Erro ao parsear JSON: {json_error}")
            raise HTTPException(status_code=400, detail="JSON inválido")
        
        # Detectar tipo de evento e processar adequadamente
        event_type = data.get("type", "")
        
        if event_type == "ReceivedCallback":
            # Processar mensagem recebida
            try:
                await asyncio.wait_for(
                    process_message_event(data, db),
                    timeout=30.0
                )
                return {
                    "status": "success",
                    "message": "Mensagem processada com sucesso",
                    "event_type": event_type,
                    "timestamp": datetime.now().isoformat() + "Z"
                }
            except asyncio.TimeoutError:
                return {
                    "status": "timeout",
                    "message": "Processamento demorou mais que 30 segundos",
                    "timestamp": datetime.now().isoformat() + "Z"
                }
        elif event_type == "DeliveryCallback":
            # Processar confirmação de entrega
            logger.info("📬 Confirmação de entrega recebida")
            return {
                "status": "success",
                "message": "Entrega confirmada",
                "event_type": event_type,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            # Evento desconhecido
            logger.warning(f"⚠️ Evento desconhecido: {event_type}")
            return {
                "status": "warning",
                "message": "Evento não processado",
                "event_type": event_type,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro crítico no webhook principal: {str(e)}")
        logger.exception("Stack trace completo:")
        
        if settings.is_production():
            return {
                "status": "error",
                "message": "Erro interno do servidor",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            return {
                "status": "error",
                "message": "Erro interno no webhook",
                "error": str(e),
                "timestamp": datetime.now().isoformat() + "Z"
            }

async def process_message_event(data: dict, db: Session):
    """Processa evento de mensagem recebida"""
    try:
        logger.info("=== INÍCIO DO PROCESSAMENTO DE MENSAGEM ===")
        
        # Extrair informações da mensagem
        phone = data.get("phone", "")
        message_text = data.get("text", {}).get("message", "")
        message_id = data.get("messageId", "")
        from_me = data.get("fromMe", False)

        # Sanitizar telefone
        phone = _sanitize_phone(phone)
        
        logger.info(f"Telefone: {phone}")
        logger.info(f"Texto da mensagem: {message_text}")
        logger.info(f"ID da mensagem: {message_id}")
        logger.info(f"FromMe: {from_me}")

        # Verificar se é mensagem enviada por nós
        if from_me:
            logger.info("⬅️ Mensagem enviada por nós, ignorando")
            return

        # Validar dados obrigatórios
        if not phone:
            logger.error("❌ Telefone ausente")
            return
            
        # Se não há texto da mensagem, pode ser um callback de status
        if not message_text:
            logger.info("ℹ️ Mensagem sem texto (callback de status), ignorando")
            return

        # Sanitizar mensagem
        message_text = _sanitize_message(message_text)
        
        # Verificar se mensagem não está vazia após sanitização
        if not message_text.strip():
            logger.info("ℹ️ Mensagem vazia após sanitização, ignorando")
            return

        # Processar mensagem
        conversation_manager = get_conversation_manager()
        
        # 🔧 CORREÇÃO CRÍTICA: Passar db corretamente
        await conversation_manager.processar_mensagem(
            phone=phone,
            message=message_text,
            message_id=message_id,
            db=db
        )
        
        logger.info("=== PROCESSAMENTO CONCLUÍDO ===")
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento de mensagem: {str(e)}")
        logger.exception("Stack trace completo:")
        raise

def _validate_webhook_data(webhook_data: Dict[str, Any]) -> bool:
    """Valida estrutura básica dos dados do webhook"""
    try:
        # Verificações básicas
        if not isinstance(webhook_data, dict):
            logger.warning("❌ Webhook data não é um dict")
            return False
        
        # Campos obrigatórios para mensagem
        required_fields = ["phone", "messageId", "fromMe"]
        for field in required_fields:
            if field not in webhook_data:
                logger.warning(f"❌ Campo obrigatório ausente: {field}")
                return False
        
        # Verificar se tem conteúdo de texto (opcional para alguns tipos)
        text_data = webhook_data.get("text", {})
        if webhook_data.get("type") == "ReceivedCallback":
            if not isinstance(text_data, dict) or "message" not in text_data:
                logger.warning("❌ Campo 'text.message' ausente para ReceivedCallback")
                return False
        
        # Verificar tipos básicos
        if not isinstance(webhook_data.get("phone"), str):
            logger.warning("❌ Campo 'phone' não é string")
            return False
        
        if not isinstance(webhook_data.get("fromMe"), bool):
            logger.warning("❌ Campo 'fromMe' não é boolean")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na validação do webhook: {str(e)}")
        return False

def _sanitize_phone(phone: str) -> str:
    """Sanitiza número de telefone"""
    if not phone:
        return ""
    
    # Remover sufixo @c.us se presente
    if phone.endswith("@c.us"):
        phone = phone[:-5]
    
    # Remover outros sufixos comuns
    if phone.endswith("@lid"):
        phone = phone[:-4]
    
    # Remove caracteres não numéricos
    phone_clean = ''.join(filter(str.isdigit, phone))
    
    # Adiciona código do país se necessário (Brasil)
    if len(phone_clean) == 11 and phone_clean.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
        phone_clean = '55' + phone_clean
    
    return phone_clean

def _sanitize_message(message: str) -> str:
    """Sanitiza texto da mensagem"""
    if not message:
        return ""
    
    # Remove caracteres de controle (exceto quebras de linha e tabs)
    message_clean = ''.join(char for char in message if ord(char) >= 32 or char in ['\n', '\t'])
    
    # Remove espaços extras
    message_clean = ' '.join(message_clean.split())
    
    # Limitar tamanho da mensagem
    if len(message_clean) > 1000:
        logger.warning(f"⚠️ Mensagem muito longa ({len(message_clean)} chars), truncando")
        message_clean = message_clean[:1000]
    
    return message_clean.strip()

@router.get("/configure")
async def configure_webhook():
    """Endpoint para configurar webhook"""
    try:
        app_host = settings.app_host.rstrip('/') if settings.app_host else "https://chatbot-clincia.vercel.app"
        webhook_url = f"{app_host}/webhook"
        
        return {
            "webhook_configuration": {
                "base_url": webhook_url,
                "endpoints": {
                    "main": f"{webhook_url}/",
                    "message": f"{webhook_url}/message",
                    "status": f"{webhook_url}/status",
                    "connected": f"{webhook_url}/connected",
                    "health": f"{webhook_url}/health"
                }
            },
            "instructions": {
                "zapi": "Configure no Z-API o webhook para: " + webhook_url,
                "events": ["ReceivedCallback", "DeliveryCallback", "ConnectedCallback"]
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro na configuração: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/status-info")
async def webhook_status_info():
    """Informações de status do webhook"""
    try:
        # Verificar status dos componentes
        manager_status = "unknown"
        try:
            manager = get_conversation_manager()
            manager_status = "active" if manager else "inactive"
        except Exception:
            manager_status = "error"
        
        return {
            "webhook_info": {
                "status": "active",
                "conversation_manager": manager_status,
                "environment": settings.environment,
                "timestamp": datetime.now().isoformat() + "Z",
                "version": "2.0.0"
            },
            "endpoints": {
                "health": "/webhook/health",
                "message": "/webhook/message",
                "status": "/webhook/status",
                "configure": "/webhook/configure"
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro no status info: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

# Fallback para rotas não encontradas (compatibilidade)
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def webhook_fallback(request: Request, path: str, db: Session = Depends(get_db)):
    """Fallback para rotas não encontradas"""
    try:
        logger.info(f"=== WEBHOOK FALLBACK CHAMADO ===")
        logger.info(f"Path: /{path}")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        
        if request.method == "POST":
            try:
                data = await request.json()
                logger.info(f"Data: {json.dumps(data, indent=2)}")
                
                # Se é um evento de mensagem, processar
                event_type = data.get("type", "")
                if event_type == "ReceivedCallback":
                    await process_message_event(data, db)
                    return {
                        "status": "success",
                        "message": "Webhook processado via fallback",
                        "path": path,
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
                else:
                    logger.info(f"ℹ️ Evento {event_type} processado via fallback")
                    return {
                        "status": "processed",
                        "message": f"Evento {event_type} recebido",
                        "path": path,
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
            except Exception as json_error:
                logger.error(f"❌ Erro ao processar JSON no fallback: {json_error}")
        
        return {
            "status": "received",
            "message": f"Endpoint /{path} recebido",
            "method": request.method,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no fallback: {str(e)}")
        return {
            "status": "error",
            "message": "Erro no processamento do fallback",
            "error": str(e) if not settings.is_production() else "Erro interno",
            "timestamp": datetime.now().isoformat() + "Z"
        }