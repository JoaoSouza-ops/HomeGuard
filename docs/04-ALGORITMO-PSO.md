# 04 — Algoritmo de Inteligência Computacional (PSO)

**Responsável sugerido:** Engenheiro de IA (Inteligência Computacional)

Este é o requisito de "Computational Intelligence & Algorithm Optimization" do edital. Leiam com calma — é a parte que a banca mais vai testar no oral, então qualquer integrante precisa saber explicar isso, não só quem implementou.

## 1. O que é PSO (explicação sem jargão)

Imagine um bando de pássaros procurando comida em um campo. Nenhum pássaro sabe exatamente onde está a comida, mas cada um sabe:
1. O melhor lugar que **ele mesmo** já encontrou (`pBest` — personal best).
2. O melhor lugar que **o bando inteiro** já encontrou (`gBest` — global best).

Cada pássaro ajusta sua direção de voo combinando "para onde eu já fui bem" com "para onde o bando está indo bem", com um pouco de aleatoriedade. Depois de várias rodadas, o bando converge para a melhor região do campo.

No PSO computacional, cada "pássaro" é chamado de **partícula**, e o "campo" é o espaço de possíveis soluções do nosso problema.

## 2. Modelando o problema do HomeGuard como um problema de otimização

**O que queremos otimizar:** os **pesos** que cada feature de tráfego tem no cálculo do score de risco de um dispositivo.

### Features extraídas por dispositivo (numa janela de tempo, ex: últimos 30 segundos)

| Feature | Descrição | Faixa |
|---|---|---|
| `taxa_pacotes_suspeitos` | % de pacotes em portas inseguras (23, 21) sobre o total | 0.0 – 1.0 |
| `uso_porta_insegura` | 1 se usa Telnet/FTP sem criptografia, 0 caso contrário | 0 ou 1 |
| `volume_anomalo` | desvio do volume de dados em relação à média histórica do dispositivo | 0.0 – 1.0 (normalizado) |
| `dispositivo_desconhecido` | 1 se o MAC nunca foi visto antes, 0 caso contrário | 0 ou 1 |
| `frequencia_conexoes` | número de novas conexões por minuto | 0.0 – 1.0 (normalizado) |

### O que é uma "partícula" aqui

Cada partícula é um vetor de 5 pesos, um para cada feature:

```
partícula = [w1, w2, w3, w4, w5]   # cada peso entre 0.0 e 1.0
```

### Função de aptidão (fitness function)

```python
def calcular_score_risco(pesos: list[float], features: dict) -> float:
    """
    pesos: [w1, w2, w3, w4, w5] — vindo de uma partícula
    features: dicionário com as 5 features do dispositivo nesta janela de tempo
    Retorna um score de 0.0 (sem risco) a 1.0 (risco máximo)
    """
    score = (
        pesos[0] * features["taxa_pacotes_suspeitos"] +
        pesos[1] * features["uso_porta_insegura"] +
        pesos[2] * features["volume_anomalo"] +
        pesos[3] * features["dispositivo_desconhecido"] +
        pesos[4] * features["frequencia_conexoes"]
    )
    return min(score / sum(pesos), 1.0)  # normalizado
```

A **aptidão** de uma partícula é avaliada contra um conjunto de exemplos rotulados manualmente pela equipe (ex: "sabemos que este tráfego do ESP vulnerável é Risco real; este outro do ESP normal é Normal real"). A partícula é "boa" se o score que ela calcula bate com o rótulo esperado — ou seja, minimizamos o erro entre score previsto e rótulo real.

```python
def fitness(pesos: list[float], dataset_rotulado: list[dict]) -> float:
    """
    dataset_rotulado: lista de {"features": {...}, "risco_esperado": 0.0 a 1.0}
    Quanto MENOR o retorno, melhor a partícula (estamos minimizando o erro)
    """
    erro_total = 0.0
    for exemplo in dataset_rotulado:
        score_previsto = calcular_score_risco(pesos, exemplo["features"])
        erro_total += (score_previsto - exemplo["risco_esperado"]) ** 2
    return erro_total / len(dataset_rotulado)
```

> **De onde vem o `dataset_rotulado`?** Da fase de testes manuais com os ESPs (docs/02 e docs/06): vocês vão gerar tráfego conhecido (normal e malicioso) e rotular manualmente qual o risco esperado de cada situação. Isso vira o conjunto de treinamento do PSO.

## 3. Implementação com `pyswarms`

```bash
pip install pyswarms numpy
```

```python
# app/domain/pso/otimizador.py
import numpy as np
import pyswarms as ps

def treinar_pesos(dataset_rotulado: list[dict]) -> list[float]:
    def fitness_enxame(enxame_de_particulas: np.ndarray) -> np.ndarray:
        # pyswarms avalia todas as partículas de uma vez (matriz n_particulas x n_dimensoes)
        return np.array([fitness(particula, dataset_rotulado) for particula in enxame_de_particulas])

    opcoes = {"c1": 0.5, "c2": 0.3, "w": 0.9}
    # c1: quanto a partícula confia na própria experiência (pBest)
    # c2: quanto a partícula confia no bando (gBest)
    # w: inércia — quanto do movimento anterior é mantido

    otimizador = ps.single.GlobalBestPSO(
        n_particles=30,       # tamanho do "bando"
        dimensions=5,         # 5 pesos, um por feature
        options=opcoes,
        bounds=(np.zeros(5), np.ones(5)),  # cada peso entre 0.0 e 1.0
    )

    melhor_erro, melhores_pesos = otimizador.optimize(fitness_enxame, iters=100)
    return melhores_pesos.tolist()
```

## 4. Classificação final (regras de negócio, não fazem parte do PSO)

Depois de ter os pesos otimizados e calcular o `score_risco` de um dispositivo em tempo real, a classificação em categorias segue limiares simples — **estes números são um ponto de partida, ajustem com dados reais dos testes**:

```python
def classificar(score: float) -> str:
    if score < 0.3:
        return "normal"
    elif score < 0.7:
        return "atencao"
    else:
        return "risco"
```

## 5. Como treinar/re-treinar durante o desenvolvimento

1. Gerem tráfego com os dois ESPs (normal e vulnerável) por alguns minutos.
2. Salvem a captura em `.pcap` (ver `docs/02-REDE-HARDWARE.md`).
3. Extraiam as features de cada janela de tempo e rotulem manualmente (planilha simples: `features` + `risco_esperado`).
4. Rodem `treinar_pesos()` sobre esse dataset.
5. Salvem os pesos resultantes (ex: em um arquivo `pesos_treinados.json`) — o backend em produção usa esses pesos já treinados, **não re-treina a cada request**.

## 6. O que a banca pode perguntar (preparem-se)

- "Por que PSO e não um algoritmo genético?" → Resposta esperada: PSO converge geralmente mais rápido em espaços de busca contínuos (nossos pesos são números reais entre 0 e 1), enquanto GA é mais natural para espaços discretos/combinatórios. Também é mais simples de implementar e tunar (menos hiperparâmetros).
- "O que acontece se `gBest` ficar preso em um mínimo local?" → Mencionar o papel do parâmetro de inércia `w` e da aleatoriedade na velocidade de cada partícula, que ajudam a escapar de ótimos locais.
- "Como vocês validam que o modelo não está enviesado?" → Mencionar a separação entre dados de treino (usados para ajustar os pesos) e dados de teste (usados só para validar, nunca para treinar).
