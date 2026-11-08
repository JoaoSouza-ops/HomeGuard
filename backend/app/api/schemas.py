from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NivelRisco(str, Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    RISCO = "risco"


class Dispositivo(BaseModel):
    # from_attributes permite criar o schema a partir de um objeto do banco
    # (DispositivoModel), lendo os atributos em vez de exigir um dicionário
    model_config = ConfigDict(from_attributes=True)

    id: str                  # MAC address ou identificador único
    nome: str                # ex: "ESP32 - Sensor Temperatura"
    ip: str
    ultima_atividade: datetime
    nivel_risco: NivelRisco
    score_risco: float = Field(ge=0.0, le=1.0)   # 0.0 a 1.0, calculado pelo PSO


class Alerta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dispositivo_id: str
    descricao: str           # ex: "Porta Telnet (23) aberta detectada"
    nivel_risco: NivelRisco
    timestamp: datetime


class MitigacaoRequest(BaseModel):
    acao: str                # ex: "bloquear_porta", "bloquear_ip"
    justificativa: str | None = None


# ---- PSO -------------------------------------------------------------------

class FeaturesJanela(BaseModel):
    """As 5 features de um dispositivo numa janela de tempo (docs/04, seção 2)."""
    taxa_pacotes_suspeitos: float = Field(ge=0.0, le=1.0)
    uso_porta_insegura: float = Field(ge=0.0, le=1.0)
    volume_anomalo: float = Field(ge=0.0, le=1.0)
    dispositivo_desconhecido: float = Field(ge=0.0, le=1.0)
    frequencia_conexoes: float = Field(ge=0.0, le=1.0)


class SimulacaoResultado(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    nivel_risco: NivelRisco
    contribuicoes: dict[str, float]


class MetricasPSO(BaseModel):
    amostras: int
    mse: float
    mae: float
    acuracia: float
    matriz_confusao: dict[str, dict[str, int]]


class RelatorioPSO(BaseModel):
    treinado_em: str | None = None
    features: list[str]
    pesos: list[float]
    particulas: int | None = None
    iteracoes: int | None = None
    semente: int | None = None
    historico_erro: list[float] = []
    metricas_treino: MetricasPSO | None = None
    metricas_teste: MetricasPSO | None = None
    fonte_dados: str = "sintetico"


class TreinoRequest(BaseModel):
    particulas: int = Field(default=30, ge=5, le=200)
    iteracoes: int = Field(default=100, ge=10, le=500)
    semente: int = 42
