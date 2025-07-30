from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import json
import logging
from collections import defaultdict, Counter
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Tipos de eventos que podem ser rastreados"""
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    STATE_CHANGE = "state_change"
    API_CALL = "api_call"
    API_ERROR = "api_error"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    USER_ACTION = "user_action"
    CONVERSATION_START = "conversation_start"
    CONVERSATION_END = "conversation_end"
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    ERROR_OCCURRED = "error_occurred"

class AnalyticsManager:
    """Gerenciador de analytics e monitoramento para o chatbot"""
    
    def __init__(self):
        self.events = []
        self.daily_stats = defaultdict(lambda: {
            "total_messages": 0,
            "total_conversations": 0,
            "total_appointments": 0,
            "total_cancellations": 0,
            "total_errors": 0,
            "api_calls": 0,
            "api_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "state_transitions": defaultdict(int),
            "user_actions": defaultdict(int),
            "error_types": defaultdict(int),
            "response_times": []
        })
        
        self.active_conversations = set()
        self.conversation_start_times = {}
        
        # Iniciar limpeza automática de dados antigos
        asyncio.create_task(self._auto_cleanup())
    
    async def track_event(self, event_type: EventType, data: Dict = None, phone: str = None):
        """Registra um evento no sistema de analytics"""
        event = {
            "timestamp": datetime.now(),
            "event_type": event_type.value,
            "phone": phone,
            "data": data or {}
        }
        
        self.events.append(event)
        
        # Atualizar estatísticas diárias
        today = datetime.now().date()
        daily_key = today.isoformat()
        
        if event_type == EventType.MESSAGE_RECEIVED:
            self.daily_stats[daily_key]["total_messages"] += 1
            
        elif event_type == EventType.CONVERSATION_START:
            self.daily_stats[daily_key]["total_conversations"] += 1
            self.active_conversations.add(phone)
            self.conversation_start_times[phone] = datetime.now()
            
        elif event_type == EventType.CONVERSATION_END:
            if phone in self.active_conversations:
                self.active_conversations.remove(phone)
            if phone in self.conversation_start_times:
                del self.conversation_start_times[phone]
                
        elif event_type == EventType.APPOINTMENT_CREATED:
            self.daily_stats[daily_key]["total_appointments"] += 1
            
        elif event_type == EventType.APPOINTMENT_CANCELLED:
            self.daily_stats[daily_key]["total_cancellations"] += 1
            
        elif event_type == EventType.API_CALL:
            self.daily_stats[daily_key]["api_calls"] += 1
            
        elif event_type == EventType.API_ERROR:
            self.daily_stats[daily_key]["api_errors"] += 1
            self.daily_stats[daily_key]["total_errors"] += 1
            if "error_type" in data:
                self.daily_stats[daily_key]["error_types"][data["error_type"]] += 1
                
        elif event_type == EventType.CACHE_HIT:
            self.daily_stats[daily_key]["cache_hits"] += 1
            
        elif event_type == EventType.CACHE_MISS:
            self.daily_stats[daily_key]["cache_misses"] += 1
            
        elif event_type == EventType.STATE_CHANGE:
            if "from_state" in data and "to_state" in data:
                transition = f"{data['from_state']} -> {data['to_state']}"
                self.daily_stats[daily_key]["state_transitions"][transition] += 1
                
        elif event_type == EventType.USER_ACTION:
            if "action" in data:
                self.daily_stats[daily_key]["user_actions"][data["action"]] += 1
                
        elif event_type == EventType.ERROR_OCCURRED:
            self.daily_stats[daily_key]["total_errors"] += 1
            if "error_type" in data:
                self.daily_stats[daily_key]["error_types"][data["error_type"]] += 1
        
        # Registrar tempo de resposta se disponível
        if "response_time" in data:
            self.daily_stats[daily_key]["response_times"].append(data["response_time"])
        
        logger.debug(f"Event tracked: {event_type.value} for {phone}")
    
    async def track_message_received(self, phone: str, message: str, message_id: str):
        """Registra recebimento de mensagem"""
        await self.track_event(EventType.MESSAGE_RECEIVED, {
            "message_length": len(message),
            "message_id": message_id,
            "has_media": False  # Implementar detecção de mídia se necessário
        }, phone)
    
    async def track_message_sent(self, phone: str, message: str, response_time: float = None):
        """Registra envio de mensagem"""
        data = {
            "message_length": len(message),
            "response_time": response_time
        }
        await self.track_event(EventType.MESSAGE_SENT, data, phone)
    
    async def track_state_change(self, phone: str, from_state: str, to_state: str):
        """Registra mudança de estado"""
        await self.track_event(EventType.STATE_CHANGE, {
            "from_state": from_state,
            "to_state": to_state
        }, phone)
    
    async def track_api_call(self, api_name: str, success: bool, response_time: float = None, error: str = None):
        """Registra chamada de API"""
        data = {
            "api_name": api_name,
            "success": success,
            "response_time": response_time
        }
        
        if not success:
            data["error"] = error
            await self.track_event(EventType.API_ERROR, data)
        else:
            await self.track_event(EventType.API_CALL, data)
    
    async def track_cache_operation(self, cache_type: str, hit: bool):
        """Registra operação de cache"""
        event_type = EventType.CACHE_HIT if hit else EventType.CACHE_MISS
        await self.track_event(event_type, {"cache_type": cache_type})
    
    async def track_user_action(self, phone: str, action: str, context: Dict = None):
        """Registra ação do usuário"""
        data = {"action": action}
        if context:
            data.update(context)
        await self.track_event(EventType.USER_ACTION, data, phone)
    
    async def track_appointment_created(self, phone: str, appointment_data: Dict):
        """Registra criação de agendamento"""
        await self.track_event(EventType.APPOINTMENT_CREATED, appointment_data, phone)
    
    async def track_appointment_cancelled(self, phone: str, appointment_data: Dict):
        """Registra cancelamento de agendamento"""
        await self.track_event(EventType.APPOINTMENT_CANCELLED, appointment_data, phone)
    
    async def track_error(self, phone: str, error_type: str, error_message: str, context: Dict = None):
        """Registra erro"""
        data = {
            "error_type": error_type,
            "error_message": error_message
        }
        if context:
            data.update(context)
        await self.track_event(EventType.ERROR_OCCURRED, data, phone)
    
    # Métodos de análise e relatórios
    
    def get_daily_stats(self, date: datetime = None) -> Dict:
        """Obtém estatísticas de um dia específico"""
        if date is None:
            date = datetime.now()
        
        daily_key = date.date().isoformat()
        stats = self.daily_stats.get(daily_key, {})
        
        # Calcular métricas derivadas
        if stats.get("response_times"):
            response_times = stats["response_times"]
            stats["avg_response_time"] = sum(response_times) / len(response_times)
            stats["min_response_time"] = min(response_times)
            stats["max_response_time"] = max(response_times)
        
        if stats.get("api_calls", 0) > 0:
            stats["api_error_rate"] = stats.get("api_errors", 0) / stats["api_calls"]
        
        if stats.get("cache_hits", 0) + stats.get("cache_misses", 0) > 0:
            total_cache_ops = stats["cache_hits"] + stats["cache_misses"]
            stats["cache_hit_rate"] = stats["cache_hits"] / total_cache_ops
        
        return stats
    
    def get_weekly_stats(self, end_date: datetime = None) -> Dict:
        """Obtém estatísticas da semana"""
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=7)
        weekly_stats = {
            "total_messages": 0,
            "total_conversations": 0,
            "total_appointments": 0,
            "total_cancellations": 0,
            "total_errors": 0,
            "api_calls": 0,
            "api_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "daily_breakdown": {}
        }
        
        current_date = start_date
        while current_date <= end_date:
            daily_key = current_date.date().isoformat()
            daily_stats = self.daily_stats.get(daily_key, {})
            
            weekly_stats["daily_breakdown"][daily_key] = daily_stats
            
            # Acumular totais
            for key in ["total_messages", "total_conversations", "total_appointments", 
                       "total_cancellations", "total_errors", "api_calls", "api_errors", 
                       "cache_hits", "cache_misses"]:
                weekly_stats[key] += daily_stats.get(key, 0)
        
        return weekly_stats
    
    def get_conversation_metrics(self, phone: str) -> Dict:
        """Obtém métricas de uma conversa específica"""
        conversation_events = [e for e in self.events if e.get("phone") == phone]
        
        if not conversation_events:
            return {}
        
        start_time = conversation_events[0]["timestamp"]
        end_time = conversation_events[-1]["timestamp"]
        duration = (end_time - start_time).total_seconds()
        
        message_count = len([e for e in conversation_events if e["event_type"] == EventType.MESSAGE_RECEIVED.value])
        state_changes = len([e for e in conversation_events if e["event_type"] == EventType.STATE_CHANGE.value])
        
        return {
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": duration,
            "message_count": message_count,
            "state_changes": state_changes,
            "events": conversation_events
        }
    
    def get_performance_metrics(self, days: int = 7) -> Dict:
        """Obtém métricas de performance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_response_times = []
        all_api_calls = 0
        all_api_errors = 0
        all_cache_hits = 0
        all_cache_misses = 0
        
        current_date = start_date
        while current_date <= end_date:
            daily_key = current_date.date().isoformat()
            daily_stats = self.daily_stats.get(daily_key, {})
            
            all_response_times.extend(daily_stats.get("response_times", []))
            all_api_calls += daily_stats.get("api_calls", 0)
            all_api_errors += daily_stats.get("api_errors", 0)
            all_cache_hits += daily_stats.get("cache_hits", 0)
            all_cache_misses += daily_stats.get("cache_misses", 0)
            
            current_date += timedelta(days=1)
        
        metrics = {
            "period_days": days,
            "total_api_calls": all_api_calls,
            "total_api_errors": all_api_errors,
            "api_error_rate": all_api_errors / all_api_calls if all_api_calls > 0 else 0,
            "total_cache_operations": all_cache_hits + all_cache_misses,
            "cache_hit_rate": all_cache_hits / (all_cache_hits + all_cache_misses) if (all_cache_hits + all_cache_misses) > 0 else 0
        }
        
        if all_response_times:
            metrics.update({
                "avg_response_time": sum(all_response_times) / len(all_response_times),
                "min_response_time": min(all_response_times),
                "max_response_time": max(all_response_times),
                "response_time_count": len(all_response_times)
            })
        
        return metrics
    
    def get_top_states(self, days: int = 7) -> List[tuple]:
        """Obtém os estados mais utilizados"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        state_counter = Counter()
        
        current_date = start_date
        while current_date <= end_date:
            daily_key = current_date.date().isoformat()
            daily_stats = self.daily_stats.get(daily_key, {})
            
            for transition, count in daily_stats.get("state_transitions", {}).items():
                to_state = transition.split(" -> ")[1]
                state_counter[to_state] += count
            
            current_date += timedelta(days=1)
        
        return state_counter.most_common(10)
    
    def get_top_errors(self, days: int = 7) -> List[tuple]:
        """Obtém os erros mais comuns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        error_counter = Counter()
        
        current_date = start_date
        while current_date <= end_date:
            daily_key = current_date.date().isoformat()
            daily_stats = self.daily_stats.get(daily_key, {})
            
            for error_type, count in daily_stats.get("error_types", {}).items():
                error_counter[error_type] += count
            
            current_date += timedelta(days=1)
        
        return error_counter.most_common(10)
    
    async def _auto_cleanup(self):
        """Limpeza automática de dados antigos"""
        while True:
            try:
                await asyncio.sleep(3600)  # Verificar a cada hora
                
                # Manter apenas eventos dos últimos 30 dias
                cutoff_date = datetime.now() - timedelta(days=30)
                self.events = [e for e in self.events if e["timestamp"] > cutoff_date]
                
                # Manter apenas estatísticas dos últimos 90 dias
                cutoff_date = datetime.now() - timedelta(days=90)
                cutoff_key = cutoff_date.date().isoformat()
                
                keys_to_remove = [k for k in self.daily_stats.keys() if k < cutoff_key]
                for key in keys_to_remove:
                    del self.daily_stats[key]
                
                if keys_to_remove:
                    logger.info(f"Analytics cleanup: removed {len(keys_to_remove)} old daily stats")
                    
            except Exception as e:
                logger.error(f"Error in analytics auto-cleanup: {e}")
    
    def export_data(self, format: str = "json") -> str:
        """Exporta dados de analytics"""
        if format == "json":
            return json.dumps({
                "events": self.events,
                "daily_stats": dict(self.daily_stats),
                "active_conversations": list(self.active_conversations),
                "export_timestamp": datetime.now().isoformat()
            }, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}") 