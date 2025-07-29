from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json

from app.models.database import get_db
from app.models.dashboard import (
    ConversationDashboard, ConversationMessage, 
    ConversationNote, ConversationStatus, ConversationTag
)
from app.services.classifier import ConversationClassifier

router = APIRouter()
classifier = ConversationClassifier()

# WebSocket manager para real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.get("/conversations")
async def list_conversations(
    status: Optional[ConversationStatus] = None,
    priority: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as conversas com filtros"""
    
    query = db.query(ConversationDashboard)
    
    if status:
        query = query.filter(ConversationDashboard.status == status)
    
    if priority is not None:
        query = query.filter(ConversationDashboard.priority == priority)
    
    if date_from:
        query = query.filter(ConversationDashboard.first_message_at >= date_from)
    
    if date_to:
        query = query.filter(ConversationDashboard.last_message_at <= date_to)
    
    if search:
        query = query.filter(
            ConversationDashboard.phone.contains(search) |
            ConversationDashboard.patient_name.contains(search) |
            ConversationDashboard.patient_cpf.contains(search)
        )
    
    # Ordenar por prioridade e data
    conversations = query.order_by(
        ConversationDashboard.priority.desc(),
        ConversationDashboard.last_message_at.desc()
    ).all()
    
    return conversations

@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Detalhes completos de uma conversa"""
    
    conversation = db.query(ConversationDashboard).filter(
        ConversationDashboard.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    # Carregar mensagens
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.dashboard_id == conversation_id
    ).order_by(ConversationMessage.timestamp).all()
    
    # Carregar notas
    notes = db.query(ConversationNote).filter(
        ConversationNote.dashboard_id == conversation_id
    ).order_by(ConversationNote.created_at.desc()).all()
    
    return {
        "conversation": conversation,
        "messages": messages,
        "notes": notes
    }

@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    status: Optional[ConversationStatus] = None,
    tags: Optional[List[str]] = None,
    priority: Optional[int] = None,
    reviewed_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Atualiza status e tags de uma conversa"""
    
    conversation = db.query(ConversationDashboard).filter(
        ConversationDashboard.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    if status:
        conversation.status = status
    
    if tags is not None:
        conversation.tags = tags
    
    if priority is not None:
        conversation.priority = priority
    
    if reviewed_by:
        conversation.reviewed_by = reviewed_by
        conversation.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    # Broadcast update
    await manager.broadcast({
        "type": "conversation_updated",
        "conversation_id": conversation_id,
        "status": status.value if status else None
    })
    
    return conversation

@router.post("/conversations/{conversation_id}/notes")
async def add_note(
    conversation_id: str,
    note: str,
    created_by: str,
    db: Session = Depends(get_db)
):
    """Adiciona nota a uma conversa"""
    
    new_note = ConversationNote(
        dashboard_id=conversation_id,
        note=note,
        created_by=created_by
    )
    
    db.add(new_note)
    db.commit()
    
    return new_note

@router.get("/analytics/summary")
async def get_analytics_summary(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Resumo analítico do período"""
    
    if not date_from:
        date_from = datetime.now() - timedelta(days=7)
    
    if not date_to:
        date_to = datetime.now()
    
    # Total de conversas
    total_conversations = db.query(ConversationDashboard).filter(
        ConversationDashboard.first_message_at >= date_from,
        ConversationDashboard.first_message_at <= date_to
    ).count()
    
    # Por status
    status_counts = {}
    for status in ConversationStatus:
        count = db.query(ConversationDashboard).filter(
            ConversationDashboard.status == status,
            ConversationDashboard.first_message_at >= date_from
        ).count()
        status_counts[status.value] = count
    
    # Taxa de resolução do bot
    bot_resolved = db.query(ConversationDashboard).filter(
        ConversationDashboard.bot_resolution == True,
        ConversationDashboard.first_message_at >= date_from
    ).count()
    
    # Tempo médio de resolução
    avg_resolution = db.query(
        func.avg(ConversationDashboard.resolution_time)
    ).filter(
        ConversationDashboard.resolution_time.isnot(None),
        ConversationDashboard.first_message_at >= date_from
    ).scalar()
    
    # Tags mais comuns
    # (Implementar agregação de tags JSON)
    
    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "total_conversations": total_conversations,
        "status_distribution": status_counts,
        "bot_resolution_rate": (bot_resolved / total_conversations * 100) if total_conversations > 0 else 0,
        "avg_resolution_time_minutes": avg_resolution or 0
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para atualizações em tempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # Manter conexão viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Função para processar nova conversa (chamada pelo bot)
async def process_new_conversation(phone: str, messages: List[Dict], db: Session):
    """Processa e classifica nova conversa"""
    
    # Analisar conversa
    analysis = await classifier.analyze_conversation(messages)
    
    # Criar entrada no dashboard
    dashboard_entry = ConversationDashboard(
        phone=phone,
        tags=analysis['tags'],
        priority=analysis['priority'],
        sentiment_score=analysis['sentiment_score'],
        ai_summary=analysis['ai_summary'],
        ai_suggested_action=analysis['ai_suggested_action'],
        status=ConversationStatus.REQUIRES_ATTENTION if analysis['requires_attention'] else ConversationStatus.PENDING,
        message_count=len(messages),
        first_message_at=messages[0]['timestamp'] if messages else datetime.utcnow(),
        last_message_at=messages[-1]['timestamp'] if messages else datetime.utcnow()
    )
    
    db.add(dashboard_entry)
    
    # Adicionar mensagens
    for msg in messages:
        conversation_msg = ConversationMessage(
            dashboard_id=dashboard_entry.id,
            sender=msg['sender'],
            message=msg['message'],
            timestamp=msg['timestamp'],
            message_type=msg.get('type', 'text')
        )
        db.add(conversation_msg)
    
    db.commit()
    
    # Notificar dashboard via WebSocket
    await manager.broadcast({
        "type": "new_conversation",
        "conversation": {
            "id": dashboard_entry.id,
            "phone": phone,
            "priority": analysis['priority'],
            "tags": analysis['tags'],
            "summary": analysis['ai_summary']
        }
    }) 