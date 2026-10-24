from datetime import datetime

from app.api.schemas import Alerta, Dispositivo, NivelRisco

DISPOSITIVOS_MOCK = [
    Dispositivo(
        id="AA:BB:CC:DD:EE:01",
        nome="ESP32 - Sensor Temperatura",
        ip="192.168.4.11",
        ultima_atividade=datetime(2026, 10, 18, 14, 0, 0),
        nivel_risco=NivelRisco.NORMAL,
        score_risco=0.12,
    ),
    Dispositivo(
        id="AA:BB:CC:DD:EE:02",
        nome="ESP32 - Dispositivo Vulneravel",
        ip="192.168.4.12",
        ultima_atividade=datetime(2026, 10, 18, 14, 1, 0),
        nivel_risco=NivelRisco.RISCO,
        score_risco=0.87,
    ),
]

ALERTAS_MOCK = [
    Alerta(
        id="alerta-1",
        dispositivo_id="AA:BB:CC:DD:EE:02",
        descricao="Porta Telnet (23) aberta detectada",
        nivel_risco=NivelRisco.RISCO,
        timestamp=datetime(2026, 10, 18, 14, 1, 30),
    ),
]