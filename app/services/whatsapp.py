import httpx
from typing import Optional, List, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        self.headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }

    async def send_text(self, phone: str, message: str, delay_message: int = 2):
        """Envia mensagem de texto simples"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "phone": self._format_phone(phone),
                    "message": message,
                    "delayMessage": delay_message
                }

                response = await client.post(
                    f"{self.base_url}/send-text",
                    json=payload,
                    headers=self.headers
                )

                if response.status_code == 200:
                    logger.info(f"Mensagem enviada para {phone}")
                    return response.json()
                else:
                    logger.error(f"Erro ao enviar mensagem: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro na comunicação com Z-API: {str(e)}")
            return None

    async def send_button_list(self, phone: str, message: str,
                             buttons: List[Dict[str, str]],
                             title: str = "Opções"):
        """Envia mensagem com lista de botões"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "phone": self._format_phone(phone),
                    "message": message,
                    "buttonList": {
                        "buttons": buttons
                    },
                    "title": title,
                    "footer": settings.clinic_name
                }

                response = await client.post(
                    f"{self.base_url}/send-button-list",
                    json=payload,
                    headers=self.headers
                )

                return response.json() if response.status_code == 200 else None

        except Exception as e:
            logger.error(f"Erro ao enviar botões: {str(e)}")
            return None

    async def send_link(self, phone: str, message: str, link: str):
        """Envia mensagem com link"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "phone": self._format_phone(phone),
                    "message": message,
                    "linkUrl": link,
                    "title": "Clique aqui",
                    "linkDescription": "Acesse o link para mais informações"
                }

                response = await client.post(
                    f"{self.base_url}/send-link",
                    json=payload,
                    headers=self.headers
                )

                return response.json() if response.status_code == 200 else None

        except Exception as e:
            logger.error(f"Erro ao enviar link: {str(e)}")
            return None

    async def mark_as_read(self, phone: str, message_id: str):
        """Marca mensagem como lida"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "phone": self._format_phone(phone),
                    "messageId": message_id
                }

                await client.post(
                    f"{self.base_url}/read-message",
                    json=payload,
                    headers=self.headers
                )

        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {str(e)}")

    def _format_phone(self, phone: str) -> str:
        """Formata número de telefone para padrão Z-API"""
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))

        # Adiciona código do país se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone

        # Adiciona 9 se for celular e não tiver
        if len(phone) == 12 and phone[4] != '9':
            phone = phone[:4] + '9' + phone[4:]

        return phone + '@c.us' 