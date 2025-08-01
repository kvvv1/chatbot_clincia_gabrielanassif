import logging
import sys
import os
import traceback
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configurar logging básico - SEM arquivos no Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Detectar ambiente
IS_VERCEL = os.getenv('VERCEL', '0') == '1'
ENVIRONMENT = 'vercel' if IS_VERCEL else os.getenv('ENVIRONMENT', 'development')

logger.info(f"🚀 Iniciando aplicação FastAPI - Ambiente: {ENVIRONMENT}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info(f"🔧 Configurando aplicação - Ambiente: {ENVIRONMENT}")
    
    try:
        # Carregar configurações
        from app.config import settings
        logger.info(f"✅ Configurações carregadas: {settings.environment}")
        
        # Verificar banco de dados
        from app.models.database import health_check
        db_health = health_check()
        logger.info(f"💾 Banco de dados: {db_health['status']} ({db_health.get('database_type', 'unknown')})")
        
        # Adicionar informações ao estado da aplicação
        app.state.environment = ENVIRONMENT
        app.state.db_health = db_health
        app.state.settings = settings
        
        logger.info("✅ Aplicação iniciada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {str(e)}")
        # Permitir que a aplicação suba mesmo com erros (modo degradado)
        app.state.initialization_error = str(e)
    
    yield
    
    # Shutdown
    logger.info("🔄 Finalizando aplicação...")
    logger.info("👋 Aplicação finalizada")

# Criar aplicação FastAPI
app = FastAPI(
    title="Chatbot Clínica WhatsApp",
    description="Assistente virtual para agendamento de consultas médicas",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
cors_origins = ["*"] if ENVIRONMENT != "production" else [
    "https://chatbot-clincia.vercel.app",
    "https://clinicanassif.com.br"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para capturar erros globais
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"❌ Erro não tratado: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "Ocorreu um erro interno no servidor",
                "environment": ENVIRONMENT,
                "details": str(e) if ENVIRONMENT != "production" else "Erro interno",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        )

# Middleware para logging de requests (apenas desenvolvimento)
if ENVIRONMENT in ["development", "local"]:
    @app.middleware("http")
    async def log_requests_middleware(request: Request, call_next):
        import time
        start_time = time.time()
        
        logger.debug(f"🔍 {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.debug(f"✅ {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ {request.method} {request.url.path} - ERROR - {process_time:.3f}s - {str(e)}")
            raise

# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz com informações da aplicação"""
    try:
        # Verificar estado da aplicação
        app_status = "healthy"
        if hasattr(app.state, 'initialization_error'):
            app_status = "degraded"
        
        return {
            "status": app_status,
            "service": "Chatbot Clínica",
            "version": "2.0.0",
            "environment": ENVIRONMENT,
            "timestamp": datetime.now().isoformat() + "Z",
            "endpoints": {
                "health": "/health",
                "webhook": "/webhook",
                "dashboard": "/dashboard",
                "docs": "/docs"
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro no endpoint root: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/health")
async def health_check():
    """Verificação de saúde completa da aplicação"""
    try:
        # Status geral
        overall_status = "healthy"
        components = {}
        
        # Verificar configurações
        try:
            from app.config import settings
            components["config"] = {
                "status": "healthy",
                "environment": settings.environment,
                "debug": settings.debug
            }
        except Exception as e:
            components["config"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "degraded"
        
        # Verificar banco de dados
        try:
            from app.models.database import health_check as db_health_check
            db_health = db_health_check()
            components["database"] = db_health
            if db_health["status"] != "healthy":
                overall_status = "degraded"
        except Exception as e:
            components["database"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        # Verificar ConversationManager
        try:
            from app.services.conversation import ConversationManager
            manager = ConversationManager()
            components["conversation_manager"] = {
                "status": "healthy",
                "initialized": True
            }
        except Exception as e:
            components["conversation_manager"] = {
                "status": "unhealthy", 
                "error": str(e),
                "initialized": False
            }
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat() + "Z",
            "environment": ENVIRONMENT,
            "version": "2.0.0",
            "components": components
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e) if ENVIRONMENT != "production" else "Erro interno",
            "timestamp": datetime.now().isoformat() + "Z"
        }

@app.get("/status")
async def system_status():
    """Status detalhado do sistema"""
    try:
        status_info = {
            "application": {
                "name": "Chatbot Clínica",
                "version": "2.0.0",
                "environment": ENVIRONMENT,
                "uptime": "N/A"  # Pode implementar contador de uptime
            },
            "system": {
                "python_version": sys.version.split()[0],
                "platform": "vercel" if IS_VERCEL else "local"
            }
        }
        
        # Adicionar informações de configuração (sem dados sensíveis)
        try:
            from app.config import settings
            status_info["configuration"] = {
                "environment": settings.environment,
                "debug": settings.debug,
                "zapi_configured": bool(settings.zapi_instance_id and settings.zapi_token),
                "gestaods_configured": bool(settings.gestaods_token)
            }
        except Exception as config_error:
            status_info["configuration"] = {"error": str(config_error)}
        
        return status_info
        
    except Exception as e:
        logger.error(f"❌ Erro no status: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter status do sistema")

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    try:
        return {
            "message": "Backend funcionando!",
            "environment": ENVIRONMENT,
            "timestamp": datetime.now().isoformat() + "Z",
            "test": "passed"
        }
    except Exception as e:
        logger.error(f"❌ Erro no endpoint test: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/debug")
async def debug_info():
    """Informações de debug (apenas em desenvolvimento)"""
    if ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        return {
            "environment": ENVIRONMENT,
            "is_vercel": IS_VERCEL,
            "env_vars": {
                "VERCEL": os.getenv('VERCEL'),
                "NODE_ENV": os.getenv('NODE_ENV'),
                "ENVIRONMENT": os.getenv('ENVIRONMENT')
            },
            "python_info": {
                "version": sys.version,
                "executable": sys.executable,
                "path": sys.path[:5]  # Primeiros 5 elementos
            },
            "app_state": {
                "has_initialization_error": hasattr(app.state, 'initialization_error'),
                "error": getattr(app.state, 'initialization_error', None)
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro no debug endpoint: {str(e)}")
        return {"error": str(e)}

# Exception handlers globais
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"❌ Exceção global não tratada: {str(exc)}")
    logger.error(f"🔍 URL: {request.url}")
    logger.error(f"🔍 Method: {request.method}")
    logger.error(f"🔍 Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Ocorreu um erro interno no servidor",
            "environment": ENVIRONMENT,
            "details": str(exc) if ENVIRONMENT != "production" else "Erro interno",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler para endpoints não encontrados"""
    logger.warning(f"⚠️ Endpoint não encontrado: {request.method} {request.url.path}")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"Endpoint {request.url.path} não encontrado",
            "available_endpoints": ["/", "/health", "/status", "/webhook", "/docs"],
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )

# Incluir routers
logger.info("🔧 Carregando routers...")

# Router webhook (crítico)
try:
    from app.handlers.webhook import router as webhook_router
    app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
    logger.info("✅ Router webhook carregado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao carregar webhook router: {str(e)}")
    logger.error("🚨 CRÍTICO: Sistema funcionará sem webhook")

# Router dashboard (opcional)
try:
    from app.handlers.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    logger.info("✅ Router dashboard carregado com sucesso")
except Exception as e:
    logger.warning(f"⚠️ Dashboard router não disponível: {str(e)}")
    
    # Criar endpoints básicos do dashboard como fallback
    @app.get("/dashboard/")
    async def dashboard_fallback():
        return {
            "status": "fallback",
            "message": "Dashboard básico funcionando",
            "environment": ENVIRONMENT,
            "timestamp": datetime.now().isoformat() + "Z"
        }

# Fallback endpoint para compatibilidade
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def fallback_handler(request: Request, path: str):
    """Handler de fallback para rotas não encontradas"""
    logger.info(f"🔍 Fallback chamado: {request.method} /{path}")
    
    # Se for uma rota de webhook, tentar processar
    if path.startswith("webhook"):
        try:
            if request.method == "POST":
                data = await request.json()
                logger.info(f"📨 Webhook recebido via fallback: {data.get('type', 'unknown')}")
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "received",
                        "message": f"Webhook processado via fallback",
                        "path": path,
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
                )
        except Exception as e:
            logger.error(f"❌ Erro no fallback webhook: {str(e)}")
    
    # Para outras rotas, retornar informação útil
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"Rota /{path} não encontrada",
            "method": request.method,
            "available_routes": {
                "root": "/",
                "health": "/health",
                "status": "/status", 
                "webhook": "/webhook/*",
                "dashboard": "/dashboard/*",
                "docs": "/docs"
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )

# Informações finais de inicialização
logger.info("🎉 Sistema FastAPI configurado com sucesso")
logger.info(f"🌍 Ambiente: {ENVIRONMENT}")
logger.info(f"📍 Vercel: {IS_VERCEL}")

# Para desenvolvimento local
if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando servidor de desenvolvimento...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT in ["development", "local"],
        log_level="info" if ENVIRONMENT != "production" else "warning"
    )