"""
Serviço para integração com Supabase
"""
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.base_url = settings.supabase_url
        self.anon_key = settings.supabase_anon_key
        self.service_role_key = settings.supabase_service_role_key
        
        # Verificar se as configurações estão presentes
        if not self.base_url or not self.anon_key:
            logger.warning("Configurações do Supabase não encontradas. Serviço funcionará em modo mock.")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        self.headers = {
            "apikey": self.anon_key or "",
            "Authorization": f"Bearer {self.anon_key or ''}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def test_connection(self) -> bool:
        """Testa conexão com Supabase"""
        if self.mock_mode:
            logger.info("Modo mock ativo - retornando sucesso simulado")
            return True
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao testar conexão Supabase: {str(e)}")
            return False
    
    async def create_conversation(self, phone: str, state: str = "inicio", context: Dict = None) -> Optional[Dict]:
        """Cria nova conversa"""
        if self.mock_mode:
            logger.info(f"Modo mock - criando conversa simulada para {phone}")
            return {
                "id": "mock-conversation-id",
                "phone": phone,
                "state": state,
                "context": context or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
        try:
            payload = {
                "phone": phone,
                "state": state,
                "context": context or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/conversations",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return response.json()[0] if response.json() else None
                else:
                    logger.error(f"Erro ao criar conversa: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao criar conversa: {str(e)}")
            return None
    
    async def get_conversation(self, phone: str) -> Optional[Dict]:
        """Busca conversa por telefone"""
        if self.mock_mode:
            logger.info(f"Modo mock - buscando conversa simulada para {phone}")
            return {
                "id": "mock-conversation-id",
                "phone": phone,
                "state": "inicio",
                "context": {},
                "created_at": datetime.utcnow().isoformat()
            }
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/conversations",
                    headers=self.headers,
                    params={"phone": f"eq.{phone}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data[0] if data else None
                else:
                    logger.error(f"Erro ao buscar conversa: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar conversa: {str(e)}")
            return None
    
    async def update_conversation(self, conversation_id: str, updates: Dict) -> bool:
        """Atualiza conversa"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/rest/v1/conversations",
                    headers=self.headers,
                    params={"id": f"eq.{conversation_id}"},
                    json=updates,
                    timeout=30.0
                )
                
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"Erro ao atualizar conversa: {str(e)}")
            return False
    
    async def create_appointment(self, appointment_data: Dict) -> Optional[Dict]:
        """Cria novo agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/appointments",
                    headers=self.headers,
                    json=appointment_data,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return response.json()[0] if response.json() else None
                else:
                    logger.error(f"Erro ao criar agendamento: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            return None
    
    async def get_appointments_by_patient(self, patient_id: str) -> List[Dict]:
        """Busca agendamentos por paciente"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/appointments",
                    headers=self.headers,
                    params={"patient_id": f"eq.{patient_id}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar agendamentos: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar agendamentos: {str(e)}")
            return []
    
    async def get_appointments_by_date(self, date: datetime) -> List[Dict]:
        """Busca agendamentos por data"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/appointments",
                    headers=self.headers,
                    params={
                        "appointment_date": f"gte.{date_str}T00:00:00",
                        "appointment_date": f"lte.{date_str}T23:59:59"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar agendamentos por data: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar agendamentos por data: {str(e)}")
            return []
    
    async def update_appointment(self, appointment_id: str, updates: Dict) -> bool:
        """Atualiza agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/rest/v1/appointments",
                    headers=self.headers,
                    params={"id": f"eq.{appointment_id}"},
                    json=updates,
                    timeout=30.0
                )
                
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"Erro ao atualizar agendamento: {str(e)}")
            return False
    
    async def add_to_waiting_list(self, waiting_data: Dict) -> Optional[Dict]:
        """Adiciona paciente à lista de espera"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/waiting_list",
                    headers=self.headers,
                    json=waiting_data,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return response.json()[0] if response.json() else None
                else:
                    logger.error(f"Erro ao adicionar à lista de espera: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao adicionar à lista de espera: {str(e)}")
            return None
    
    async def get_waiting_list(self, priority: Optional[int] = None) -> List[Dict]:
        """Busca lista de espera"""
        try:
            params = {}
            if priority is not None:
                params["priority"] = f"eq.{priority}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/waiting_list",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar lista de espera: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar lista de espera: {str(e)}")
            return []
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas para o dashboard"""
        try:
            stats = {}
            
            # Contar conversas
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/conversations",
                    headers=self.headers,
                    params={"select": "count"},
                    timeout=30.0
                )
                if response.status_code == 200:
                    stats["total_conversations"] = response.json()[0]["count"]
                
                # Contar agendamentos
                response = await client.get(
                    f"{self.base_url}/rest/v1/appointments",
                    headers=self.headers,
                    params={"select": "count"},
                    timeout=30.0
                )
                if response.status_code == 200:
                    stats["total_appointments"] = response.json()[0]["count"]
                
                # Contar lista de espera
                response = await client.get(
                    f"{self.base_url}/rest/v1/waiting_list",
                    headers=self.headers,
                    params={"select": "count"},
                    timeout=30.0
                )
                if response.status_code == 200:
                    stats["total_waiting"] = response.json()[0]["count"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {} 