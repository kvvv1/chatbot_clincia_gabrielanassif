"""
Configurações específicas para produção
"""
from app.config import Settings

class ProductionSettings(Settings):
    """Configurações para ambiente de produção"""
    
    # Forçar configurações de produção
    environment: str = "production"
    debug: bool = False
    
    # WebSocket otimizado para produção
    websocket_enabled: bool = True
    websocket_max_connections: int = 100
    
    # CORS restritivo para produção
    cors_origins: str = "https://seu-frontend.netlify.app"
    cors_allow_credentials: bool = True
    
    # Logging otimizado
    log_level: str = "INFO"
    
    # Timeouts para produção
    request_timeout: int = 30
    websocket_timeout: int = 60
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False

def get_production_settings():
    """Retorna configurações de produção"""
    return ProductionSettings() 