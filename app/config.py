from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Z-API
    zapi_instance_id: Optional[str] = ""
    zapi_token: Optional[str] = ""
    zapi_client_token: Optional[str] = ""
    zapi_base_url: str = "https://api.z-api.io"

    # GestãoDS
    gestaods_api_url: str = "https://apidev.gestaods.com.br"
    gestaods_token: str = "733a8e19a94b65d58390da380ac946b6d603a535"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/chatbot_clinica"
    
    # Supabase
    supabase_url: Optional[str] = ""
    supabase_anon_key: Optional[str] = ""
    supabase_service_role_key: Optional[str] = ""

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
    clinic_name: Optional[str] = "Clínica Nassif"
    clinic_phone: Optional[str] = ""
    reminder_hour: int = 18
    reminder_minute: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            logger.info("Configurações carregadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
            # Usar valores padrão em caso de erro
            self.zapi_instance_id = ""
            self.zapi_token = ""
            self.zapi_client_token = ""
            self.zapi_base_url = "https://api.z-api.io"
            self.gestaods_api_url = "https://apidev.gestaods.com.br"
            self.gestaods_token = ""
            self.database_url = ""
            self.supabase_url = ""
            self.supabase_anon_key = ""
            self.supabase_service_role_key = ""
            self.app_host = "0.0.0.0"
            self.app_port = 8000
            self.environment = "development"
            self.debug = True
            self.websocket_enabled = False  # Desabilitar WebSocket por padrão em produção
            self.websocket_max_connections = 10
            self.cors_origins = "*"
            self.cors_allow_credentials = False
            self.clinic_name = "Clínica Nassif"
            self.clinic_phone = ""
            self.reminder_hour = 18
            self.reminder_minute = 0

@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {str(e)}")
        # Retornar configurações de fallback
        settings = Settings()
        settings.supabase_url = ""
        settings.supabase_anon_key = ""
        settings.websocket_enabled = False
        return settings

settings = get_settings() 