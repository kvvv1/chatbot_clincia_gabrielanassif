from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Z-API
    zapi_instance_id: str = ""
    zapi_token: str = ""
    zapi_client_token: str = ""
    zapi_base_url: str = "https://api.z-api.io"

    # GestãoDS
    gestaods_api_url: str = "https://apidev.gestaods.com.br"
    gestaods_token: str = "733a8e19a94b65d58390da380ac946b6d603a535"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/chatbot_clinica"
    
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
    clinic_phone: str = ""
    reminder_hour: int = 18
    reminder_minute: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 