from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import traceback

# Configurar logging básico
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

logger.info(f"Iniciando aplicação FastAPI - Ambiente: {'Vercel' if IS_VERCEL else 'Local'}")

# Inicializar configurações de forma segura
try:
    from app.config import settings
    logger.info("Configurações carregadas com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar configurações: {str(e)}")
    logger.info("Aplicação continuará com configurações mínimas")
    # Criar objeto de configurações mínimas
    class MinimalSettings:
        environment = "vercel" if IS_VERCEL else "development"
        debug = False if IS_VERCEL else True
        websocket_enabled = False
    settings = MinimalSettings()

# Criar aplicação FastAPI
app = FastAPI(
    title="Chatbot Clínica WhatsApp",
    description="Assistente virtual para agendamento de consultas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
                "environment": "vercel" if IS_VERCEL else "local",
                "details": str(e)
            }
        )

# Endpoints básicos
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
        return {
            "status": "healthy",
            "environment": "vercel" if IS_VERCEL else "local",
            "config": {
                "vercel": IS_VERCEL,
                "python_version": sys.version,
                "python_path": sys.path
            }
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "environment": "vercel" if IS_VERCEL else "local"
        }

@app.get("/debug")
async def debug_info():
    """Informações de debug para desenvolvimento"""
    try:
        return {
            "environment": "vercel" if IS_VERCEL else "local",
            "env_vars": {
                "VERCEL": os.getenv('VERCEL'),
                "NODE_ENV": os.getenv('NODE_ENV'),
                "PYTHONPATH": os.getenv('PYTHONPATH')
            },
            "python_info": {
                "version": sys.version,
                "executable": sys.executable,
                "path": sys.path[:5]  # Primeiros 5 elementos
            }
        }
    except Exception as e:
        logger.error(f"Erro no debug endpoint: {str(e)}")
        return {"error": str(e)}

# Criar router de fallback sempre disponível
from fastapi import APIRouter

fallback_router = APIRouter()

@fallback_router.get("/test")
async def fallback_test():
    return {"status": "fallback", "message": "Router de fallback funcionando"}

@fallback_router.get("/status")
async def fallback_status():
    return {
        "status": "fallback",
        "message": "Dashboard API funcionando (modo fallback)",
        "environment": "vercel" if IS_VERCEL else "local"
    }

# Sempre incluir o router de fallback primeiro
app.include_router(fallback_router, prefix="/dashboard", tags=["dashboard"])

# Tentar incluir routers apenas se não houver erro
try:
    from app.handlers.webhook import router as webhook_router
    app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
    logger.info("Router webhook carregado com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar webhook router: {str(e)}")
    logger.info("Webhook router não disponível - usando apenas endpoints básicos")

# Tentar incluir dashboard router (pode sobrescrever fallback se bem-sucedido)
try:
    from app.handlers.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/dashboard-advanced", tags=["dashboard-advanced"])
    logger.info("Router dashboard avançado carregado com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar dashboard router: {str(e)}")
    logger.info("Usando apenas router de fallback para dashboard")

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
            "environment": "vercel" if IS_VERCEL else "local",
            "details": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 