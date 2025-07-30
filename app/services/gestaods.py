import httpx
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GestaoDS:
    def __init__(self):
        self.base_url = settings.gestaods_api_url
        self.token = settings.gestaods_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def buscar_paciente_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca paciente por CPF"""
        try:
            cpf_limpo = ''.join(filter(str.isdigit, cpf))

            async with httpx.AsyncClient() as client:
                # Usando a API correta da GestãoDS
                response = await client.get(
                    f"{self.base_url}/api/pacientes",
                    headers=self.headers,
                    params={"cpf": cpf_limpo},
                    timeout=30.0
                )

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

    async def listar_horarios_disponiveis(self,
                                        data_inicio: datetime,
                                        data_fim: datetime,
                                        tipo_consulta: str = "consulta") -> List[Dict]:
        """Lista horários disponíveis para agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                    "data_fim": data_fim.strftime("%Y-%m-%d"),
                    "tipo": tipo_consulta,
                    "disponivel": True
                }

                response = await client.get(
                    f"{self.base_url}/api/agenda/horarios/",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    horarios = response.json()
                    # Filtrar apenas horários disponíveis
                    horarios_disponiveis = [h for h in horarios if h.get('disponivel', False)]
                    return self._formatar_horarios(horarios_disponiveis)
                else:
                    logger.error(f"Erro ao buscar horários: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao listar horários: {str(e)}")
            return []

    async def criar_agendamento(self,
                              paciente_id: int,
                              data_hora: datetime,
                              tipo: str = "consulta",
                              observacoes: str = "") -> Optional[Dict]:
        """Cria novo agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "paciente_id": paciente_id,
                    "data_hora": data_hora.isoformat(),
                    "tipo": tipo,
                    "status": "agendado",
                    "observacoes": observacoes,
                    "origem": "whatsapp_bot"
                }

                response = await client.post(
                    f"{self.base_url}/api/agendamentos/",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Erro ao criar agendamento: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao agendar: {str(e)}")
            return None

    async def listar_agendamentos_paciente(self, paciente_id: int) -> List[Dict]:
        """Lista agendamentos do paciente"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/paciente/{paciente_id}/agendamentos/",
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return []

        except Exception as e:
            logger.error(f"Erro ao listar agendamentos: {str(e)}")
            return []

    async def cancelar_agendamento(self, agendamento_id: int, motivo: str = "") -> bool:
        """Cancela agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "status": "cancelado",
                    "motivo_cancelamento": motivo,
                    "cancelado_por": "paciente_whatsapp"
                }

                response = await client.patch(
                    f"{self.base_url}/api/agendamento/{agendamento_id}/",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Erro ao cancelar: {str(e)}")
            return False

    async def buscar_agendamentos_dia(self, data: datetime) -> List[Dict]:
        """Busca todos agendamentos de um dia específico"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "data": data.strftime("%Y-%m-%d"),
                    "status": "agendado"
                }

                response = await client.get(
                    f"{self.base_url}/api/agenda/dia/",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return []

        except Exception as e:
            logger.error(f"Erro ao buscar agenda do dia: {str(e)}")
            return []

    def _formatar_horarios(self, horarios: List[Dict]) -> List[Dict]:
        """Formata horários para exibição amigável"""
        horarios_formatados = []

        for horario in horarios:
            data_hora = datetime.fromisoformat(horario['data_hora'])
            horarios_formatados.append({
                'id': horario.get('id'),
                'data': data_hora.strftime("%d/%m/%Y"),
                'hora': data_hora.strftime("%H:%M"),
                'dia_semana': self._get_dia_semana(data_hora),
                'tipo': horario.get('tipo', 'consulta'),
                'profissional': horario.get('profissional', 'Dr(a). Gabriela Nassif')
            })

        return horarios_formatados

    def _get_dia_semana(self, data: datetime) -> str:
        """Retorna dia da semana em português"""
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return dias[data.weekday()] 