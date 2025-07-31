from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Z-API
    zapi_instance_id: str = ""
    zapi_token: str = ""
    zapi_client_token: str = ""
    zapi_base_url: str = "https://api.z-api.io"

    # GestãoDS
    gestaods_api_url: str = "https://apidev.gestaods.com.br"
    gestaods_token: str = "733a8e19a94b65d58390da380ac946b6d603a535"

    # Database - Usar Supabase no Vercel
    database_url: str = ""
    
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    environment: str = "development"
    debug: bool = True
    
    # WebSocket
    websocket_enabled: bool = True
    websocket_max_connections: int = 50
    
    # CORS
    cors_origins: str = "*"
    cors_allow_credentials: bool = True

    # Clinic
    clinic_name: str = "Clínica Nassif"
    clinic_phone: str = "+553198600366"
    clinic_email: str = "contato@clinicanassif.com.br"
    clinic_address: str = "Rua Example, 123 - Savassi\nBelo Horizonte - MG"
    reminder_hour: int = 18
    reminder_minute: int = 0

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore", 
        "validate_assignment": False,
        "validate_default": False
    }

@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {str(e)}")
        logger.error(f"Criando configurações de fallback para evitar crash")
        # Retornar configurações de fallback totalmente seguras
        return create_fallback_settings()

def create_fallback_settings():
    """Cria configurações de fallback sem usar Pydantic para evitar erros de validação"""
    class FallbackSettings:
        def __init__(self):
            self.zapi_instance_id = os.getenv('ZAPI_INSTANCE_ID', '')
            self.zapi_token = os.getenv('ZAPI_TOKEN', '')
            self.zapi_client_token = os.getenv('ZAPI_CLIENT_TOKEN', '')
            self.zapi_base_url = os.getenv('ZAPI_BASE_URL', 'https://api.z-api.io')
            self.gestaods_api_url = os.getenv('GESTAODS_API_URL', 'https://apidev.gestaods.com.br')
            self.gestaods_token = os.getenv('GESTAODS_TOKEN', '')
            
            # No Vercel, não usar database_url local
            if os.getenv('VERCEL', '0') == '1':
                self.database_url = ""
            else:
                self.database_url = os.getenv('DATABASE_URL', '')
                
            self.supabase_url = os.getenv('SUPABASE_URL', '')
            self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '')
            self.supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
            self.app_host = os.getenv('APP_HOST', '0.0.0.0')
            self.app_port = int(os.getenv('APP_PORT', '8000'))
            self.environment = os.getenv('ENVIRONMENT', 'development')
            self.debug = os.getenv('DEBUG', 'True').lower() == 'true'
            self.websocket_enabled = os.getenv('WEBSOCKET_ENABLED', 'False').lower() == 'true'
            self.websocket_max_connections = int(os.getenv('WEBSOCKET_MAX_CONNECTIONS', '10'))
            self.cors_origins = os.getenv('CORS_ORIGINS', '*')
            self.cors_allow_credentials = os.getenv('CORS_ALLOW_CREDENTIALS', 'False').lower() == 'true'
            self.clinic_name = os.getenv('CLINIC_NAME', 'Clínica Nassif')
            self.clinic_phone = os.getenv('CLINIC_PHONE', '+553198600366')
            self.clinic_email = os.getenv('CLINIC_EMAIL', 'contato@clinicanassif.com.br')
            self.clinic_address = os.getenv('CLINIC_ADDRESS', 'Rua Example, 123 - Savassi\nBelo Horizonte - MG')
            self.reminder_hour = int(os.getenv('REMINDER_HOUR', '18'))
            self.reminder_minute = int(os.getenv('REMINDER_MINUTE', '0'))
    
    return FallbackSettings()

# Tentar usar Pydantic primeiro, fallback para classe simples se falhar
try:
    settings = get_settings()
    logger.info("Usando configurações Pydantic")
except Exception as e:
    logger.error(f"Falha ao carregar com Pydantic: {str(e)}")
    settings = create_fallback_settings()
    logger.info("Usando configurações de fallback") 