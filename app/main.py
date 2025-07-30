from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import traceback

from app.config import settings
from app.handlers.webhook import router as webhook_router
from app.handlers.dashboard import router as dashboard_router

# Configurar logging mais detalhado para Vercel
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

# Middleware para capturar erros
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "Ocorreu um erro interno no servidor",
                "environment": "vercel" if IS_VERCEL else "local"
            }
        )

# Incluir routers
try:
    app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
    app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    logger.info("Routers carregados com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar routers: {str(e)}")

@app.get("/")
async def root():
    """Endpoint de saúde"""
    try:
        return {
            "status": "online",
            "service": "Chatbot Clínica",
            "version": "1.0.0",
            "environment": "vercel" if IS_VERCEL else "local",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Erro no endpoint root: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    try:
        return {
            "message": "Backend funcionando!",
            "environment": "vercel" if IS_VERCEL else "local",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Erro no endpoint test: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/health")
async def health_check():
    """Verificação de saúde detalhada"""
    try:
        # Verificar configurações básicas
        health_status = {
            "status": "healthy",
            "environment": "vercel" if IS_VERCEL else "local",
            "config": {
                "supabase_url": bool(settings.supabase_url),
                "supabase_anon_key": bool(settings.supabase_anon_key),
                "zapi_instance_id": bool(settings.zapi_instance_id),
                "gestaods_token": bool(settings.gestaods_token)
            }
        }
        
        # Verificar se as configurações essenciais estão presentes
        if not settings.supabase_url or not settings.supabase_anon_key:
            health_status["status"] = "warning"
            health_status["message"] = "Configurações do Supabase não encontradas"
        
        return health_status
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "environment": "vercel" if IS_VERCEL else "local"
        }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"Exceção global: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Ocorreu um erro interno no servidor",
            "environment": "vercel" if IS_VERCEL else "local"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 