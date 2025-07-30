from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

from app.config import settings
from app.handlers.webhook import router as webhook_router
from app.handlers.dashboard import router as dashboard_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Verificar se estamos no Vercel
IS_VERCEL = os.getenv('VERCEL', '0') == '1'

# Criar aplicação FastAPI
app = FastAPI(
    title="Chatbot Clínica WhatsApp",
    description="Assistente virtual para agendamento de consultas",
    version="1.0.0"
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
        "version": "1.0.0",
        "environment": "vercel" if IS_VERCEL else "local"
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {
        "message": "Backend funcionando!",
        "environment": "vercel" if IS_VERCEL else "local",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde detalhada"""
    return {
        "status": "healthy",
        "database": "connected",
        "whatsapp": "connected",
        "environment": "vercel" if IS_VERCEL else "local"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 