"""Treina, salva e carrega os pesos. O backend usa os pesos já treinados:
NUNCA re-treina a cada request (docs/04, seção 5)."""
import json
from datetime import datetime, timezone
from pathlib import Path

from app.domain.pso.dataset import dividir_treino_teste, gerar_dataset
from app.domain.pso.metricas import avaliar
from app.domain.pso.modelo import FEATURES, calcular_score_risco, classificar
from app.domain.pso.otimizador import treinar_pesos

ARQUIVO_PESOS = Path(__file__).resolve().parent / "pesos_treinados.json"
# Ponto de partida quando ainda não há treino salvo: pesos iguais.
PESOS_PADRAO = [0.2] * len(FEATURES)


def treinar_e_salvar(caminho: Path = ARQUIVO_PESOS, semente: int = 42, **kwargs) -> dict:
    dados = gerar_dataset(semente=semente)
    treino, teste = dividir_treino_teste(dados)
    resultado = treinar_pesos(treino, semente=semente, **kwargs)
    relatorio = {
        "treinado_em": datetime.now(timezone.utc).isoformat(),
        "features": list(FEATURES),
        "pesos": resultado.pesos,
        "particulas": resultado.particulas,
        "iteracoes": resultado.iteracoes,
        "semente": semente,
        "historico_erro": resultado.historico,
        "metricas_treino": avaliar(resultado.pesos, treino),
        "metricas_teste": avaliar(resultado.pesos, teste),
        "fonte_dados": "sintetico",
    }
    caminho.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return relatorio


def carregar_relatorio(caminho: Path = ARQUIVO_PESOS) -> dict | None:
    if not caminho.is_file():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_pesos(caminho: Path = ARQUIVO_PESOS) -> list[float]:
    relatorio = carregar_relatorio(caminho)
    return relatorio["pesos"] if relatorio else list(PESOS_PADRAO)


def pontuar(features: dict, caminho: Path = ARQUIVO_PESOS) -> dict:
    """Score + classificação + contribuição de cada feature para o score."""
    pesos = carregar_pesos(caminho)
    soma = sum(pesos) or 1.0
    score = calcular_score_risco(pesos, features)
    contribuicoes = {n: round(p * float(features[n]) / soma, 4) for p, n in zip(pesos, FEATURES)}
    return {"score": score, "nivel_risco": classificar(score), "contribuicoes": contribuicoes}
