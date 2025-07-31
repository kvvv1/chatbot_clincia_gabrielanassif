import httpx
from typing import Optional, List, Dict
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço robusto para integração com Z-API"""
    
    def __init__(self):
        self.base_url = f"{settings.zapi_base_url}/instances/{settings.zapi_instance_id}/token/{settings.zapi_token}"
        self.headers = {
            "Client-Token": settings.zapi_client_token,
            "Content-Type": "application/json"
        }
        self.timeout = 30
        self.max_retries = 3
        
        # Validar configurações
        self._validate_config()
    
    def _validate_config(self):
        """Valida se as configurações estão corretas"""
        required = ['zapi_base_url', 'zapi_instance_id', 'zapi_token', 'zapi_client_token']
        missing = []
        
        for field in required:
            if not getattr(settings, field, None):
                missing.append(field)
        
        if missing:
            logger.error(f"❌ Configurações Z-API faltando: {missing}")
            logger.error("Configure as variáveis de ambiente necessárias")
        else:
            logger.info("✅ Configurações Z-API validadas com sucesso")
    
    async def send_text(self, phone: str, message: str, delay_message: int = 2) -> Optional[Dict]:
        """
        Envia mensagem de texto com retry e tratamento de erros
        
        Args:
            phone: Número do telefone
            message: Mensagem a enviar
            delay_message: Delay em segundos antes de enviar
            
        Returns:
            Response da API ou None em caso de erro
        """
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "message": message,
            "delayMessage": delay_message
        }
        
        # Tentar enviar com retry
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{self.max_retries} - Enviando mensagem para {formatted_phone}")
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/send-text",
                        json=payload,
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Mensagem enviada com sucesso para {phone}")
                        return response.json()
                    elif response.status_code == 429:  # Rate limit
                        logger.warning("Rate limit atingido, aguardando...")
                        await asyncio.sleep(5 * (attempt + 1))  # Backoff exponencial
                        continue
                    else:
                        logger.error(f"Erro na API: {response.status_code} - {response.text}")
                        
            except httpx.TimeoutException:
                logger.error(f"Timeout ao enviar mensagem (tentativa {attempt + 1})")
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem: {str(e)}")
                
        logger.error(f"❌ Falha ao enviar mensagem após {self.max_retries} tentativas")
        return None
    
    async def send_message(self, phone: str, message: str, delay_message: int = 2) -> Optional[Dict]:
        """Alias para send_text - mantém compatibilidade"""
        return await self.send_text(phone, message, delay_message)
    
    async def send_button_list(self, phone: str, message: str, buttons: List[Dict[str, str]], 
                             title: str = "Opções", footer: str = None) -> Optional[Dict]:
        """
        Envia mensagem com lista de botões
        
        Args:
            phone: Número do telefone
            message: Mensagem principal
            buttons: Lista de botões [{"id": "1", "text": "Opção 1"}]
            title: Título da lista
            footer: Rodapé da mensagem
        """
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "message": message,
            "title": title,
            "footer": footer or settings.clinic_name,
            "sections": [{
                "title": title,
                "rows": buttons
            }]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send-button-list",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Lista de botões enviada para {phone}")
                    return response.json()
                else:
                    logger.error(f"Erro ao enviar botões: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao enviar lista de botões: {str(e)}")
            return None
    
    async def send_link(self, phone: str, message: str, link: str, 
                       link_title: str = "Clique aqui",
                       link_description: str = "Acesse o link para mais informações") -> Optional[Dict]:
        """Envia mensagem com link"""
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "message": message,
            "linkUrl": link,
            "title": link_title,
            "linkDescription": link_description
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send-link",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Link enviado para {phone}")
                    return response.json()
                else:
                    logger.error(f"Erro ao enviar link: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao enviar link: {str(e)}")
            return None
    
    async def mark_as_read(self, phone: str, message_id: str) -> bool:
        """Marca mensagem como lida"""
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "messageId": message_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/read-message",
                    json=payload,
                    headers=self.headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {str(e)}")
            return False
    
    async def send_location(self, phone: str, latitude: float, longitude: float,
                          name: str = None, address: str = None) -> Optional[Dict]:
        """Envia localização"""
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "latitude": latitude,
            "longitude": longitude,
            "name": name or settings.clinic_name,
            "address": address or settings.clinic_address
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send-location",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Localização enviada para {phone}")
                    return response.json()
                else:
                    logger.error(f"Erro ao enviar localização: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao enviar localização: {str(e)}")
            return None
    
    async def check_status(self) -> Dict:
        """Verifica status da instância Z-API"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"connected": False, "error": f"Status code: {response.status_code}"}
                    
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def _format_phone(self, phone: str) -> str:
        """
        Formata número de telefone para padrão Z-API
        
        Formato esperado: 5511999999999@c.us
        """
        # Remove caracteres não numéricos
        phone_clean = ''.join(filter(str.isdigit, phone))
        
        # Remove @c.us se já tiver
        if phone_clean.endswith('@c.us'):
            phone_clean = phone_clean.replace('@c.us', '')
        
        # Adiciona código do país se não tiver
        if not phone_clean.startswith('55'):
            phone_clean = '55' + phone_clean
        
        # Adiciona 9 dígito se for celular de SP e não tiver
        if len(phone_clean) == 12 and phone_clean[2:4] in ['11', '12', '13', '14', '15', '16', '17', '18', '19']:
            if phone_clean[4] != '9':
                phone_clean = phone_clean[:4] + '9' + phone_clean[4:]
        
        # Adiciona sufixo do WhatsApp
        return phone_clean + '@c.us'
    
    async def send_typing(self, phone: str, duration: int = 3) -> bool:
        """Simula digitação por alguns segundos"""
        formatted_phone = self._format_phone(phone)
        
        payload = {
            "phone": formatted_phone,
            "duration": duration * 1000  # Converter para milissegundos
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send-typing",
                    json=payload,
                    headers=self.headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Erro ao enviar typing: {str(e)}")
            return False