import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GestaoDS:
    def __init__(self):
        self.base_url = settings.gestaods_api_url
        self.token = settings.gestaods_token
        # A API do GestãoDS não usa Bearer token, o token vai na URL
        self.headers = {
            "Content-Type": "application/json"
        }

    async def buscar_paciente_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca paciente por CPF usando o endpoint correto da API"""
        try:
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            if len(cpf_limpo) != 11:
                logger.error(f"CPF inválido: {cpf}")
                return None

            # Para testes locais, retornar dados mock
            import os
            if os.getenv('ENVIRONMENT', 'development') == 'development' or not self.base_url or self.base_url == "":
                logger.info("Modo de teste local - retornando dados mock")
                return {
                    "id": "12345",
                    "nome": "João Silva",
                    "cpf": cpf_limpo,
                    "telefone": "5531999999999",
                    "email": "joao@email.com"
                }

            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/paciente/{token}/{cpf}/
                url = f"{self.base_url}/api/paciente/{self.token}/{cpf_limpo}/"
                logger.info(f"Buscando paciente: {url}")
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                logger.info(f"Resposta da API: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return data[0]  # Retorna primeiro paciente encontrado
                    else:
                        logger.info(f"Paciente não encontrado: {cpf}")
                        return None
                elif response.status_code == 404:
                    logger.info(f"Paciente não encontrado: {cpf}")
                    return None
                else:
                    logger.error(f"Erro ao buscar paciente: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro na API GestãoDS: {str(e)}")
            return None

    async def buscar_dias_disponiveis(self, data: Optional[str] = None) -> List[Dict]:
        """Busca dias disponíveis para agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/dias-disponiveis/{token}
                url = f"{self.base_url}/api/agendamento/dias-disponiveis/{self.token}"
                params = {}
                
                if data:
                    params["data"] = data

                logger.info(f"Buscando dias disponíveis: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                logger.info(f"Resposta dias disponíveis: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar dias disponíveis: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao buscar dias disponíveis: {str(e)}")
            return []

    async def buscar_horarios_disponiveis(self, data: Optional[str] = None) -> List[Dict]:
        """Busca horários disponíveis para agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/horarios-disponiveis/{token}
                url = f"{self.base_url}/api/agendamento/horarios-disponiveis/{self.token}"
                params = {}
                
                if data:
                    params["data"] = data

                logger.info(f"Buscando horários disponíveis: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                logger.info(f"Resposta horários disponíveis: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar horários disponíveis: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao buscar horários disponíveis: {str(e)}")
            return []

    async def retornar_agendamento(self, agendamento_id: str) -> Optional[Dict]:
        """Retorna dados de um agendamento específico"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/retornar-agendamento/
                url = f"{self.base_url}/api/agendamento/retornar-agendamento/"
                params = {
                    "token": self.token,
                    "agendamento": agendamento_id
                }

                logger.info(f"Buscando agendamento: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                logger.info(f"Resposta agendamento: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar agendamento: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao buscar agendamento: {str(e)}")
            return None

    async def criar_agendamento(self, 
                              cpf: str,
                              data_agendamento: str,
                              data_fim_agendamento: str,
                              primeiro_atendimento: bool = True) -> Optional[Dict]:
        """Cria novo agendamento usando o endpoint correto"""
        try:
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            if len(cpf_limpo) != 11:
                logger.error(f"CPF inválido: {cpf}")
                return None

            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/agendar/
                url = f"{self.base_url}/api/agendamento/agendar/"
                
                payload = {
                    "cpf": cpf_limpo,
                    "token": self.token,
                    "data_agendamento": data_agendamento,
                    "data_fim_agendamento": data_fim_agendamento,
                    "primeiro_atendimento": primeiro_atendimento
                }

                logger.info(f"Criando agendamento: {url}")
                logger.info(f"Payload: {payload}")
                
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                logger.info(f"Resposta criar agendamento: {response.status_code} - {response.text}")

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Erro ao criar agendamento: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            return None

    async def reagendar_agendamento(self,
                                  agendamento_id: str,
                                  data_agendamento: str,
                                  data_fim_agendamento: str) -> Optional[Dict]:
        """Reagenda um agendamento existente"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/reagendar/
                url = f"{self.base_url}/api/agendamento/reagendar/"
                
                payload = {
                    "token": self.token,
                    "agendamento": agendamento_id,
                    "data_agendamento": data_agendamento,
                    "data_fim_agendamento": data_fim_agendamento
                }

                logger.info(f"Reagendando: {url}")
                logger.info(f"Payload: {payload}")
                
                response = await client.put(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                logger.info(f"Resposta reagendar: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao reagendar: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao reagendar: {str(e)}")
            return None

    async def retornar_fuso_horario(self) -> Optional[Dict]:
        """Retorna o fuso horário da agenda"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/agendamento/retornar-fuso-horario/{token}
                url = f"{self.base_url}/api/agendamento/retornar-fuso-horario/{self.token}"

                logger.info(f"Buscando fuso horário: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                logger.info(f"Resposta fuso horário: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar fuso horário: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao buscar fuso horário: {str(e)}")
            return None

    async def buscar_dados_agendamento(self) -> Optional[Dict]:
        """Busca dados do agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/dados-agendamento/{token}/
                url = f"{self.base_url}/api/dados-agendamento/{self.token}/"

                logger.info(f"Buscando dados do agendamento: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                logger.info(f"Resposta dados agendamento: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao buscar dados do agendamento: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao buscar dados do agendamento: {str(e)}")
            return None

    async def listar_agendamentos_periodo(self, data_inicial: str, data_final: str) -> List[Dict]:
        """Lista agendamentos de um período específico"""
        try:
            # Para testes locais, retornar dados mock
            import os
            if os.getenv('ENVIRONMENT', 'development') == 'development' or not self.base_url or self.base_url == "":
                logger.info("Modo de teste local - retornando agendamentos mock")
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

            async with httpx.AsyncClient() as client:
                # Endpoint correto: /api/dados-agendamento/listagem/{token}
                url = f"{self.base_url}/api/dados-agendamento/listagem/{self.token}"
                params = {
                    "data_inicial": data_inicial,
                    "data_final": data_final
                }

                logger.info(f"Listando agendamentos: {url}")
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                logger.info(f"Resposta listar agendamentos: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao listar agendamentos: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao listar agendamentos: {str(e)}")
            return []

    # Métodos de desenvolvimento (dev) - para testes
    async def dev_buscar_paciente_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca paciente por CPF usando endpoint de desenvolvimento"""
        try:
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            if len(cpf_limpo) != 11:
                logger.error(f"CPF inválido: {cpf}")
                return None

            async with httpx.AsyncClient() as client:
                # Endpoint dev: /api/dev-paciente/{token}/{cpf}/
                url = f"{self.base_url}/api/dev-paciente/{self.token}/{cpf_limpo}/"
                logger.info(f"Buscando paciente (dev): {url}")
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                logger.info(f"Resposta da API (dev): {response.status_code} - {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return data[0]
                    else:
                        logger.info(f"Paciente não encontrado (dev): {cpf}")
                        return None
                elif response.status_code == 404:
                    logger.info(f"Paciente não encontrado (dev): {cpf}")
                    return None
                else:
                    logger.error(f"Erro ao buscar paciente (dev): {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro na API GestãoDS (dev): {str(e)}")
            return None

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