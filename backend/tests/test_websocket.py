import json
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.ws_manager import ConnectionManager, manager, publicar_alerta, publicar_dispositivo
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def limpar_manager():
    manager.active_connections.clear()
    yield
    manager.active_connections.clear()


class FalsaConexao:
    """Imita um WebSocket: guarda o que recebe, e pode simular um cliente que caiu."""

    def __init__(self, falha: bool = False):
        self.aceita = False
        self.recebidas = []
        self.falha = falha

    async def accept(self):
        self.aceita = True

    async def send_json(self, mensagem):
        if self.falha:
            raise RuntimeError("cliente desconectado")
        self.recebidas.append(mensagem)


@pytest.mark.anyio
async def test_connect_aceita_e_registra_o_cliente():
    gerenciador = ConnectionManager()
    conexao = FalsaConexao()

    await gerenciador.connect(conexao)

    assert conexao.aceita is True
    assert gerenciador.active_connections == [conexao]


def test_disconnect_remove_e_nao_quebra_se_repetido():
    gerenciador = ConnectionManager()
    conexao = FalsaConexao()
    gerenciador.active_connections.append(conexao)

    gerenciador.disconnect(conexao)
    gerenciador.disconnect(conexao)

    assert gerenciador.active_connections == []


@pytest.mark.anyio
async def test_broadcast_envia_a_todos_os_clientes():
    gerenciador = ConnectionManager()
    a, b = FalsaConexao(), FalsaConexao()
    gerenciador.active_connections.extend([a, b])

    await gerenciador.broadcast({"id": "x"})

    assert a.recebidas == [{"id": "x"}]
    assert b.recebidas == [{"id": "x"}]


@pytest.mark.anyio
async def test_broadcast_remove_quem_falhou_e_entrega_aos_demais():
    gerenciador = ConnectionManager()
    caida, viva = FalsaConexao(falha=True), FalsaConexao()
    gerenciador.active_connections.extend([caida, viva])

    await gerenciador.broadcast({"id": "x"})

    assert viva.recebidas == [{"id": "x"}]
    assert gerenciador.active_connections == [viva]


@pytest.mark.anyio
async def test_publicar_dispositivo_envia_json_no_formato_do_contrato():
    conexao = FalsaConexao()
    manager.active_connections.append(conexao)
    dispositivo = SimpleNamespace(
        id="AA:BB:CC:DD:EE:02",
        nome="ESP32 - Dispositivo Vulneravel",
        ip="192.168.4.12",
        ultima_atividade=datetime(2026, 11, 8, 10, 0, 0),
        nivel_risco="risco",
        score_risco=0.87,
    )

    await publicar_dispositivo(dispositivo)

    mensagem = conexao.recebidas[0]
    json.dumps(mensagem)  # não pode levantar: datas já viraram texto
    assert mensagem["id"] == "AA:BB:CC:DD:EE:02"
    assert mensagem["nivel_risco"] == "risco"
    assert mensagem["ultima_atividade"] == "2026-11-08T10:00:00"


@pytest.mark.anyio
async def test_publicar_alerta_envia_json_no_formato_do_contrato():
    conexao = FalsaConexao()
    manager.active_connections.append(conexao)
    alerta = SimpleNamespace(
        id="alerta-9",
        dispositivo_id="AA:BB:CC:DD:EE:02",
        descricao="Porta Telnet (23) aberta detectada",
        nivel_risco="risco",
        timestamp=datetime(2026, 11, 8, 10, 1, 0),
    )

    await publicar_alerta(alerta)

    mensagem = conexao.recebidas[0]
    json.dumps(mensagem)
    assert mensagem["dispositivo_id"] == "AA:BB:CC:DD:EE:02"
    assert mensagem["timestamp"] == "2026-11-08T10:01:00"


def test_rota_websocket_aceita_conexao():
    client = TestClient(app)

    with client.websocket_connect("/ws/alerts") as websocket:
        websocket.send_text("ping")
