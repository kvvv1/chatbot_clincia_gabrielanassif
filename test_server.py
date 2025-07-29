from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação FastAPI
app = FastAPI(
    title="Chatbot Clínica WhatsApp - Teste",
    description="Servidor de teste para o chatbot",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint de saúde"""
    return {
        "status": "online",
        "service": "Chatbot Clínica - Teste",
        "version": "1.0.0",
        "message": "Servidor funcionando corretamente!"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde detalhada"""
    return {
        "status": "healthy",
        "database": "sqlite (teste)",
        "whatsapp": "simulado",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {
        "message": "Teste funcionando!",
        "config": {
            "clinic_name": os.getenv("CLINIC_NAME", "Clínica Teste"),
            "app_host": os.getenv("APP_HOST", "0.0.0.0"),
            "app_port": os.getenv("APP_PORT", "8000")
        }
    }

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    print(f"🚀 Iniciando servidor de teste em http://{host}:{port}")
    print(f"📋 Endpoints disponíveis:")
    print(f"   - GET / - Status básico")
    print(f"   - GET /health - Verificação de saúde")
    print(f"   - GET /test - Teste de configuração")
    
    uvicorn.run(
        "test_server:app",
        host=host,
        port=port,
        reload=True
    ) 