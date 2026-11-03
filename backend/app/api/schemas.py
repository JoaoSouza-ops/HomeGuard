from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NivelRisco(str, Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    RISCO = "risco"


class Dispositivo(BaseModel):
    id: str                  # MAC address ou identificador único
    nome: str                # ex: "ESP32 - Sensor Temperatura"
    ip: str
    ultima_atividade: datetime
    nivel_risco: NivelRisco
    score_risco: float = Field(ge=0.0, le=1.0)   # 0.0 a 1.0, calculado pelo PSO


class Alerta(BaseModel):
    id: str
    dispositivo_id: str
    descricao: str           # ex: "Porta Telnet (23) aberta detectada"
    nivel_risco: NivelRisco
    timestamp: datetime


class MitigacaoRequest(BaseModel):
    acao: str                # ex: "bloquear_porta", "bloquear_ip"
    justificativa: str | None = None