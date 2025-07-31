import httpx
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from app.config import settings
import logging
import asyncio
import json
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class APIEndpoint(Enum):
    """Enumeração dos endpoints da API GestãoDS"""
    BUSCAR_PACIENTE = "/api/paciente/{token}/{cpf}/"
    DIAS_DISPONIVEIS = "/api/agendamento/dias-disponiveis/{token}"
    HORARIOS_DISPONIVEIS = "/api/agendamento/horarios-disponiveis/{token}"
    RETORNAR_AGENDAMENTO = "/api/agendamento/retornar-agendamento/"
    REALIZAR_AGENDAMENTO = "/api/agendamento/agendar/"
    REAGENDAR = "/api/agendamento/reagendar/"
    FUSO_HORARIO = "/api/agendamento/retornar-fuso-horario/{token}"
    DADOS_AGENDAMENTO = "/api/dados-agendamento/{token}/"
    RELATORIO_AGENDAMENTOS = "/api/dados-agendamento/listagem/{token}"

@dataclass
class APIResponse:
    """Classe para padronizar respostas da API"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: int = 0
    raw_response: Optional[str] = None

class GestaoDSValidator:
    """Classe para validações específicas da API GestãoDS"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF com algoritmo oficial"""
        try:
            # Remove caracteres não numéricos
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            if len(cpf_limpo) != 11:
                return False
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                return False
            
            # Validação do primeiro dígito verificador
            soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[9]) != digito1:
                return False
            
            # Validação do segundo dígito verificador
            soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[10]) != digito2:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erro na validação de CPF: {str(e)}")
            return False
    
    @staticmethod
    def validar_data(data: str) -> bool:
        """Valida formato de data (YYYY-MM-DD)"""
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_data_hora(data_hora: str) -> bool:
        """Valida formato de data/hora (YYYY-MM-DD HH:MM:SS)"""
        try:
            datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_token(token: str) -> bool:
        """Valida formato do token"""
        if not token or len(token) < 10:
            return False
        return True

class GestaoDSClient:
    """Cliente HTTP otimizado para a API GestãoDS"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def request(self, method: str, url: str, **kwargs) -> APIResponse:
        """Executa requisição HTTP com retry e tratamento de erros"""
        if not self.session:
            raise RuntimeError("Cliente não inicializado. Use 'async with'")
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries} - {method} {url}")
                
                response = await self.session.request(method, url, **kwargs)
                
                logger.info(f"Resposta: {response.status_code} - {response.text[:200]}...")
                
                # Sucesso
                if response.status_code in [200, 201]:
                    try:
                        data = response.json() if response.text else None
                        return APIResponse(
                            success=True,
                            data=data,
                            status_code=response.status_code,
                            raw_response=response.text
                        )
                    except json.JSONDecodeError:
                        return APIResponse(
                            success=True,
                            data={"raw_text": response.text},
                            status_code=response.status_code,
                            raw_response=response.text
                        )
                
                # Erro 404 - Recurso não encontrado
                elif response.status_code == 404:
                    return APIResponse(
                        success=False,
                        error="Recurso não encontrado",
                        status_code=404,
                        raw_response=response.text
                    )
                
                # Erro 400 - Bad Request
                elif response.status_code == 400:
                    return APIResponse(
                        success=False,
                        error=f"Requisição inválida: {response.text}",
                        status_code=400,
                        raw_response=response.text
                    )
                
                # Erro 401/403 - Não autorizado
                elif response.status_code in [401, 403]:
                    return APIResponse(
                        success=False,
                        error="Token inválido ou não autorizado",
                        status_code=response.status_code,
                        raw_response=response.text
                    )
                
                # Erro 500+ - Erro do servidor
                elif response.status_code >= 500:
                    if attempt < max_retries - 1:
                        logger.warning(f"Erro do servidor, tentando novamente em {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        return APIResponse(
                            success=False,
                            error=f"Erro do servidor: {response.status_code}",
                            status_code=response.status_code,
                            raw_response=response.text
                        )
                
                # Outros erros
                else:
                    return APIResponse(
                        success=False,
                        error=f"Erro HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        raw_response=response.text
                    )
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout, tentando novamente em {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return APIResponse(
                        success=False,
                        error="Timeout na requisição",
                        status_code=0
                    )
            
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Erro de conexão, tentando novamente em {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return APIResponse(
                        success=False,
                        error=f"Erro de conexão: {str(e)}",
                        status_code=0
                    )
            
            except Exception as e:
                return APIResponse(
                    success=False,
                    error=f"Erro inesperado: {str(e)}",
                    status_code=0
                )
        
        return APIResponse(
            success=False,
            error="Número máximo de tentativas excedido",
            status_code=0
        )

class GestaoDS:
    """Classe principal para integração com a API GestãoDS"""
    
    def __init__(self):
        self.base_url = settings.gestaods_api_url
        self.token = settings.gestaods_token
        self.validator = GestaoDSValidator()
        
        # Cache para otimização
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        
        logger.info(f"GestãoDS inicializado - URL: {self.base_url}")
    
    def _get_cache_key(self, method: str, params: Dict) -> str:
        """Gera chave única para cache"""
        return f"{method}:{hash(json.dumps(params, sort_keys=True))}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Obtém resposta do cache se ainda válida"""
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_ttl:
                logger.info(f"Resposta obtida do cache: {cache_key}")
                return cached_data
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cached_response(self, cache_key: str, data: Dict):
        """Armazena resposta no cache"""
        self._cache[cache_key] = (data, datetime.now().timestamp())
        logger.info(f"Resposta armazenada no cache: {cache_key}")
    
    def _limpar_cache(self):
        """Limpa cache expirado"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.info(f"Cache limpo: {len(expired_keys)} entradas expiradas")
    
    async def buscar_paciente_cpf(self, cpf: str) -> Optional[Dict]:
        """
        Busca paciente por CPF usando o endpoint correto da API
        Endpoint: /api/paciente/{token}/{cpf}/
        """
        try:
            # Validação do CPF
            if not self.validator.validar_cpf(cpf):
                logger.error(f"CPF inválido: {cpf}")
                return None
            
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            # Verificar cache
            cache_key = self._get_cache_key("buscar_paciente", {"cpf": cpf_limpo})
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando dados mock")
                mock_data = self._get_mock_paciente(cpf_limpo)
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/paciente/{self.token}/{cpf_limpo}/"
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url)
                
                if response.success:
                    if response.data and len(response.data) > 0:
                        paciente = response.data[0]  # Primeiro paciente encontrado
                        self._set_cached_response(cache_key, paciente)
                        logger.info(f"Paciente encontrado: {paciente.get('nome', 'N/A')}")
                        return paciente
                    else:
                        logger.info(f"Paciente não encontrado: {cpf}")
                        return None
                else:
                    logger.error(f"Erro ao buscar paciente: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro na busca de paciente: {str(e)}")
            return None
    
    async def buscar_dias_disponiveis(self, data: Optional[str] = None) -> List[Dict]:
        """
        Busca dias disponíveis para agendamento
        Endpoint: /api/agendamento/dias-disponiveis/{token}
        """
        try:
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return []
            
            # Validação da data (se fornecida)
            if data and not self.validator.validar_data(data):
                logger.error(f"Data inválida: {data}")
                return []
            
            # Verificar cache
            cache_key = self._get_cache_key("dias_disponiveis", {"data": data})
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando dias mock")
                mock_data = self._get_mock_dias_disponiveis()
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/dias-disponiveis/{self.token}"
            params = {}
            if data:
                params["data"] = data
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url, params=params)
                
                if response.success:
                    self._set_cached_response(cache_key, response.data)
                    logger.info(f"Dias disponíveis encontrados: {len(response.data)}")
                    return response.data
                else:
                    logger.error(f"Erro ao buscar dias disponíveis: {response.error}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar dias disponíveis: {str(e)}")
            return []
    
    async def buscar_horarios_disponiveis(self, data: Optional[str] = None) -> List[Dict]:
        """
        Busca horários disponíveis para agendamento
        Endpoint: /api/agendamento/horarios-disponiveis/{token}
        """
        try:
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return []
            
            # Validação da data (se fornecida)
            if data and not self.validator.validar_data(data):
                logger.error(f"Data inválida: {data}")
                return []
            
            # Verificar cache
            cache_key = self._get_cache_key("horarios_disponiveis", {"data": data})
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando horários mock")
                mock_data = self._get_mock_horarios_disponiveis()
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/horarios-disponiveis/{self.token}"
            params = {}
            if data:
                params["data"] = data
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url, params=params)
                
                if response.success:
                    self._set_cached_response(cache_key, response.data)
                    logger.info(f"Horários disponíveis encontrados: {len(response.data)}")
                    return response.data
                else:
                    logger.error(f"Erro ao buscar horários disponíveis: {response.error}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar horários disponíveis: {str(e)}")
            return []
    
    async def retornar_agendamento(self, agendamento_id: str) -> Optional[Dict]:
        """
        Retorna dados de um agendamento específico
        Endpoint: /api/agendamento/retornar-agendamento/
        """
        try:
            # Validação do ID do agendamento
            if not agendamento_id or not agendamento_id.strip():
                logger.error("ID do agendamento inválido")
                return None
            
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando agendamento mock")
                return self._get_mock_agendamento(agendamento_id)
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/retornar-agendamento/"
            params = {
                "token": self.token,
                "agendamento": agendamento_id
            }
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url, params=params)
                
                if response.success:
                    logger.info(f"Agendamento encontrado: {agendamento_id}")
                    return response.data
                else:
                    logger.error(f"Erro ao buscar agendamento: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar agendamento: {str(e)}")
            return None
    
    async def criar_agendamento(self, 
                              cpf: str,
                              data_agendamento: str,
                              data_fim_agendamento: str,
                              primeiro_atendimento: bool = True) -> Optional[Dict]:
        """
        Cria novo agendamento usando o endpoint correto
        Endpoint: /api/agendamento/agendar/
        """
        try:
            # Validações
            if not self.validator.validar_cpf(cpf):
                logger.error(f"CPF inválido: {cpf}")
                return None
            
            if not self.validator.validar_data_hora(data_agendamento):
                logger.error(f"Data de agendamento inválida: {data_agendamento}")
                return None
            
            if not self.validator.validar_data_hora(data_fim_agendamento):
                logger.error(f"Data de fim inválida: {data_fim_agendamento}")
                return None
            
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - criando agendamento mock")
                return self._get_mock_agendamento_criado()
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/agendar/"
            payload = {
                "cpf": cpf_limpo,
                "token": self.token,
                "data_agendamento": data_agendamento,
                "data_fim_agendamento": data_fim_agendamento,
                "primeiro_atendimento": primeiro_atendimento
            }
            
            logger.info(f"Criando agendamento: {payload}")
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("POST", url, json=payload)
                
                if response.success:
                    logger.info(f"Agendamento criado com sucesso")
                    return response.data
                else:
                    logger.error(f"Erro ao criar agendamento: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            return None
    
    async def reagendar_agendamento(self,
                                  agendamento_id: str,
                                  data_agendamento: str,
                                  data_fim_agendamento: str) -> Optional[Dict]:
        """
        Reagenda um agendamento existente
        Endpoint: /api/agendamento/reagendar/
        """
        try:
            # Validações
            if not agendamento_id or not agendamento_id.strip():
                logger.error("ID do agendamento inválido")
                return None
            
            if not self.validator.validar_data_hora(data_agendamento):
                logger.error(f"Data de agendamento inválida: {data_agendamento}")
                return None
            
            if not self.validator.validar_data_hora(data_fim_agendamento):
                logger.error(f"Data de fim inválida: {data_fim_agendamento}")
                return None
            
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - reagendando mock")
                return self._get_mock_agendamento_reagendado()
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/reagendar/"
            payload = {
                "token": self.token,
                "agendamento": agendamento_id,
                "data_agendamento": data_agendamento,
                "data_fim_agendamento": data_fim_agendamento
            }
            
            logger.info(f"Reagendando: {payload}")
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("PUT", url, json=payload)
                
                if response.success:
                    logger.info(f"Agendamento reagendado com sucesso")
                    return response.data
                else:
                    logger.error(f"Erro ao reagendar: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao reagendar: {str(e)}")
            return None
    
    async def retornar_fuso_horario(self) -> Optional[Dict]:
        """
        Retorna o fuso horário da agenda
        Endpoint: /api/agendamento/retornar-fuso-horario/{token}
        """
        try:
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            # Verificar cache
            cache_key = self._get_cache_key("fuso_horario", {})
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando fuso horário mock")
                mock_data = {"fuso_horario": "America/Sao_Paulo"}
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/agendamento/retornar-fuso-horario/{self.token}"
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url)
                
                if response.success:
                    self._set_cached_response(cache_key, response.data)
                    logger.info(f"Fuso horário obtido: {response.data}")
                    return response.data
                else:
                    logger.error(f"Erro ao buscar fuso horário: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar fuso horário: {str(e)}")
            return None
    
    async def buscar_dados_agendamento(self) -> Optional[Dict]:
        """
        Busca dados do agendamento
        Endpoint: /api/dados-agendamento/{token}/
        """
        try:
            # Validação do token
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return None
            
            # Verificar cache
            cache_key = self._get_cache_key("dados_agendamento", {})
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando dados de agendamento mock")
                mock_data = self._get_mock_dados_agendamento()
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/dados-agendamento/{self.token}/"
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url)
                
                if response.success:
                    self._set_cached_response(cache_key, response.data)
                    logger.info(f"Dados de agendamento obtidos")
                    return response.data
                else:
                    logger.error(f"Erro ao buscar dados do agendamento: {response.error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar dados do agendamento: {str(e)}")
            return None
    
    async def listar_agendamentos_periodo(self, data_inicial: str, data_final: str) -> List[Dict]:
        """
        Lista agendamentos de um período específico
        Endpoint: /api/dados-agendamento/listagem/{token}
        """
        try:
            # Validações
            if not self.validator.validar_data(data_inicial):
                logger.error(f"Data inicial inválida: {data_inicial}")
                return []
            
            if not self.validator.validar_data(data_final):
                logger.error(f"Data final inválida: {data_final}")
                return []
            
            if not self.validator.validar_token(self.token):
                logger.error("Token inválido")
                return []
            
            # Verificar cache
            cache_key = self._get_cache_key("listar_agendamentos", {
                "data_inicial": data_inicial,
                "data_final": data_final
            })
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                return cached_data
            
            # Modo de teste local
            if self._is_test_mode():
                logger.info("Modo de teste local - retornando agendamentos mock")
                mock_data = self._get_mock_agendamentos_periodo()
                self._set_cached_response(cache_key, mock_data)
                return mock_data
            
            # Chamada real da API
            url = f"{self.base_url}/api/dados-agendamento/listagem/{self.token}"
            params = {
                "data_inicial": data_inicial,
                "data_final": data_final
            }
            
            async with GestaoDSClient(self.base_url) as client:
                response = await client.request("GET", url, params=params)
                
                if response.success:
                    self._set_cached_response(cache_key, response.data)
                    logger.info(f"Agendamentos encontrados: {len(response.data)}")
                    return response.data
                else:
                    logger.error(f"Erro ao listar agendamentos: {response.error}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos: {str(e)}")
            return []
    
    # Métodos auxiliares
    def _is_test_mode(self) -> bool:
        """Verifica se está em modo de teste"""
        import os
        return (os.getenv('ENVIRONMENT', 'development') == 'development' or 
                not self.base_url or self.base_url == "" or
                os.getenv('GESTAODS_TEST_MODE', 'false').lower() == 'true')
    
    def _get_mock_paciente(self, cpf: str) -> Dict:
        """Retorna dados mock de paciente"""
        return {
            "id": "12345",
            "nome": "João Silva",
            "cpf": cpf,
            "telefone": "5531999999999",
            "email": "joao@email.com",
            "data_nascimento": "1985-03-15",
            "endereco": "Rua das Flores, 123"
        }
    
    def _get_mock_dias_disponiveis(self) -> List[Dict]:
        """Retorna dias disponíveis mock"""
        return [
            {"data": "2024-01-15", "disponivel": True},
            {"data": "2024-01-16", "disponivel": True},
            {"data": "2024-01-17", "disponivel": False},
            {"data": "2024-01-18", "disponivel": True}
        ]
    
    def _get_mock_horarios_disponiveis(self) -> List[Dict]:
        """Retorna horários disponíveis mock"""
        return [
            {"horario": "08:00", "disponivel": True},
            {"horario": "09:00", "disponivel": True},
            {"horario": "10:00", "disponivel": False},
            {"horario": "14:00", "disponivel": True},
            {"horario": "15:00", "disponivel": True}
        ]
    
    def _get_mock_agendamento(self, agendamento_id: str) -> Dict:
        """Retorna agendamento mock"""
        return {
            "id": agendamento_id,
            "data_hora": "2024-01-15T14:00:00",
            "tipo_consulta": "Consulta médica geral",
            "profissional": "Dr. Maria Santos",
            "status": "agendado",
            "paciente": {
                "nome": "João Silva",
                "cpf": "12345678901"
            }
        }
    
    def _get_mock_agendamento_criado(self) -> Dict:
        """Retorna agendamento criado mock"""
        return {
            "id": "99999",
            "status": "criado",
            "data_hora": "2024-01-15T14:00:00",
            "mensagem": "Agendamento criado com sucesso"
        }
    
    def _get_mock_agendamento_reagendado(self) -> Dict:
        """Retorna agendamento reagendado mock"""
        return {
            "id": "99999",
            "status": "reagendado",
            "data_hora": "2024-01-20T10:00:00",
            "mensagem": "Agendamento reagendado com sucesso"
        }
    
    def _get_mock_dados_agendamento(self) -> Dict:
        """Retorna dados de agendamento mock"""
        return {
            "profissionais": [
                {"id": "1", "nome": "Dr. Maria Santos"},
                {"id": "2", "nome": "Dr. Carlos Oliveira"}
            ],
            "tipos_consulta": [
                {"id": "1", "nome": "Consulta médica geral"},
                {"id": "2", "nome": "Exame de rotina"}
            ],
            "configuracoes": {
                "intervalo_consulta": 30,
                "horario_inicio": "08:00",
                "horario_fim": "18:00"
            }
        }
    
    def _get_mock_agendamentos_periodo(self) -> List[Dict]:
        """Retorna agendamentos do período mock"""
        return [
            {
                "id": "1",
                "data_hora": "2024-01-15T14:00:00",
                "tipo_consulta": "Consulta médica geral",
                "profissional": "Dr. Maria Santos",
                "status": "agendado"
            },
            {
                "id": "2", 
                "data_hora": "2024-01-20T10:30:00",
                "tipo_consulta": "Exame de rotina",
                "profissional": "Dr. Carlos Oliveira",
                "status": "agendado"
            }
        ]
    
    def formatar_data_hora(self, data_hora_str: str) -> str:
        """Formata data/hora para o formato esperado pela API (dd/mm/yyyy hh:mm:ss)"""
        try:
            # Converte de ISO para o formato esperado
            dt = datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except Exception as e:
            logger.error(f"Erro ao formatar data/hora: {str(e)}")
            return data_hora_str
    
    def formatar_data(self, data_str: str) -> str:
        """Formata data para o formato esperado pela API (dd/mm/yyyy)"""
        try:
            # Converte de YYYY-MM-DD para dd/mm/yyyy
            dt = datetime.strptime(data_str, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except Exception as e:
            logger.error(f"Erro ao formatar data: {str(e)}")
            return data_str
    
    def limpar_cache(self):
        """Limpa todo o cache"""
        self._cache.clear()
        logger.info("Cache limpo completamente")
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        self._limpar_cache()  # Remove entradas expiradas primeiro
        return {
            "total_entries": len(self._cache),
            "cache_ttl": self._cache_ttl
        } 