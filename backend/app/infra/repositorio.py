from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.models import AlertaModel, DispositivoModel

# O repositório é o único lugar que sabe consultar o banco. A camada api/ pede
# "me dê os dispositivos" e não sabe se por trás há SQLite ou PostgreSQL.
# Ele devolve objetos do banco (DispositivoModel, AlertaModel): quem chama
# converte para os schemas Pydantic. A sessão é aberta e fechada por quem chama.

NIVEIS_VALIDOS = {"normal", "atencao", "risco"}


def listar_dispositivos(sessao: Session) -> list[DispositivoModel]:
    return list(sessao.scalars(select(DispositivoModel)).all())


def buscar_dispositivo(sessao: Session, device_id: str) -> DispositivoModel | None:
    return sessao.get(DispositivoModel, device_id)


def listar_alertas(sessao: Session) -> list[AlertaModel]:
    """Alertas ordenados do mais recente para o mais antigo, como pede o contrato."""
    consulta = select(AlertaModel).order_by(AlertaModel.timestamp.desc())
    return list(sessao.scalars(consulta).all())


def _validar_nivel(nivel_risco: str) -> None:
    if nivel_risco not in NIVEIS_VALIDOS:
        raise ValueError(f"nivel_risco inválido: {nivel_risco!r} (use {sorted(NIVEIS_VALIDOS)})")


def salvar_dispositivo(
    sessao: Session,
    *,
    device_id: str,
    nome: str,
    ip: str,
    ultima_atividade: datetime,
    nivel_risco: str,
    score_risco: float,
) -> DispositivoModel:
    """Cria o dispositivo ou atualiza o que já existe com o mesmo id."""
    _validar_nivel(nivel_risco)
    if not 0.0 <= score_risco <= 1.0:
        raise ValueError(f"score_risco fora da faixa 0.0-1.0: {score_risco}")

    dispositivo = sessao.merge(
        DispositivoModel(
            id=device_id,
            nome=nome,
            ip=ip,
            ultima_atividade=ultima_atividade,
            nivel_risco=nivel_risco,
            score_risco=score_risco,
        )
    )
    sessao.commit()
    return dispositivo


def registrar_alerta(
    sessao: Session,
    *,
    dispositivo_id: str,
    descricao: str,
    nivel_risco: str,
    timestamp: datetime | None = None,
    alerta_id: str | None = None,
) -> AlertaModel:
    """Grava um alerta de um dispositivo que já existe. Gera o id e o horário se não vierem."""
    _validar_nivel(nivel_risco)
    if buscar_dispositivo(sessao, dispositivo_id) is None:
        raise ValueError(f"Dispositivo não encontrado: {dispositivo_id}")

    alerta = AlertaModel(
        id=alerta_id or str(uuid4()),
        dispositivo_id=dispositivo_id,
        descricao=descricao,
        nivel_risco=nivel_risco,
        timestamp=timestamp or datetime.now(),
    )
    sessao.add(alerta)
    sessao.commit()
    return alerta
