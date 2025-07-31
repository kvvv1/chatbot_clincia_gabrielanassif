import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.config import settings
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

class GestaoDS:
    """Classe para integração com a API GestãoDS - Versão Alinhada com Documentação"""
    
    def __init__(self):
        self.base_url = settings.gestaods_api_url.rstrip('/')
        self.token = settings.gestaods_token
        self.timeout = 30
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        
        # Detectar ambiente (dev vs prod)
        self.is_dev = "apidev" in self.base_url or settings.environment == "development"
        self.env_prefix = "dev-" if self.is_dev else ""
        
        logger.info(f"GestãoDS inicializado - URL: {self.base_url}")
        logger.info(f"Ambiente: {'desenvolvimento' if self.is_dev else 'produção'}")
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Faz requisição HTTP com tratamento de erros melhorado"""
        url = f"{self.base_url}{endpoint}"
        
        # Substituir token na URL se necessário
        url = url.replace("{token}", self.token)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"{method} {url}")
                
                response = await client.request(method, url, **kwargs)
                
                logger.info(f"Response: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Recurso não encontrado: {url}")
                    return None
                elif response.status_code == 422:
                    # Erro de validação - extrair detalhes
                    try:
                        error_detail = response.json()
                        logger.error(f"Erro de validação (422): {error_detail}")
                        return {"validation_error": True, "detail": error_detail}
                    except:
                        logger.error(f"Erro de validação (422): {response.text}")
                        return {"validation_error": True, "detail": response.text}
                else:
                    logger.error(f"Erro na API: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout na requisição: {url}")
            return None
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None
    
    async def buscar_paciente_cpf(self, cpf: str) -> Optional[Dict]:
        """
        Busca paciente por CPF
        GET /api/paciente/{token}/{cpf}/ (prod)
        GET /api/dev-paciente/{token}/{cpf}/ (dev)
        """
        # Limpar CPF
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_limpo) != 11:
            logger.error(f"CPF inválido: {cpf}")
            return None
        
        # Verificar cache
        cache_key = f"paciente_{cpf_limpo}"
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_ttl:
                logger.info("Retornando paciente do cache")
                return cached_data
        
        # Buscar na API - usar endpoint correto baseado no ambiente
        endpoint = f"/api/{self.env_prefix}paciente/{self.token}/{cpf_limpo}/"
        result = await self._request("GET", endpoint)
        
        if result:
            # Verificar se é erro de validação
            if isinstance(result, dict) and result.get("validation_error"):
                logger.error(f"Erro de validação ao buscar paciente: {result.get('detail')}")
                return None
            
            # API retorna lista, pegar primeiro item
            if isinstance(result, list) and len(result) > 0:
                paciente = result[0]
                # Adicionar ao cache
                self._cache[cache_key] = (paciente, datetime.now().timestamp())
                return paciente
            elif isinstance(result, dict):
                # Se retornar dict direto
                self._cache[cache_key] = (result, datetime.now().timestamp())
                return result
        
        return None
    
    async def buscar_dias_disponiveis(self, data: Optional[str] = None) -> List[Dict]:
        """
        Busca dias disponíveis para agendamento
        GET /api/agendamento/dias-disponiveis/{token} (prod)
        GET /api/dev-agendamento/dias-disponiveis/{token} (dev)
        """
        endpoint = f"/api/{self.env_prefix}agendamento/dias-disponiveis/{self.token}"
        params = {}
        if data:
            params["data"] = data
        
        result = await self._request("GET", endpoint, params=params)
        
        if result:
            # Verificar se é erro de validação
            if isinstance(result, dict) and result.get("validation_error"):
                logger.error(f"Erro de validação ao buscar dias: {result.get('detail')}")
                return self._gerar_dias_disponiveis_mock()
            
            # Garantir que retorna lista
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'dias' in result:
                return result['dias']
        
        # Fallback: gerar dias mock se API falhar
        return self._gerar_dias_disponiveis_mock()
    
    async def buscar_horarios_disponiveis(self, data: str) -> List[Dict]:
        """
        Busca horários disponíveis para uma data
        GET /api/agendamento/horarios-disponiveis/{token} (prod)
        GET /api/dev-agendamento/horarios-disponiveis/{token} (dev)
        """
        endpoint = f"/api/{self.env_prefix}agendamento/horarios-disponiveis/{self.token}"
        params = {"data": data}
        
        result = await self._request("GET", endpoint, params=params)
        
        if result:
            # Verificar se é erro de validação
            if isinstance(result, dict) and result.get("validation_error"):
                logger.error(f"Erro de validação ao buscar horários: {result.get('detail')}")
                return self._gerar_horarios_disponiveis_mock()
            
            # Garantir que retorna lista
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'horarios' in result:
                return result['horarios']
        
        # Fallback: gerar horários mock se API falhar
        return self._gerar_horarios_disponiveis_mock()
    
    async def retornar_agendamento(self, agendamento_id: str) -> Optional[Dict]:
        """
        Retorna dados de um agendamento
        GET /api/agendamento/retornar-agendamento/ (prod)
        GET /api/dev-agendamento/retornar-agendamento/ (dev)
        """
        endpoint = f"/api/{self.env_prefix}agendamento/retornar-agendamento/"
        params = {
            "token": self.token,
            "agendamento": agendamento_id
        }
        
        result = await self._request("GET", endpoint, params=params)
        
        # Verificar se é erro de validação
        if isinstance(result, dict) and result.get("validation_error"):
            logger.error(f"Erro de validação ao buscar agendamento: {result.get('detail')}")
            return None
        
        return result
    
    async def criar_agendamento(self, cpf: str, data_agendamento: str, 
                              data_fim_agendamento: str, 
                              primeiro_atendimento: bool = True) -> Optional[Dict]:
        """
        Cria novo agendamento
        POST /api/agendamento/agendar/ (prod)
        POST /api/dev-agendamento/agendar/ (dev)
        
        Formato esperado das datas: dd/mm/yyyy hh:mm:ss
        """
        # Limpar CPF (11 dígitos sem formatação)
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_limpo) != 11:
            logger.error(f"CPF inválido para agendamento: {cpf}")
            return None
        
        # Validar formato das datas (deve ser dd/mm/yyyy hh:mm:ss)
        if not self._validar_formato_data_api(data_agendamento):
            logger.error(f"Formato de data_agendamento inválido: {data_agendamento}")
            return None
            
        if not self._validar_formato_data_api(data_fim_agendamento):
            logger.error(f"Formato de data_fim_agendamento inválido: {data_fim_agendamento}")
            return None
        
        payload = {
            "data_agendamento": data_agendamento,
            "data_fim_agendamento": data_fim_agendamento,
            "cpf": cpf_limpo,
            "token": self.token,
            "primeiro_atendimento": primeiro_atendimento
        }
        
        logger.info(f"Criando agendamento: {payload}")
        
        endpoint = f"/api/{self.env_prefix}agendamento/agendar/"
        result = await self._request("POST", endpoint, json=payload)
        
        if result:
            # Verificar se é erro de validação
            if isinstance(result, dict) and result.get("validation_error"):
                logger.error(f"Erro de validação ao criar agendamento: {result.get('detail')}")
                return None
            
            logger.info("✅ Agendamento criado com sucesso")
            return result
        
        return None
    
    async def reagendar_agendamento(self, agendamento_id: str, 
                                  data_agendamento: str,
                                  data_fim_agendamento: str) -> Optional[Dict]:
        """
        Reagenda um agendamento existente
        PUT /api/agendamento/reagendar/ (prod)
        PUT /api/dev-agendamento/reagendar/ (dev)
        
        Formato esperado das datas: dd/mm/yyyy hh:mm:ss
        """
        # Validar formato das datas
        if not self._validar_formato_data_api(data_agendamento):
            logger.error(f"Formato de data_agendamento inválido: {data_agendamento}")
            return None
            
        if not self._validar_formato_data_api(data_fim_agendamento):
            logger.error(f"Formato de data_fim_agendamento inválido: {data_fim_agendamento}")
            return None
        
        payload = {
            "data_agendamento": data_agendamento,
            "data_fim_agendamento": data_fim_agendamento,
            "token": self.token,
            "agendamento": agendamento_id
        }
        
        logger.info(f"Reagendando: {payload}")
        
        endpoint = f"/api/{self.env_prefix}agendamento/reagendar/"
        result = await self._request("PUT", endpoint, json=payload)
        
        # Verificar se é erro de validação
        if isinstance(result, dict) and result.get("validation_error"):
            logger.error(f"Erro de validação ao reagendar: {result.get('detail')}")
            return None
        
        return result
    
    async def retornar_fuso_horario(self) -> Optional[Dict]:
        """
        Retorna o fuso horário da agenda
        GET /api/agendamento/retornar-fuso-horario/{token} (prod)
        GET /api/dev-agendamento/retornar-fuso-horario/{token} (dev)
        """
        endpoint = f"/api/{self.env_prefix}agendamento/retornar-fuso-horario/{self.token}"
        result = await self._request("GET", endpoint)
        
        # Verificar se é erro de validação
        if isinstance(result, dict) and result.get("validation_error"):
            logger.error(f"Erro de validação ao buscar fuso horário: {result.get('detail')}")
            return {"fuso_horario": "America/Sao_Paulo"}
        
        if not result:
            # Retornar fuso padrão
            return {"fuso_horario": "America/Sao_Paulo"}
        
        return result
    
    async def buscar_dados_agendamento(self) -> Optional[Dict]:
        """
        Busca dados do agendamento
        GET /api/dados-agendamento/{token}/ (prod)
        GET /api/dev-dados-agendamento/{token}/ (dev)
        """
        endpoint = f"/api/{self.env_prefix}dados-agendamento/{self.token}/"
        result = await self._request("GET", endpoint)
        
        # Verificar se é erro de validação
        if isinstance(result, dict) and result.get("validation_error"):
            logger.error(f"Erro de validação ao buscar dados: {result.get('detail')}")
            return None
        
        return result
    
    async def listar_agendamentos_periodo(self, data_inicial: str, 
                                        data_final: str) -> List[Dict]:
        """
        Lista agendamentos de um período
        GET /api/dados-agendamento/listagem/{token} (prod)
        GET /api/dev-dados-agendamento/listagem/{token} (dev)
        
        Parâmetros data_inicial e data_final obrigatórios
        """
        endpoint = f"/api/{self.env_prefix}dados-agendamento/listagem/{self.token}"
        params = {
            "data_inicial": data_inicial,
            "data_final": data_final
        }
        
        result = await self._request("GET", endpoint, params=params)
        
        if result:
            # Verificar se é erro de validação
            if isinstance(result, dict) and result.get("validation_error"):
                logger.error(f"Erro de validação ao listar agendamentos: {result.get('detail')}")
                return []
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'agendamentos' in result:
                return result['agendamentos']
        
        return []
    
    # Métodos auxiliares e de fallback
    
    def _validar_formato_data_api(self, data_str: str) -> bool:
        """
        Valida se a data está no formato esperado pela API: dd/mm/yyyy hh:mm:ss
        
        Exemplos válidos:
        - "05/08/2025 10:00:00"
        - "25/12/2024 14:30:00"
        """
        import re
        
        # Padrão: dd/mm/yyyy hh:mm:ss
        pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$'
        
        if not re.match(pattern, data_str):
            return False
        
        # Validação adicional das partes
        try:
            date_part, time_part = data_str.split(' ')
            day, month, year = date_part.split('/')
            hour, minute, second = time_part.split(':')
            
            # Validar ranges
            if not (1 <= int(day) <= 31):
                return False
            if not (1 <= int(month) <= 12):
                return False
            if not (2020 <= int(year) <= 2030):  # Range razoável
                return False
            if not (0 <= int(hour) <= 23):
                return False
            if not (0 <= int(minute) <= 59):
                return False
            if not (0 <= int(second) <= 59):
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def converter_datetime_para_api(dt: datetime) -> str:
        """
        Converte datetime Python para formato da API: dd/mm/yyyy hh:mm:ss
        
        Args:
            dt: datetime object
            
        Returns:
            String no formato dd/mm/yyyy hh:mm:ss
        """
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    
    @staticmethod
    def converter_api_para_datetime(data_str: str) -> Optional[datetime]:
        """
        Converte string da API (dd/mm/yyyy hh:mm:ss) para datetime Python
        
        Args:
            data_str: String no formato dd/mm/yyyy hh:mm:ss
            
        Returns:
            datetime object ou None se inválido
        """
        try:
            return datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            logger.error(f"Formato de data inválido: {data_str}")
            return None
    
    def _gerar_dias_disponiveis_mock(self) -> List[Dict]:
        """Gera dias disponíveis mock para fallback"""
        dias = []
        data_atual = datetime.now()
        
        for i in range(1, 8):
            data = data_atual + timedelta(days=i)
            # Pular fins de semana
            if data.weekday() < 5:  # 0-4 = Seg-Sex
                dias.append({
                    "data": data.strftime("%Y-%m-%d"),
                    "disponivel": True
                })
        
        return dias
    
    def _gerar_horarios_disponiveis_mock(self) -> List[Dict]:
        """Gera horários disponíveis mock para fallback"""
        horarios_base = [
            "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30"
        ]
        
        return [
            {"horario": h, "disponivel": True} 
            for h in horarios_base
        ]
    
    def limpar_cache(self):
        """Limpa todo o cache"""
        self._cache.clear()
        logger.info("Cache limpo")
    
    # Validações
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF"""
        try:
            # Remove caracteres não numéricos
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            if len(cpf_limpo) != 11:
                return False
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                return False
            
            # Cálculo do primeiro dígito verificador
            soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[9]) != digito1:
                return False
            
            # Cálculo do segundo dígito verificador
            soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[10]) != digito2:
                return False
            
            return True
        except:
            return False