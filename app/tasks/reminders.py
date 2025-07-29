from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Appointment, WaitingList, SessionLocal
from app.services.whatsapp import WhatsAppService
from app.services.gestaods import GestaoDS
from app.utils.formatters import FormatterUtils
import logging

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.gestaods = GestaoDS()

    async def enviar_lembretes_diarios(self):
        """Envia lembretes para consultas do dia seguinte"""
        try:
            db = SessionLocal()

            # Buscar consultas de amanhã
            amanha = datetime.now() + timedelta(days=1)
            inicio_dia = amanha.replace(hour=0, minute=0, second=0)
            fim_dia = amanha.replace(hour=23, minute=59, second=59)

            consultas = db.query(Appointment).filter(
                Appointment.appointment_date >= inicio_dia,
                Appointment.appointment_date <= fim_dia,
                Appointment.status == "scheduled",
                Appointment.reminder_sent == False
            ).all()

            logger.info(f"Enviando {len(consultas)} lembretes")

            for consulta in consultas:
                await self._enviar_lembrete_individual(consulta, db)

            db.close()

        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {str(e)}")

    async def _enviar_lembrete_individual(self, consulta: Appointment, db: Session):
        """Envia lembrete individual"""
        try:
            data_hora = consulta.appointment_date

            mensagem = FormatterUtils.formatar_mensagem_lembrete(
                consulta.patient_name,
                data_hora,
                data_hora.strftime("%H:%M")
            )

            # Enviar lembrete
            await self.whatsapp.send_text(consulta.patient_phone, mensagem)

            # Marcar como enviado
            consulta.reminder_sent = True
            db.commit()

            logger.info(f"Lembrete enviado para {consulta.patient_name}")

        except Exception as e:
            logger.error(f"Erro ao enviar lembrete: {str(e)}")

    async def verificar_cancelamentos(self):
        """Verifica cancelamentos e notifica lista de espera"""
        try:
            db = SessionLocal()

            # Buscar consultas canceladas recentemente
            uma_hora_atras = datetime.now() - timedelta(hours=1)

            consultas_canceladas = db.query(Appointment).filter(
                Appointment.status == "cancelled",
                Appointment.updated_at >= uma_hora_atras
            ).all()

            for consulta in consultas_canceladas:
                await self._notificar_lista_espera(consulta, db)

            db.close()

        except Exception as e:
            logger.error(f"Erro ao verificar cancelamentos: {str(e)}")

    async def _notificar_lista_espera(self, consulta_cancelada: Appointment, db: Session):
        """Notifica pessoas na lista de espera sobre vaga disponível"""
        try:
            # Buscar pessoas na lista de espera
            lista_espera = db.query(WaitingList).filter(
                WaitingList.notified == False
            ).order_by(WaitingList.priority.desc(), WaitingList.created_at).limit(3).all()

            data_hora = consulta_cancelada.appointment_date

            for pessoa in lista_espera:
                mensagem = f"""
🎉 *Vaga Disponível!*

Olá, {pessoa.patient_name}!

Surgiu uma vaga para consulta:

📆 Data: {FormatterUtils.formatar_data_brasil(data_hora)}
⏰ Horário: {FormatterUtils.formatar_hora_brasil(data_hora)}

*Deseja agendar?*

*1* - ✅ Sim, quero a vaga!
*2* - ❌ Não posso neste horário

⚡ Responda rápido! Esta vaga pode ser preenchida por outra pessoa.
"""

                await self.whatsapp.send_text(pessoa.patient_phone, mensagem)

                # Marcar como notificado
                pessoa.notified = True
                db.commit()

                logger.info(f"Lista de espera notificada: {pessoa.patient_name}")

        except Exception as e:
            logger.error(f"Erro ao notificar lista de espera: {str(e)}") 