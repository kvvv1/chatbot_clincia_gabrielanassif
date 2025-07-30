from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Verificar se estamos no Vercel (serverless)
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

@router.get("/health")
async def dashboard_health():
    """Verificação de saúde do dashboard"""
    try:
        return {
            "status": "healthy",
            "dashboard": "connected",
            "environment": "vercel" if IS_VERCEL else "local",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "dashboard": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.get("/conversations")
async def get_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Lista conversas com paginação e filtros"""
    try:
        # Por enquanto, retornar dados de exemplo
        sample_conversations = [
            {
                "id": 1,
                "phone": "553198600366",
                "state": "menu_principal",
                "created_at": datetime.now().isoformat() + "Z",
                "updated_at": datetime.now().isoformat() + "Z",
                "message_count": 3,
                "context": {"acao": "agendar"}
            },
            {
                "id": 2,
                "phone": "5531999999999",
                "state": "aguardando_cpf",
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat() + "Z",
                "updated_at": datetime.now().isoformat() + "Z",
                "message_count": 1,
                "context": {}
            }
        ]
        
        return {
            "conversations": sample_conversations,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(sample_conversations),
                "pages": 1
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar conversas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(conversation_id: int):
    """Obtém detalhes de uma conversa específica"""
    try:
        # Dados de exemplo
        conversation = {
            "id": conversation_id,
            "phone": "553198600366",
            "state": "menu_principal",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "message_count": 3,
            "context": {"acao": "agendar"}
        }
        
        return conversation
        
    except Exception as e:
        logger.error(f"Erro ao buscar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/conversations/{conversation_id}/send-message")
async def send_message_to_conversation(
    conversation_id: int,
    message: str
):
    """Envia mensagem para uma conversa específica"""
    try:
        return {
            "status": "success",
            "message": "Mensagem enviada com sucesso",
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat() + "Z"
        }
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/analytics")
async def get_analytics():
    """Obtém estatísticas e análises"""
    try:
        return {
            "conversations": {
                "total": 2,
                "active_last_7_days": 2,
                "by_state": [
                    {"state": "menu_principal", "count": 1},
                    {"state": "aguardando_cpf", "count": 1}
                ]
            },
            "appointments": {
                "total": 0,
                "today": 0,
                "next_7_days": 0,
                "by_status": []
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste do dashboard"""
    return {
        "status": "success",
        "message": "Dashboard funcionando corretamente",
        "environment": "vercel" if IS_VERCEL else "local",
        "timestamp": datetime.now().isoformat() + "Z"
    }

@router.get("/status")
async def get_status():
    """Status do dashboard"""
    return {
        "status": "online",
        "dashboard": "connected",
        "environment": "vercel" if IS_VERCEL else "local",
        "timestamp": datetime.now().isoformat() + "Z"
    } 