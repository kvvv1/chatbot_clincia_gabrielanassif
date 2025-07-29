from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ConversationSchema(BaseModel):
    id: str
    phone: str
    state: str
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentSchema(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    patient_phone: str
    appointment_date: datetime
    appointment_type: str
    status: str
    reminder_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WaitingListSchema(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    patient_phone: str
    preferred_dates: Optional[Dict[str, Any]] = None
    priority: int = 0
    created_at: datetime
    notified: bool = False

    class Config:
        from_attributes = True

class WebhookMessageSchema(BaseModel):
    type: str
    phone: str
    messageId: str
    text: Optional[Dict[str, str]] = None

class WebhookStatusSchema(BaseModel):
    type: str
    phone: str
    messageId: str
    status: str

class WebhookConnectedSchema(BaseModel):
    connected: bool
    instance: str 