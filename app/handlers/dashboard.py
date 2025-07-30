from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
import logging
import json
import uuid
import os
from app.config import settings
from app.services.gestaods_widget import GestaoDSWidget
from app.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections
active_connections = []
MAX_CONNECTIONS = 50  # Limite máximo de conexões para produção

# Verificar se estamos no Vercel (serverless)
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint para atualizações em tempo real"""
    # Desabilitar WebSocket em ambiente serverless
    if IS_VERCEL:
        logger.warning("WebSocket desabilitado em ambiente serverless (Vercel)")
        await websocket.close(code=1008, reason="WebSocket not supported in serverless environment")
        return
    
    # Verificar se WebSocket está habilitado
    if not getattr(settings, 'websocket_enabled', True):
        await websocket.close(code=1008, reason="WebSocket disabled")
        return
    
    # Em ambiente serverless, limitar conexões WebSocket
    if IS_VERCEL and len(active_connections) >= 10:
        logger.warning(f"Limite de conexões WebSocket atingido em Vercel ({len(active_connections)})")
        await websocket.close(code=1008, reason="Too many connections")
        return
    
    # Verificar limite de conexões
    if len(active_connections) >= MAX_CONNECTIONS:
        logger.warning(f"Limite de conexões WebSocket atingido ({MAX_CONNECTIONS})")
        await websocket.close(code=1008, reason="Too many connections")
        return
    
    try:
        await websocket.accept()
        connection_id = str(uuid.uuid4())[:8]
        active_connections.append(websocket)
        
        logger.info(f"WebSocket conectado - ID: {connection_id}, Total: {len(active_connections)}")
        
        # Em ambiente serverless, manter conexão por tempo limitado
        max_messages = 100 if IS_VERCEL else 1000
        message_count = 0
        
        while True:
            # Keep connection alive - aguardar mensagem do cliente
            data = await websocket.receive_text()
            message_count += 1
            logger.debug(f"Mensagem recebida do WebSocket {connection_id}: {data}")
            
            # Em ambiente serverless, limitar número de mensagens
            if IS_VERCEL and message_count >= max_messages:
                logger.info(f"Limite de mensagens atingido para WebSocket {connection_id}")
                break
            
            # Responder com confirmação
            await websocket.send_text(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": connection_id,
                "message_count": message_count
            }))
            
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket desconectado - ID: {connection_id}, Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"Erro no WebSocket {connection_id}: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass

async def broadcast_message(message: dict):
    """Envia mensagem para todos os clientes WebSocket conectados"""
    if not active_connections:
        return
        
    logger.info(f"Enviando mensagem para {len(active_connections)} clientes WebSocket")
    
    for connection in active_connections[:]:  # Copiar lista para evitar modificação durante iteração
        try:
            await connection.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WebSocket: {str(e)}")
            active_connections.remove(connection)

@router.patch("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, updates: dict):
    """Atualiza uma conversa"""
    try:
        # In a real implementation, this would update the database
        # For now, just return success
        return {
            "id": conversation_id,
            "status": "success",
            "message": "Conversa atualizada com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/conversations/{conversation_id}/notes")
async def add_note(conversation_id: str, note_data: dict):
    """Adiciona uma nota a uma conversa"""
    try:
        # In a real implementation, this would save to database
        # For now, just return success
        return {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "note": note_data.get("note", ""),
            "created_by": note_data.get("created_by", "admin"),
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao adicionar nota: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    """Obtém detalhes de uma conversa específica"""
    try:
        # Sample conversation detail
        sample_conversation = {
            "id": conversation_id,
            "phone": "5531999999999",
            "patient_name": "Maria Silva",
            "status": "pending",
            "priority": 2,
            "ai_summary": "Paciente solicitando agendamento de consulta para próxima semana",
            "tags": ["agendamento", "consulta"],
            "message_count": 5,
            "last_message_at": "2024-01-15T10:30:00Z",
            "messages": [
                {
                    "id": "1",
                    "sender": "user",
                    "message": "Olá, gostaria de agendar uma consulta",
                    "timestamp": "2024-01-15T10:00:00Z"
                },
                {
                    "id": "2", 
                    "sender": "bot",
                    "message": "Olá! Claro, posso ajudá-lo a agendar uma consulta. Qual especialidade você precisa?",
                    "timestamp": "2024-01-15T10:01:00Z"
                },
                {
                    "id": "3",
                    "sender": "user", 
                    "message": "Preciso de um cardiologista",
                    "timestamp": "2024-01-15T10:02:00Z"
                }
            ],
            "notes": []
        }
        return sample_conversation
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/conversations")
async def list_conversations():
    """Lista todas as conversas - versão simplificada para teste"""
    try:
        # Sample data for testing
        sample_conversations = [
            {
                "id": "1",
                "phone": "5531999999999",
                "patient_name": "Maria Silva",
                "status": "pending",
                "priority": 2,
                "ai_summary": "Paciente solicitando agendamento de consulta para próxima semana",
                "tags": ["agendamento", "consulta"],
                "message_count": 5,
                "last_message_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "2", 
                "phone": "5531888888888",
                "patient_name": "João Santos",
                "status": "in_progress",
                "priority": 1,
                "ai_summary": "Paciente com dúvidas sobre horários de atendimento",
                "tags": ["horários", "dúvida"],
                "message_count": 3,
                "last_message_at": "2024-01-15T09:15:00Z"
            },
            {
                "id": "3",
                "phone": "5531777777777", 
                "patient_name": "Ana Costa",
                "status": "requires_attention",
                "priority": 3,
                "ai_summary": "Paciente com urgência médica - precisa de atendimento imediato",
                "tags": ["urgência", "emergência"],
                "message_count": 8,
                "last_message_at": "2024-01-15T11:45:00Z"
            }
        ]
        return sample_conversations
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/analytics/summary")
async def get_analytics_summary():
    """Endpoint para dados de analytics"""
    return {
        "total_conversations": 3,
        "pending_conversations": 1,
        "completed_conversations": 0,
        "requires_attention": 1,
        "average_response_time": 2.5,
        "conversations_by_status": {
            "pending": 1,
            "in_progress": 1,
            "completed": 0,
            "requires_attention": 1
        },
        "conversations_by_priority": {
            "0": 0,
            "1": 1,
            "2": 1,
            "3": 1
        }
    }

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {"status": "ok", "message": "Dashboard API funcionando!"}

@router.get("/ws-test")
async def websocket_test():
    """Teste se o endpoint WebSocket está acessível"""
    if IS_VERCEL:
        return {
            "status": "warning", 
            "message": "WebSocket não suportado em ambiente serverless (Vercel)",
            "environment": "serverless"
        }
    return {"status": "ok", "message": "WebSocket endpoint está acessível"}

async def process_new_conversation(phone: str, messages: list, db):
    """Processa nova conversa para o dashboard"""
    try:
        logger.info(f"Processando nova conversa para {phone}")
        # Aqui você pode adicionar lógica para processar conversas
        # Por exemplo, salvar no banco, enviar notificações, etc.
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro ao processar conversa: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/status")
async def get_status():
    """Endpoint de status para verificar se a API está funcionando"""
    try:
        return {
            "status": "ok",
            "message": "Dashboard API funcionando!",
            "environment": "vercel" if IS_VERCEL else "local",
            "timestamp": datetime.utcnow().isoformat(),
            "config": {
                "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key),
                "websocket_enabled": getattr(settings, 'websocket_enabled', True),
                "serverless": IS_VERCEL
            }
        }
    except Exception as e:
        logger.error(f"Erro no endpoint status: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "environment": "vercel" if IS_VERCEL else "local"
        }

@router.get("/supabase/test")
async def test_supabase_connection():
    """Testa conexão com Supabase"""
    try:
        # Verificar se as configurações do Supabase estão presentes
        if not settings.supabase_url or not settings.supabase_anon_key:
            return {
                "status": "warning", 
                "message": "Configurações do Supabase não encontradas",
                "environment": "vercel" if IS_VERCEL else "local"
            }
        
        supabase = SupabaseService()
        is_connected = await supabase.test_connection()
        
        if is_connected:
            return {"status": "success", "message": "Conexão com Supabase estabelecida"}
        else:
            return {"status": "error", "message": "Erro ao conectar com Supabase"}
    except Exception as e:
        logger.error(f"Erro ao testar Supabase: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/supabase/stats")
async def get_supabase_stats():
    """Obtém estatísticas do Supabase"""
    try:
        # Verificar se as configurações do Supabase estão presentes
        if not settings.supabase_url or not settings.supabase_anon_key:
            return {
                "status": "warning", 
                "message": "Configurações do Supabase não encontradas",
                "environment": "vercel" if IS_VERCEL else "local"
            }
        
        supabase = SupabaseService()
        stats = await supabase.get_dashboard_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/supabase/conversation")
async def create_supabase_conversation(conversation_data: dict):
    """Cria conversa no Supabase"""
    try:
        # Verificar se as configurações do Supabase estão presentes
        if not settings.supabase_url or not settings.supabase_anon_key:
            return {
                "status": "warning", 
                "message": "Configurações do Supabase não encontradas",
                "environment": "vercel" if IS_VERCEL else "local"
            }
        
        supabase = SupabaseService()
        result = await supabase.create_conversation(
            phone=conversation_data.get("phone"),
            state=conversation_data.get("state", "inicio"),
            context=conversation_data.get("context", {})
        )
        
        if result:
            return {"status": "success", "conversation": result}
        else:
            return {"status": "error", "message": "Erro ao criar conversa"}
    except Exception as e:
        logger.error(f"Erro ao criar conversa: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/supabase/conversation/{phone}")
async def get_supabase_conversation(phone: str):
    """Busca conversa no Supabase"""
    try:
        # Verificar se as configurações do Supabase estão presentes
        if not settings.supabase_url or not settings.supabase_anon_key:
            return {
                "status": "warning", 
                "message": "Configurações do Supabase não encontradas",
                "environment": "vercel" if IS_VERCEL else "local"
            }
        
        supabase = SupabaseService()
        result = await supabase.get_conversation(phone)
        
        if result:
            return {"status": "success", "conversation": result}
        else:
            return {"status": "not_found", "message": "Conversa não encontrada"}
    except Exception as e:
        logger.error(f"Erro ao buscar conversa: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/gestaods/widget")
async def get_gestaods_widget():
    """Obtém informações do widget da GestãoDS"""
    try:
        widget = GestaoDSWidget()
        return {
            "widget_url": widget.get_widget_url(),
            "embed_code": widget.get_widget_embed_code(),
            "share_data": widget.get_share_modal_data()
        }
    except Exception as e:
        logger.error(f"Erro ao obter widget: {str(e)}")
        return {"error": "Erro ao obter widget da GestãoDS"}

@router.get("/gestaods/slots/{date}")
async def get_available_slots(date: str):
    """Obtém horários disponíveis para uma data específica"""
    try:
        from datetime import datetime
        widget = GestaoDSWidget()
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        slots = await widget.get_available_slots(date_obj)
        return {"slots": slots, "date": date}
    except Exception as e:
        logger.error(f"Erro ao obter horários: {str(e)}")
        return {"error": "Erro ao obter horários disponíveis"}

@router.post("/gestaods/appointment")
async def create_appointment_via_widget(appointment_data: dict):
    """Cria agendamento via widget da GestãoDS"""
    try:
        widget = GestaoDSWidget()
        result = await widget.create_appointment_via_widget(
            patient_data=appointment_data.get("patient", {}),
            slot_id=appointment_data.get("slot_id"),
            notes=appointment_data.get("notes", "")
        )
        
        if result:
            return {"status": "success", "appointment": result}
        else:
            return {"status": "error", "message": "Erro ao criar agendamento"}
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        return {"status": "error", "message": str(e)} 