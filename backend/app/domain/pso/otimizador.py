"""PSO (Particle Swarm Optimization) implementado do zero com NumPy.

Cada partícula é um vetor de 5 pesos em [0, 1]. A cada iteração:
    v = w*v + c1*r1*(pBest - x) + c2*r2*(gBest - x)
    x = x + v
O fitness é o erro quadrático médio entre o score previsto e o risco rotulado
(quanto MENOR, melhor).
"""
from dataclasses import dataclass, field

import numpy as np

from app.domain.pso.modelo import FEATURES


@dataclass
class ResultadoPSO:
    pesos: list[float]
    erro_treino: float
    historico: list[float] = field(default_factory=list)  # melhor erro por iteração
    iteracoes: int = 0
    particulas: int = 0
    semente: int | None = None


def _matrizes(dataset: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    x = np.array([[ex["features"][n] for n in FEATURES] for ex in dataset], dtype=float)
    y = np.array([ex["risco_esperado"] for ex in dataset], dtype=float)
    return x, y


def erro_quadratico_medio(pesos: np.ndarray, x: np.ndarray, y: np.ndarray) -> float:
    """Mesmo cálculo de calcular_score_risco, vetorizado para o dataset inteiro."""
    soma = float(np.sum(pesos))
    if soma <= 0:
        return float(np.mean(y ** 2))
    scores = np.clip(x @ pesos / soma, 0.0, 1.0)
    return float(np.mean((scores - y) ** 2))


def treinar_pesos(dataset: list[dict], n_particulas: int = 30, iteracoes: int = 100,
                  w: float = 0.9, c1: float = 0.5, c2: float = 0.3,
                  semente: int | None = 42) -> ResultadoPSO:
    """Roda o PSO e devolve os melhores pesos e a curva de convergência."""
    if not dataset:
        raise ValueError("dataset vazio")
    rng = np.random.default_rng(semente)
    x, y = _matrizes(dataset)
    dim = len(FEATURES)

    pos = rng.random((n_particulas, dim))
    vel = rng.uniform(-0.1, 0.1, (n_particulas, dim))
    pbest = pos.copy()
    pbest_erro = np.array([erro_quadratico_medio(p, x, y) for p in pos])
    i_melhor = int(np.argmin(pbest_erro))
    gbest = pbest[i_melhor].copy()
    gbest_erro = float(pbest_erro[i_melhor])
    historico = [gbest_erro]

    for _ in range(iteracoes):
        r1 = rng.random((n_particulas, dim))
        r2 = rng.random((n_particulas, dim))
        vel = w * vel + c1 * r1 * (pbest - pos) + c2 * r2 * (gbest - pos)
        pos = np.clip(pos + vel, 0.0, 1.0)  # mantém cada peso em [0, 1]

        erros = np.array([erro_quadratico_medio(p, x, y) for p in pos])
        melhorou = erros < pbest_erro
        pbest[melhorou] = pos[melhorou]
        pbest_erro[melhorou] = erros[melhorou]

        i_melhor = int(np.argmin(pbest_erro))
        if pbest_erro[i_melhor] < gbest_erro:
            gbest_erro = float(pbest_erro[i_melhor])
            gbest = pbest[i_melhor].copy()
        historico.append(gbest_erro)

    return ResultadoPSO(
        pesos=[round(float(p), 6) for p in gbest],
        erro_treino=gbest_erro,
        historico=historico,
        iteracoes=iteracoes,
        particulas=n_particulas,
        semente=semente,
    )
