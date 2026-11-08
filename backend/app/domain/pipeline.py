from collections import Counter
from collections.abc import Iterable, Iterator

from app.domain.analyzers.factory import AnalyzerFactory


class PipelineFeatures:
    """Transforma pacotes brutos em dicionarios de features.

    Pacotes sem camada de transporte (ARP, ICMPv6, IGMP...) ou com protocolo
    que nao temos analisador sao descartados, mas contados em `descartados`.
    Esta classe nao sabe de onde os pacotes vem (arquivo ou rede ao vivo):
    quem chama entrega o iteravel de pacotes.
    """

    def __init__(self) -> None:
        self.processados = 0
        self.descartados: Counter = Counter()

    def processar(self, pacotes: Iterable) -> Iterator[dict]:
        for pacote in pacotes:
            protocolo = pacote.transport_layer

            if protocolo is None:
                self.descartados["sem_camada_de_transporte"] += 1
                continue

            try:
                analisador = AnalyzerFactory.get_analyzer(protocolo)
            except ValueError:
                self.descartados[f"nao_suportado_{protocolo}"] += 1
                continue

            self.processados += 1
            yield analisador.extract_features(pacote)
