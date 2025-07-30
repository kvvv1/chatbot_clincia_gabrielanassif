from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging
import sys

from app.config import settings
from app.handlers.webhook import router as webhook_router
from app.handlers.dashboard import router as dashboard_router
from app.tasks.reminders import ReminderService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Scheduler global
scheduler = AsyncIOScheduler()
reminder_service = ReminderService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação...")

    # Configurar tarefas agendadas
    scheduler.add_job(
        reminder_service.enviar_lembretes_diarios,
        'cron',
        hour=settings.reminder_hour,
        minute=settings.reminder_minute
    )

    scheduler.add_job(
        reminder_service.verificar_cancelamentos,
        'interval',
        minutes=30
    )

    scheduler.start()
    logger.info("Scheduler iniciado")

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("Aplicação encerrada")

# Criar aplicação FastAPI
app = FastAPI(
    title="Chatbot Clínica WhatsApp",
    description="Assistente virtual para agendamento de consultas",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    """Endpoint de saúde"""
    return {
        "status": "online",
        "service": "Chatbot Clínica",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde detalhada"""
    return {
        "status": "healthy",
        "database": "connected",
        "whatsapp": "connected",
        "scheduler": scheduler.running
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    ) 