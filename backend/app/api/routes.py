from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencias import get_sessao
from app.api.schemas import Alerta, Dispositivo, MitigacaoRequest
from app.infra import repositorio

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/devices", response_model=list[Dispositivo])
def listar_dispositivos(sessao: Session = Depends(get_sessao)):
    return repositorio.listar_dispositivos(sessao)


@router.get("/devices/{device_id}", response_model=Dispositivo)
def detalhe_dispositivo(device_id: str, sessao: Session = Depends(get_sessao)):
    dispositivo = repositorio.buscar_dispositivo(sessao, device_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    return dispositivo


@router.get("/alerts", response_model=list[Alerta])
def listar_alertas(sessao: Session = Depends(get_sessao)):
    # o repositório já devolve do mais recente para o mais antigo, como pede o contrato
    return repositorio.listar_alertas(sessao)


@router.post("/devices/{device_id}/mitigate")
def mitigar(device_id: str, request: MitigacaoRequest, sessao: Session = Depends(get_sessao)):
    if repositorio.buscar_dispositivo(sessao, device_id) is None:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    # Mock: não executa nenhuma ação real. A mitigação de verdade é o Passo 6.
    return {"status": "mitigado"}
