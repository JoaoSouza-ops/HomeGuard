"""Score de risco e classificação. Regras de negócio, não fazem parte do PSO."""
from collections.abc import Sequence

FEATURES = (
    "taxa_pacotes_suspeitos",
    "uso_porta_insegura",
    "volume_anomalo",
    "dispositivo_desconhecido",
    "frequencia_conexoes",
)

LIMIAR_ATENCAO = 0.3
LIMIAR_RISCO = 0.7


def calcular_score_risco(pesos: Sequence[float], features: dict) -> float:
    """Média ponderada das 5 features, de 0.0 (sem risco) a 1.0 (risco máximo).

    Dividir pela soma dos pesos faz o score depender só da PROPORÇÃO entre eles.
    Se todos os pesos forem zero, devolve 0.0 em vez de dividir por zero.
    """
    soma = float(sum(pesos))
    if soma <= 0:
        return 0.0
    bruto = sum(p * float(features[nome]) for p, nome in zip(pesos, FEATURES))
    return min(max(bruto / soma, 0.0), 1.0)


def classificar(score: float) -> str:
    if score < LIMIAR_ATENCAO:
        return "normal"
    if score < LIMIAR_RISCO:
        return "atencao"
    return "risco"
