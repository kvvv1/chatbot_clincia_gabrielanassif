"""
Serviço para integração com o widget da GestãoDS
Baseado na documentação: https://apidev.gestaods.com.br/redoc
"""
import httpx
from typing import Optional, Dict, List
from datetime import datetime
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GestaoDSWidget:
    def __init__(self):
        self.base_url = settings.gestaods_api_url
        self.token = settings.gestaods_token
        self.widget_url = f"https://calendario.gestaods.com.br/?token={self.token}"
        
    def get_widget_embed_code(self, width: int = 1200, height: int = 800) -> str:
        """Gera código HTML para embedar o widget da GestãoDS"""
        return f'''
        <iframe 
            frameborder="0" 
            width="{width}" 
            height="{height}" 
            src="{self.widget_url}">
        </iframe>
        '''
    
    def get_widget_url(self) -> str:
        """Retorna URL direta do widget"""
        return self.widget_url
    
    async def get_widget_config(self) -> Dict:
        """Obtém configuração do widget"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/widget/config/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao obter configuração do widget: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Erro ao obter configuração do widget: {str(e)}")
            return {}
    
    async def get_available_slots(self, date: datetime) -> List[Dict]:
        """Obtém horários disponíveis para uma data específica"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "data": date.strftime("%Y-%m-%d"),
                    "token": self.token
                }
                
                response = await client.get(
                    f"{self.base_url}/api/widget/slots/",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao obter horários: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao obter horários: {str(e)}")
            return []
    
    async def create_appointment_via_widget(self, 
                                          patient_data: Dict, 
                                          slot_id: str,
                                          notes: str = "") -> Optional[Dict]:
        """Cria agendamento via widget"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "patient": patient_data,
                    "slot_id": slot_id,
                    "notes": notes,
                    "source": "whatsapp_bot"
                }
                
                response = await client.post(
                    f"{self.base_url}/api/widget/appointment/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Erro ao criar agendamento: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            return None
    
    def get_share_modal_data(self) -> Dict:
        """Retorna dados para modal de compartilhamento"""
        return {
            "title": "Compartilhar",
            "instructions": "Clique no bloco ao lado para copiar o código para a área de transferência, na sequência, cole o mesmo no código HTML de seu site.",
            "embed_code": self.get_widget_embed_code(),
            "widget_url": self.widget_url,
            "token": self.token,
            "documentation_url": "https://apidev.gestaods.com.br/redoc"
        } 