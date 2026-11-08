import pytest
from fastapi.testclient import TestClient

from app.api.routes_pso import get_caminho_pesos
from app.domain.pso.dataset import dividir_treino_teste, gerar_dataset
from app.domain.pso.metricas import avaliar
from app.domain.pso.modelo import FEATURES, calcular_score_risco, classificar
from app.domain.pso.otimizador import treinar_pesos
from app.main import app


def test_score_com_pesos_zero_nao_divide_por_zero():
    assert calcular_score_risco([0] * 5, {n: 1.0 for n in FEATURES}) == 0.0


def test_score_fica_entre_0_e_1():
    assert calcular_score_risco([1] * 5, {n: 1.0 for n in FEATURES}) == pytest.approx(1.0)
    assert calcular_score_risco([1] * 5, {n: 0.0 for n in FEATURES}) == 0.0


@pytest.mark.parametrize("score,nivel", [(0.0, "normal"), (0.29, "normal"), (0.3, "atencao"),
                                         (0.69, "atencao"), (0.7, "risco"), (1.0, "risco")])
def test_classificar_limiares(score, nivel):
    assert classificar(score) == nivel


def test_dataset_e_reprodutivel_e_balanceado():
    a, b = gerar_dataset(10, semente=1), gerar_dataset(10, semente=1)
    assert a == b
    assert len(a) == 30
    assert all(0 <= v <= 1 for ex in a for v in ex["features"].values())


def test_divisao_treino_teste_nao_mistura():
    treino, teste = dividir_treino_teste(gerar_dataset(20), 0.3)
    assert len(treino) + len(teste) == 60 and len(teste) == 18


def test_pso_reduz_erro_e_respeita_limites():
    treino, teste = dividir_treino_teste(gerar_dataset(40))
    r = treinar_pesos(treino, iteracoes=60, semente=3)
    assert len(r.pesos) == 5 and all(0.0 <= p <= 1.0 for p in r.pesos)
    assert r.historico[-1] < r.historico[0]
    assert all(b <= a for a, b in zip(r.historico, r.historico[1:]))  # nunca piora
    m = avaliar(r.pesos, teste)
    assert m["acuracia"] > 0.8


def test_pso_com_mesma_semente_da_mesmo_resultado():
    dados = gerar_dataset(20)
    assert treinar_pesos(dados, iteracoes=20, semente=5).pesos == \
        treinar_pesos(dados, iteracoes=20, semente=5).pesos


def test_pso_dataset_vazio():
    with pytest.raises(ValueError):
        treinar_pesos([])


@pytest.fixture
def client(tmp_path):
    app.dependency_overrides[get_caminho_pesos] = lambda: tmp_path / "pesos.json"
    yield TestClient(app)
    app.dependency_overrides.pop(get_caminho_pesos, None)


def test_pesos_sem_treino_devolve_padrao(client):
    r = client.get("/pso/pesos")
    assert r.status_code == 200
    assert r.json()["pesos"] == [0.2] * 5 and r.json()["metricas_teste"] is None


def test_treinar_e_depois_obter(client):
    r = client.post("/pso/treinar", json={"particulas": 10, "iteracoes": 20})
    assert r.status_code == 200
    corpo = client.get("/pso/pesos").json()
    assert corpo["pesos"] == r.json()["pesos"]
    assert len(corpo["historico_erro"]) == 21
    assert corpo["metricas_teste"]["amostras"] > 0


def test_treinar_valida_parametros(client):
    assert client.post("/pso/treinar", json={"particulas": 1}).status_code == 422


def test_simular_telnet_da_risco_alto(client):
    client.post("/pso/treinar", json={})
    r = client.post("/pso/simular", json={
        "taxa_pacotes_suspeitos": 0.9, "uso_porta_insegura": 1, "volume_anomalo": 0.8,
        "dispositivo_desconhecido": 0, "frequencia_conexoes": 0.8})
    assert r.status_code == 200
    assert r.json()["nivel_risco"] == "risco"


def test_simular_rejeita_feature_fora_da_faixa(client):
    r = client.post("/pso/simular", json={
        "taxa_pacotes_suspeitos": 2, "uso_porta_insegura": 1, "volume_anomalo": 0,
        "dispositivo_desconhecido": 0, "frequencia_conexoes": 0})
    assert r.status_code == 422
