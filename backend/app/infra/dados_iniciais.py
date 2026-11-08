from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.models import AlertaModel, DispositivoModel

# Estes são os dados que antes viviam em app/api/mock_data.py. Ficam em infra/
# porque são gravados no banco, e a infra não deve importar a camada api/.


def _dispositivos_exemplo() -> list[DispositivoModel]:
    return [
        DispositivoModel(
            id="AA:BB:CC:DD:EE:01",
            nome="ESP32 - Sensor Temperatura",
            ip="192.168.4.11",
            ultima_atividade=datetime(2026, 10, 18, 14, 0, 0),
            nivel_risco="normal",
            score_risco=0.12,
        ),
        DispositivoModel(
            id="AA:BB:CC:DD:EE:02",
            nome="ESP32 - Dispositivo Vulneravel",
            ip="192.168.4.12",
            ultima_atividade=datetime(2026, 10, 18, 14, 1, 0),
            nivel_risco="risco",
            score_risco=0.87,
        ),
    ]


def _alertas_exemplo() -> list[AlertaModel]:
    return [
        AlertaModel(
            id="alerta-1",
            dispositivo_id="AA:BB:CC:DD:EE:02",
            descricao="Porta Telnet (23) aberta detectada",
            nivel_risco="risco",
            timestamp=datetime(2026, 10, 18, 14, 1, 30),
        ),
    ]


def carregar_dados_iniciais(sessao: Session) -> bool:
    """Grava os dados de exemplo se a tabela de dispositivos estiver vazia.

    Devolve True se gravou e False se não fez nada (o banco já tinha dados).
    """
    total = sessao.scalar(select(func.count()).select_from(DispositivoModel))
    if total:
        return False

    sessao.add_all(_dispositivos_exemplo())
    sessao.add_all(_alertas_exemplo())
    sessao.commit()
    return True
