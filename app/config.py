import os
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class Settings:
    """Configurações robustas sem dependência do Pydantic"""
    
    def __init__(self):
        # Z-API
        self.zapi_instance_id = os.getenv('ZAPI_INSTANCE_ID', '')
        self.zapi_token = os.getenv('ZAPI_TOKEN', '')
        self.zapi_client_token = os.getenv('ZAPI_CLIENT_TOKEN', '')
        self.zapi_base_url = os.getenv('ZAPI_BASE_URL', 'https://api.z-api.io')

        # GestãoDS
        self.gestaods_api_url = os.getenv('GESTAODS_API_URL', 'https://apidev.gestaods.com.br')
        self.gestaods_token = os.getenv('GESTAODS_TOKEN', '733a8e19a94b65d58390da380ac946b6d603a535')

        # Database - Configuração inteligente baseada no ambiente
        self.database_url = self._get_database_url()
        
        # Supabase
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '')
        self.supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

        # App
        self.app_host = os.getenv('APP_HOST', 'https://chatbot-clincia.vercel.app')
        self.app_port = int(os.getenv('APP_PORT', '8000'))
        self.environment = self._detect_environment()
        self.debug = self._get_debug_mode()
        
        # WebSocket
        self.websocket_enabled = os.getenv('WEBSOCKET_ENABLED', 'False').lower() == 'true'
        self.websocket_max_connections = int(os.getenv('WEBSOCKET_MAX_CONNECTIONS', '50'))
        
        # CORS
        self.cors_origins = os.getenv('CORS_ORIGINS', '*')
        self.cors_allow_credentials = os.getenv('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'

        # Clinic
        self.clinic_name = os.getenv('CLINIC_NAME', 'Clínica Nassif')
        self.clinic_phone = os.getenv('CLINIC_PHONE', '+553198600366')
        self.clinic_email = os.getenv('CLINIC_EMAIL', 'contato@clinicanassif.com.br')
        self.clinic_address = os.getenv('CLINIC_ADDRESS', 'Rua Example, 123 - Savassi\nBelo Horizonte - MG')
        self.reminder_hour = int(os.getenv('REMINDER_HOUR', '18'))
        self.reminder_minute = int(os.getenv('REMINDER_MINUTE', '0'))
        
        # Log da configuração
        self._log_configuration()
    
    def _get_database_url(self) -> str:
        """Obtém URL do banco baseado no ambiente"""
        # 1. Verificar DATABASE_URL direto
        database_url = os.getenv('DATABASE_URL', '')
        if database_url:
            return database_url
        
        # 2. No Vercel, não usar database_url local
        if self.is_vercel():
            return ""
        
        # 3. Ambiente local pode usar SQLite
        return ""
    
    def _detect_environment(self) -> str:
        """Detecta automaticamente o ambiente"""
        if os.getenv('VERCEL'):
            return 'vercel'
        elif os.getenv('ENVIRONMENT'):
            return os.getenv('ENVIRONMENT', 'development').lower()
        elif os.getenv('NODE_ENV') == 'production':
            return 'production'
        else:
            return 'development'
    
    def _get_debug_mode(self) -> bool:
        """Define modo debug baseado no ambiente"""
        if self.environment in ['development', 'local']:
            return True
        debug_env = os.getenv('DEBUG', 'False').lower()
        return debug_env in ['true', '1', 'yes']
    
    def _log_configuration(self):
        """Log da configuração (sem dados sensíveis)"""
        logger.info(f"🔧 Ambiente: {self.environment}")
        logger.info(f"🔧 Debug: {self.debug}")
        logger.info(f"🔧 Vercel: {self.is_vercel()}")
        logger.info(f"🔧 Produção: {self.is_production()}")
        
        # APIs
        if self.zapi_instance_id and self.zapi_token:
            logger.info("✅ Z-API configurado")
        else:
            logger.warning("⚠️ Z-API não configurado completamente")
        
        if self.gestaods_token:
            logger.info("✅ GestãoDS token configurado")
        else:
            logger.warning("⚠️ GestãoDS token não configurado")
        
        # Database
        if self.database_url:
            logger.info("✅ DATABASE_URL configurada")
        
        if self.supabase_url and self.supabase_service_role_key:
            logger.info("✅ Supabase configurado")
        else:
            logger.info("ℹ️ Supabase não configurado - usando fallback")
    
    def is_vercel(self) -> bool:
        """Verifica se está rodando na Vercel"""
        return bool(os.getenv('VERCEL')) or self.environment == 'vercel'
    
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment in ['production', 'vercel']
    
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.environment in ['development', 'local']
    
    def get_database_config(self) -> dict:
        """Retorna configuração do banco"""
        return {
            "database_url": self.database_url,
            "supabase": {
                "url": self.supabase_url,
                "service_role_key": "***" if self.supabase_service_role_key else None,
                "anon_key": "***" if self.supabase_anon_key else None,
            },
            "environment": self.environment
        }
    
    def get_zapi_config(self) -> dict:
        """Retorna configuração do Z-API"""
        return {
            "instance_id": self.zapi_instance_id,
            "token": "***" if self.zapi_token else None,
            "base_url": self.zapi_base_url,
            "configured": bool(self.zapi_instance_id and self.zapi_token)
        }
    
    def get_gestaods_config(self) -> dict:
        """Retorna configuração do GestãoDS"""
        return {
            "api_url": self.gestaods_api_url,
            "token": "***" if self.gestaods_token else None,
            "configured": bool(self.gestaods_token)
        }

def create_fallback_settings():
    """Cria configurações de fallback para casos de erro crítico"""
    logger.warning("🚨 Usando configurações de fallback")
    
    class FallbackSettings:
        def __init__(self):
            # Configurações mínimas para funcionamento
            self.zapi_instance_id = ""
            self.zapi_token = ""
            self.zapi_base_url = "https://api.z-api.io"
            self.gestaods_api_url = "https://apidev.gestaods.com.br"
            self.gestaods_token = ""
            self.database_url = ""
            self.supabase_url = ""
            self.supabase_service_role_key = ""
            self.app_host = "https://chatbot-clincia.vercel.app"
            self.environment = "fallback"
            self.debug = True
            self.clinic_name = "Clínica Nassif"
            self.clinic_phone = "+553198600366"
            self.clinic_email = "contato@clinicanassif.com.br"
            self.clinic_address = "Endereço não configurado"
        
        def is_vercel(self):
            return bool(os.getenv('VERCEL'))
        
        def is_production(self):
            return False
        
        def is_development(self):
            return True
    
    return FallbackSettings()

@lru_cache()
def get_settings():
    """Obtém configurações com fallback robusto"""
    try:
        return Settings()
    except Exception as e:
        logger.error(f"❌ Erro ao carregar configurações: {str(e)}")
        return create_fallback_settings()

# Instância global das configurações
try:
    settings = get_settings()
    logger.info("✅ Configurações carregadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro crítico nas configurações: {str(e)}")
    settings = create_fallback_settings()

# Configurar logging baseado nas configurações
def setup_logging():
    """Configura o sistema de logging"""
    try:
        log_level = logging.INFO
        if settings.debug:
            log_level = logging.DEBUG
        elif settings.is_production():
            log_level = logging.WARNING
        
        # Configuração básica sem arquivo (compatível com Vercel)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Reduzir logs verbosos em produção
        if settings.is_production():
            logging.getLogger('httpx').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        
        logger.info("🔧 Sistema de logging configurado")
        
    except Exception as e:
        # Configuração mínima se tudo falhar
        logging.basicConfig(level=logging.INFO)
        logger.error(f"❌ Erro na configuração de logging: {e}")

# Configurar logging na importação
setup_logging()