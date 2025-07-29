from pydantic import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Z-API
    zapi_instance_id: str
    zapi_token: str
    zapi_client_token: str
    zapi_base_url: str = "https://api.z-api.io"

    # GestãoDS
    gestaods_api_url: str
    gestaods_token: str

    # Database
    database_url: str

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    environment: str = "development"
    debug: bool = True

    # Clinic
    clinic_name: str
    clinic_phone: str
    reminder_hour: int = 18
    reminder_minute: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 