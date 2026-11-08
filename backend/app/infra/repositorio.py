from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.models import AlertaModel, DispositivoModel

# O repositório é o único lugar que sabe consultar o banco. A camada api/ pede
# "me dê os dispositivos" e não sabe se por trás há SQLite ou PostgreSQL.
# Ele devolve objetos do banco (DispositivoModel, AlertaModel): quem chama
# converte para os schemas Pydantic. A sessão é aberta e fechada por quem chama.


def listar_dispositivos(sessao: Session) -> list[DispositivoModel]:
    return list(sessao.scalars(select(DispositivoModel)).all())


def buscar_dispositivo(sessao: Session, device_id: str) -> DispositivoModel | None:
    return sessao.get(DispositivoModel, device_id)


def listar_alertas(sessao: Session) -> list[AlertaModel]:
    """Alertas ordenados do mais recente para o mais antigo, como pede o contrato."""
    consulta = select(AlertaModel).order_by(AlertaModel.timestamp.desc())
    return list(sessao.scalars(consulta).all())
