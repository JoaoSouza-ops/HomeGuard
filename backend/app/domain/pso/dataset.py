"""Dataset rotulado SINTÉTICO para treinar/validar o PSO.

Enquanto a equipe não tem capturas reais rotuladas dos ESPs, geramos janelas de
tráfego plausíveis para três cenários. Quando houver dados reais, basta salvar
um JSON no mesmo formato ({"features": {...}, "risco_esperado": 0..1}) e
passá-lo para o treino no lugar deste gerador.
"""
import random

from app.domain.pso.modelo import FEATURES

# (média, desvio) de cada feature por cenário + risco esperado do cenário.
CENARIOS = {
    "normal": {
        "risco": 0.10,
        "perfil": {
            "taxa_pacotes_suspeitos": (0.03, 0.03),
            "uso_porta_insegura": (0.0, 0.0),
            "volume_anomalo": (0.12, 0.08),
            "dispositivo_desconhecido": (0.0, 0.0),
            "frequencia_conexoes": (0.15, 0.08),
        },
    },
    "atencao": {
        "risco": 0.50,
        "perfil": {
            "taxa_pacotes_suspeitos": (0.30, 0.12),
            "uso_porta_insegura": (0.5, 0.5),
            "volume_anomalo": (0.55, 0.15),
            "dispositivo_desconhecido": (0.3, 0.46),
            "frequencia_conexoes": (0.50, 0.15),
        },
    },
    "risco": {
        "risco": 0.90,
        "perfil": {
            "taxa_pacotes_suspeitos": (0.85, 0.10),
            "uso_porta_insegura": (1.0, 0.0),
            "volume_anomalo": (0.75, 0.15),
            "dispositivo_desconhecido": (0.6, 0.49),
            "frequencia_conexoes": (0.75, 0.15),
        },
    },
}


def _amostra(cenario: str, rng: random.Random) -> dict:
    perfil = CENARIOS[cenario]["perfil"]
    features = {}
    for nome in FEATURES:
        media, desvio = perfil[nome]
        valor = rng.gauss(media, desvio) if desvio else media
        if nome in ("uso_porta_insegura", "dispositivo_desconhecido"):
            # features binárias: sorteia 0/1 com a probabilidade do cenário
            valor = 1.0 if rng.random() < min(max(media, 0.0), 1.0) else 0.0
        features[nome] = round(min(max(valor, 0.0), 1.0), 4)
    return {
        "features": features,
        "risco_esperado": CENARIOS[cenario]["risco"],
        "cenario": cenario,
    }


def gerar_dataset(n_por_cenario: int = 60, semente: int = 42) -> list[dict]:
    rng = random.Random(semente)
    dados = [_amostra(c, rng) for c in CENARIOS for _ in range(n_por_cenario)]
    rng.shuffle(dados)
    return dados


def dividir_treino_teste(dados: list[dict], proporcao_teste: float = 0.3,
                         semente: int = 7) -> tuple[list[dict], list[dict]]:
    """Separa treino (ajusta os pesos) e teste (só valida, nunca treina)."""
    copia = list(dados)
    random.Random(semente).shuffle(copia)
    corte = int(len(copia) * (1 - proporcao_teste))
    return copia[:corte], copia[corte:]
