from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.dependencias import get_sessao
from app.api.schemas import Alerta, Dispositivo, MitigacaoRequest
from app.api.ws_manager import manager
from app.domain import mitigacao
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
    dispositivo = repositorio.buscar_dispositivo(sessao, device_id)
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")

    try:
        mitigacao.executar_mitigacao(request.acao, dispositivo.ip)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": "mitigado"}


@router.websocket("/ws/alerts")
async def websocket_alertas(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantém a conexão viva
    except WebSocketDisconnect:
        manager.disconnect(websocket)
