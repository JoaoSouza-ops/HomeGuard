import pytest

from app.infra.config import dados_iniciais_ligados, obter_tshark_path


def test_devolve_caminho_quando_variavel_definida(monkeypatch):
    monkeypatch.setenv("TSHARK_PATH", r"C:\falso\tshark.exe")
    assert obter_tshark_path() == r"C:\falso\tshark.exe"


def test_devolve_none_quando_variavel_ausente(monkeypatch):
    monkeypatch.delenv("TSHARK_PATH", raising=False)
    assert obter_tshark_path() is None


def test_devolve_none_quando_variavel_vazia(monkeypatch):
    monkeypatch.setenv("TSHARK_PATH", "")
    assert obter_tshark_path() is None


@pytest.mark.parametrize("valor", ["true", "TRUE", "1", "yes", " true "])
def test_dados_iniciais_ligados_com_valores_verdadeiros(monkeypatch, valor):
    monkeypatch.setenv("CARREGAR_DADOS_INICIAIS", valor)
    assert dados_iniciais_ligados() is True


@pytest.mark.parametrize("valor", ["false", "0", "", "talvez"])
def test_dados_iniciais_desligados_com_outros_valores(monkeypatch, valor):
    monkeypatch.setenv("CARREGAR_DADOS_INICIAIS", valor)
    assert dados_iniciais_ligados() is False


def test_dados_iniciais_desligados_por_padrao(monkeypatch):
    monkeypatch.delenv("CARREGAR_DADOS_INICIAIS", raising=False)
    assert dados_iniciais_ligados() is False
