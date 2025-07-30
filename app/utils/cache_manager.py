from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import json
import hashlib
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Tipos de cache disponíveis"""
    PATIENT_DATA = "patient_data"
    APPOINTMENT_SLOTS = "appointment_slots"
    PROFESSIONALS = "professionals"
    CONSULTATION_TYPES = "consultation_types"
    CONVERSATION_CONTEXT = "conversation_context"

class CacheManager:
    """Gerenciador de cache inteligente para o chatbot"""
    
    def __init__(self):
        self.cache = {}
        self.cache_metadata = {}
        self.default_ttl = {
            CacheType.PATIENT_DATA: 3600,  # 1 hora
            CacheType.APPOINTMENT_SLOTS: 300,  # 5 minutos
            CacheType.PROFESSIONALS: 7200,  # 2 horas
            CacheType.CONSULTATION_TYPES: 7200,  # 2 horas
            CacheType.CONVERSATION_CONTEXT: 1800  # 30 minutos
        }
        
        # Iniciar limpeza automática do cache
        asyncio.create_task(self._auto_cleanup())
    
    def _generate_key(self, cache_type: CacheType, identifier: str) -> str:
        """Gera chave única para o cache"""
        key_data = f"{cache_type.value}:{identifier}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_context_key(self, phone: str, context_data: Dict) -> str:
        """Gera chave para contexto de conversa"""
        context_str = json.dumps(context_data, sort_keys=True)
        return self._generate_key(CacheType.CONVERSATION_CONTEXT, f"{phone}:{context_str}")
    
    async def get(self, cache_type: CacheType, identifier: str) -> Optional[Any]:
        """Obtém dados do cache"""
        key = self._generate_key(cache_type, identifier)
        
        if key not in self.cache:
            return None
        
        # Verificar se o cache expirou
        if self._is_expired(key):
            await self.delete(cache_type, identifier)
            return None
        
        logger.debug(f"Cache hit: {cache_type.value} - {identifier}")
        return self.cache[key]
    
    async def set(self, cache_type: CacheType, identifier: str, data: Any, ttl: Optional[int] = None) -> None:
        """Armazena dados no cache"""
        key = self._generate_key(cache_type, identifier)
        
        if ttl is None:
            ttl = self.default_ttl[cache_type]
        
        self.cache[key] = data
        self.cache_metadata[key] = {
            "type": cache_type.value,
            "identifier": identifier,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "ttl": ttl
        }
        
        logger.debug(f"Cache set: {cache_type.value} - {identifier} (TTL: {ttl}s)")
    
    async def delete(self, cache_type: CacheType, identifier: str) -> None:
        """Remove dados do cache"""
        key = self._generate_key(cache_type, identifier)
        
        if key in self.cache:
            del self.cache[key]
            del self.cache_metadata[key]
            logger.debug(f"Cache deleted: {cache_type.value} - {identifier}")
    
    async def clear_type(self, cache_type: CacheType) -> None:
        """Limpa todos os dados de um tipo específico"""
        keys_to_delete = []
        
        for key, metadata in self.cache_metadata.items():
            if metadata["type"] == cache_type.value:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]
            del self.cache_metadata[key]
        
        logger.info(f"Cleared {len(keys_to_delete)} cache entries for {cache_type.value}")
    
    async def clear_all(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        self.cache_metadata.clear()
        logger.info("All cache cleared")
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se o cache expirou"""
        if key not in self.cache_metadata:
            return True
        
        metadata = self.cache_metadata[key]
        return datetime.now() > metadata["expires_at"]
    
    async def _auto_cleanup(self) -> None:
        """Limpeza automática do cache expirado"""
        while True:
            try:
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
                
                keys_to_delete = []
                for key, metadata in self.cache_metadata.items():
                    if self._is_expired(key):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.cache[key]
                    del self.cache_metadata[key]
                
                if keys_to_delete:
                    logger.info(f"Auto-cleanup: removed {len(keys_to_delete)} expired cache entries")
                    
            except Exception as e:
                logger.error(f"Error in cache auto-cleanup: {e}")
    
    # Métodos específicos para diferentes tipos de dados
    
    async def get_patient_data(self, cpf: str) -> Optional[Dict]:
        """Obtém dados do paciente do cache"""
        return await self.get(CacheType.PATIENT_DATA, cpf)
    
    async def set_patient_data(self, cpf: str, patient_data: Dict) -> None:
        """Armazena dados do paciente no cache"""
        await self.set(CacheType.PATIENT_DATA, cpf, patient_data)
    
    async def get_appointment_slots(self, date: str, professional: str = None) -> Optional[List[Dict]]:
        """Obtém horários disponíveis do cache"""
        identifier = f"{date}:{professional or 'all'}"
        return await self.get(CacheType.APPOINTMENT_SLOTS, identifier)
    
    async def set_appointment_slots(self, date: str, slots: List[Dict], professional: str = None) -> None:
        """Armazena horários disponíveis no cache"""
        identifier = f"{date}:{professional or 'all'}"
        await self.set(CacheType.APPOINTMENT_SLOTS, identifier, slots)
    
    async def get_professionals(self) -> Optional[List[Dict]]:
        """Obtém lista de profissionais do cache"""
        return await self.get(CacheType.PROFESSIONALS, "all")
    
    async def set_professionals(self, professionals: List[Dict]) -> None:
        """Armazena lista de profissionais no cache"""
        await self.set(CacheType.PROFESSIONALS, "all", professionals)
    
    async def get_consultation_types(self) -> Optional[List[Dict]]:
        """Obtém tipos de consulta do cache"""
        return await self.get(CacheType.CONSULTATION_TYPES, "all")
    
    async def set_consultation_types(self, types: List[Dict]) -> None:
        """Armazena tipos de consulta no cache"""
        await self.set(CacheType.CONSULTATION_TYPES, "all", types)
    
    async def get_conversation_context(self, phone: str, context_data: Dict) -> Optional[Dict]:
        """Obtém contexto de conversa do cache"""
        key = self._generate_context_key(phone, context_data)
        return await self.get(CacheType.CONVERSATION_CONTEXT, key)
    
    async def set_conversation_context(self, phone: str, context_data: Dict, context: Dict) -> None:
        """Armazena contexto de conversa no cache"""
        key = self._generate_context_key(phone, context_data)
        await self.set(CacheType.CONVERSATION_CONTEXT, key, context)
    
    # Métodos de invalidação inteligente
    
    async def invalidate_patient_cache(self, cpf: str) -> None:
        """Invalida cache relacionado a um paciente específico"""
        await self.delete(CacheType.PATIENT_DATA, cpf)
        # Também invalidar slots de agendamento que podem ter mudado
        await self.clear_type(CacheType.APPOINTMENT_SLOTS)
        logger.info(f"Invalidated cache for patient: {cpf}")
    
    async def invalidate_appointment_cache(self, date: str = None) -> None:
        """Invalida cache de agendamentos"""
        if date:
            # Invalidar apenas para uma data específica
            await self.clear_type(CacheType.APPOINTMENT_SLOTS)
        else:
            # Invalidar todos os slots
            await self.clear_type(CacheType.APPOINTMENT_SLOTS)
        logger.info(f"Invalidated appointment cache for date: {date or 'all'}")
    
    async def invalidate_professional_cache(self) -> None:
        """Invalida cache de profissionais"""
        await self.clear_type(CacheType.PROFESSIONALS)
        logger.info("Invalidated professionals cache")
    
    # Métodos de estatísticas
    
    def get_cache_stats(self) -> Dict:
        """Obtém estatísticas do cache"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for key in self.cache_metadata if self._is_expired(key))
        
        type_counts = {}
        for metadata in self.cache_metadata.values():
            cache_type = metadata["type"]
            type_counts[cache_type] = type_counts.get(cache_type, 0) + 1
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "valid_entries": total_entries - expired_entries,
            "type_counts": type_counts,
            "memory_usage_mb": self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estima uso de memória do cache em MB"""
        try:
            import sys
            total_size = 0
            
            # Tamanho dos dados
            for key, value in self.cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
            
            # Tamanho dos metadados
            for key, metadata in self.cache_metadata.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(metadata)
            
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    # Métodos de cache inteligente
    
    async def get_or_set(self, cache_type: CacheType, identifier: str, 
                        fetch_func, ttl: Optional[int] = None) -> Any:
        """Obtém do cache ou busca e armazena se não existir"""
        cached_data = await self.get(cache_type, identifier)
        
        if cached_data is not None:
            return cached_data
        
        # Buscar dados
        try:
            data = await fetch_func()
            if data is not None:
                await self.set(cache_type, identifier, data, ttl)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for cache: {e}")
            return None
    
    async def refresh_cache(self, cache_type: CacheType, identifier: str, 
                          fetch_func, ttl: Optional[int] = None) -> Any:
        """Força atualização do cache"""
        try:
            data = await fetch_func()
            if data is not None:
                await self.set(cache_type, identifier, data, ttl)
            return data
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            return None 