from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.schemas import Dispositivo


def _dispositivo(**extra):
    base = dict(id="AA:BB", nome="ESP32", ip="192.168.4.11",
                ultima_atividade=datetime(2026, 10, 18), nivel_risco="normal", score_risco=0.5)
    base.update(extra)
    return Dispositivo(**base)


@pytest.mark.parametrize("score", [0.0, 0.5, 1.0])
def test_score_valido(score):
    assert _dispositivo(score_risco=score).score_risco == score


@pytest.mark.parametrize("score", [-0.1, 1.01, 5.0])
def test_score_fora_do_intervalo(score):
    with pytest.raises(ValidationError):
        _dispositivo(score_risco=score)


def test_nivel_risco_invalido():
    with pytest.raises(ValidationError):
        _dispositivo(nivel_risco="perigo")
