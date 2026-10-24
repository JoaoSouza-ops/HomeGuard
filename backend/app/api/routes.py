from fastapi import APIRouter, HTTPException

from app.api.mock_data import ALERTAS_MOCK, DISPOSITIVOS_MOCK
from app.api.schemas import Alerta, Dispositivo, MitigacaoRequest

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/devices", response_model=list[Dispositivo])
def listar_dispositivos():
    return DISPOSITIVOS_MOCK


@router.get("/devices/{device_id}", response_model=Dispositivo)
def detalhe_dispositivo(device_id: str):
    for dispositivo in DISPOSITIVOS_MOCK:
        if dispositivo.id == device_id:
            return dispositivo
    raise HTTPException(status_code=404, detail="Dispositivo não encontrado")


@router.get("/alerts", response_model=list[Alerta])
def listar_alertas():
    # mais recentes primeiro, como pede o contrato
    return sorted(ALERTAS_MOCK, key=lambda a: a.timestamp, reverse=True)


@router.post("/devices/{device_id}/mitigate")
def mitigar(device_id: str, request: MitigacaoRequest):
    if not any(d.id == device_id for d in DISPOSITIVOS_MOCK):
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    # Mock: não executa nenhuma ação real. A mitigação de verdade é o Passo 6.
    return {"status": "mitigado"}