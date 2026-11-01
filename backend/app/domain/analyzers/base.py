from abc import ABC, abstractmethod


class PacketAnalyzer(ABC):
    @abstractmethod
    def extract_features(self, packet) -> dict:
        """Recebe um pacote pyshark e devolve um dicionário de features de risco."""
        ...