"""Métricas para validar o modelo no conjunto de TESTE."""
from app.domain.pso.modelo import calcular_score_risco, classificar

CLASSES = ("normal", "atencao", "risco")


def avaliar(pesos: list[float], dataset: list[dict]) -> dict:
    if not dataset:
        raise ValueError("dataset vazio")
    erro_q = erro_abs = 0.0
    matriz = {real: {prev: 0 for prev in CLASSES} for real in CLASSES}
    acertos = 0
    for ex in dataset:
        score = calcular_score_risco(pesos, ex["features"])
        esperado = ex["risco_esperado"]
        erro_q += (score - esperado) ** 2
        erro_abs += abs(score - esperado)
        real, prev = classificar(esperado), classificar(score)
        matriz[real][prev] += 1
        acertos += real == prev
    n = len(dataset)
    return {
        "amostras": n,
        "mse": erro_q / n,
        "mae": erro_abs / n,
        "acuracia": acertos / n,
        "matriz_confusao": matriz,
    }
