from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database import Base

# Estes modelos descrevem as TABELAS. Os schemas Pydantic de app/api/schemas.py
# descrevem o CONTRATO da API. São coisas separadas de propósito.
# nivel_risco é guardado como texto ("normal", "atencao", "risco") em vez de
# um tipo enum do banco, que se comporta diferente entre SQLite e PostgreSQL.


class DispositivoModel(Base):
    __tablename__ = "dispositivos"

    id: Mapped[str] = mapped_column(primary_key=True)  # MAC address ou identificador único
    nome: Mapped[str]
    ip: Mapped[str]
    ultima_atividade: Mapped[datetime]
    nivel_risco: Mapped[str]
    score_risco: Mapped[float]


class AlertaModel(Base):
    __tablename__ = "alertas"

    id: Mapped[str] = mapped_column(primary_key=True)
    dispositivo_id: Mapped[str] = mapped_column(ForeignKey("dispositivos.id"))
    descricao: Mapped[str]
    nivel_risco: Mapped[str]
    timestamp: Mapped[datetime]

    dispositivo: Mapped["DispositivoModel"] = relationship()
