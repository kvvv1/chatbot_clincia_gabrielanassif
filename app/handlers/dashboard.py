from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import json
import os
from app.services.gestaods import GestaoDS

logger = logging.getLogger(__name__)
router = APIRouter()

# Verificar se estamos no Vercel (serverless)
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

# Instância do GestãoDS
try:
    gestaods = GestaoDS()
    logger.info(f"GestãoDS inicializado - URL: {gestaods.base_url}")
    logger.info(f"Token configurado: {'Sim' if gestaods.token else 'Não'}")
except Exception as e:
    logger.error(f"Erro ao inicializar GestãoDS: {str(e)}")
    gestaods = None

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

# Endpoints do GestãoDS
@router.get("/gestaods/health")
async def gestaods_health():
    """Verificação de saúde do GestãoDS"""
    try:
        if gestaods is None:
            return {
                "status": "unhealthy",
                "service": "gestaods",
                "error": "GestãoDS não inicializado",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
        return {
            "status": "healthy",
            "service": "gestaods",
            "base_url": gestaods.base_url,
            "environment": "dev" if gestaods.is_dev else "prod",
            "token_configured": bool(gestaods.token),
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro no health check do GestãoDS: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "gestaods",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.get("/gestaods/patient/{cpf}")
async def gestaods_get_patient(cpf: str):
    """Busca paciente por CPF"""
    try:
        # Verificar se o GestãoDS está configurado
        if not gestaods.base_url or not gestaods.token:
            logger.error("GestãoDS não configurado corretamente")
            return {
                "status": "error",
                "message": "GestãoDS não configurado",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
        # Limpar CPF
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise HTTPException(status_code=400, detail="CPF inválido")
        
        logger.info(f"Buscando paciente com CPF: {cpf_limpo}")
        paciente = await gestaods.buscar_paciente_cpf(cpf_limpo)
        
        if paciente:
            return {
                "status": "success",
                "patient": paciente,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            # Retornar paciente não encontrado em vez de erro 404
            return {
                "status": "not_found",
                "message": "Paciente não encontrado",
                "cpf": cpf_limpo,
                "timestamp": datetime.now().isoformat() + "Z"
            }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar paciente {cpf}: {str(e)}")
        logger.error(f"Tipo de erro: {type(e).__name__}")
        return {
            "status": "error",
            "message": f"Erro interno: {str(e)}",
            "cpf": cpf,
            "timestamp": datetime.now().isoformat() + "Z"
        }

@router.get("/gestaods/slots/{date}")
async def gestaods_get_slots(date: str):
    """Busca datas disponíveis"""
    try:
        slots = await gestaods.buscar_dias_disponiveis(date)
        return {
            "status": "success",
            "date": date,
            "slots": slots,
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/gestaods/times/{date}")
async def gestaods_get_times(date: str):
    """Busca horários disponíveis para uma data"""
    try:
        times = await gestaods.buscar_horarios_disponiveis(date)
        return {
            "status": "success",
            "date": date,
            "times": times,
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar horários: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/gestaods/widget")
async def gestaods_get_widget():
    """Informações do widget do GestãoDS"""
    try:
        return {
            "status": "success",
            "widget": {
                "name": "GestãoDS Calendar Widget",
                "version": "1.0",
                "base_url": gestaods.base_url,
                "environment": "dev" if gestaods.is_dev else "prod",
                "features": [
                    "patient_search",
                    "slot_booking",
                    "appointment_management"
                ]
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar widget: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/gestaods/config")
async def gestaods_get_config():
    """Configuração do GestãoDS"""
    try:
        return {
            "status": "success",
            "config": {
                "base_url": gestaods.base_url,
                "environment": "dev" if gestaods.is_dev else "prod",
                "timeout": gestaods.timeout,
                "cache_ttl": gestaods._cache_ttl
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar configuração: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/gestaods/services")
async def gestaods_get_services():
    """Lista de serviços disponíveis"""
    try:
        return {
            "status": "success",
            "services": [
                {
                    "name": "Patient Search",
                    "endpoint": "/gestaods/patient/{cpf}",
                    "method": "GET",
                    "description": "Busca paciente por CPF"
                },
                {
                    "name": "Available Slots",
                    "endpoint": "/gestaods/slots/{date}",
                    "method": "GET",
                    "description": "Busca datas disponíveis"
                },
                {
                    "name": "Available Times",
                    "endpoint": "/gestaods/times/{date}",
                    "method": "GET",
                    "description": "Busca horários disponíveis"
                },
                {
                    "name": "Create Appointment",
                    "endpoint": "/gestaods/appointment",
                    "method": "POST",
                    "description": "Cria novo agendamento"
                }
            ],
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar serviços: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/gestaods/doctors")
async def gestaods_get_doctors():
    """Lista de médicos disponíveis"""
    try:
        # Por enquanto, retornar dados de exemplo
        return {
            "status": "success",
            "doctors": [
                {
                    "id": 1,
                    "name": "Dr. Gabriela Nassif",
                    "specialty": "Clínica Geral",
                    "available": True
                },
                {
                    "id": 2,
                    "name": "Dr. João Silva",
                    "specialty": "Cardiologia",
                    "available": True
                }
            ],
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar médicos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/gestaods/appointment")
async def gestaods_create_appointment(request: dict):
    """Cria novo agendamento"""
    try:
        cpf = request.get("cpf")
        data_agendamento = request.get("data_agendamento")
        data_fim_agendamento = request.get("data_fim_agendamento")
        primeiro_atendimento = request.get("primeiro_atendimento", True)
        
        if not all([cpf, data_agendamento, data_fim_agendamento]):
            raise HTTPException(status_code=400, detail="Dados obrigatórios não fornecidos")
        
        agendamento = await gestaods.criar_agendamento(
            cpf=cpf,
            data_agendamento=data_agendamento,
            data_fim_agendamento=data_fim_agendamento,
            primeiro_atendimento=primeiro_atendimento
        )
        
        if agendamento:
            return {
                "status": "success",
                "appointment": agendamento,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar agendamento")
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

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
        # Por enquanto, apenas simular envio
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message": message,
            "sent_at": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/analytics")
async def get_analytics():
    """Obtém dados de analytics"""
    try:
        # Dados de exemplo
        analytics = {
            "conversations": {
                "total": 2,
                "active_last_7_days": 2,
                "by_state": [
                    {
                        "state": "menu_principal",
                        "count": 1
                    },
                    {
                        "state": "aguardando_cpf",
                        "count": 1
                    }
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
        
        return analytics
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {
        "message": "Dashboard funcionando!",
        "timestamp": datetime.now().isoformat() + "Z"
    }

@router.get("/status")
async def get_status():
    """Status geral do sistema"""
    try:
        return {
            "status": "operational",
            "services": {
                "dashboard": "healthy",
                "gestaods": "healthy" if gestaods.base_url else "unhealthy",
                "webhook": "healthy"
            },
            "environment": "vercel" if IS_VERCEL else "local",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat() + "Z"
        } 