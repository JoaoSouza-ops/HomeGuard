"""Teste manual de ponta a ponta: .pcap -> capture -> pipeline -> features.

Uso (dentro de backend/, com a venv ativa):
    python scripts/testar_pipeline.py C:\\caminho\\para\\pequeno.pcap
    python scripts/testar_pipeline.py C:\\caminho\\para\\pequeno.pcap --limite 200

Atencao: a saida mostra IPs e MACs reais da rede capturada.
"""
import argparse
import sys
from collections import Counter
from itertools import islice
from pathlib import Path

# Permite "from app..." mesmo rodando o arquivo direto de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.capture.file_capture import ler_pcap  # noqa: E402
from app.domain.pipeline import PipelineFeatures  # noqa: E402
from app.infra.config import obter_tshark_path  # noqa: E402

EXEMPLOS = 5
ORIGENS_MOSTRADAS = 5


def main() -> int:
    parser = argparse.ArgumentParser(description="Testa capture + pipeline com um .pcap")
    parser.add_argument("pcap", help="caminho do arquivo .pcap")
    parser.add_argument("-n", "--limite", type=int, default=100,
                        help="quantos pacotes ler (padrao: 100)")
    args = parser.parse_args()

    if not Path(args.pcap).is_file():
        print(f"ERRO: arquivo nao encontrado: {args.pcap}")
        return 1

    print(f"Arquivo: {args.pcap}")
    print(f"Lendo ate {args.limite} pacotes...\n")

    pacotes = ler_pcap(args.pcap, obter_tshark_path())
    pipeline = PipelineFeatures()
    mostrados = 0
    origens = Counter()
    sem_ip = 0
    sem_mac = 0

    try:
        for features in pipeline.processar(islice(pacotes, args.limite)):
            if mostrados < EXEMPLOS:
                mostrados += 1
                print(features)

            origens[(features["src_mac"], features["src_ip"])] += 1
            if features["src_ip"] is None:
                sem_ip += 1
            if features["src_mac"] is None:
                sem_mac += 1
    finally:
        pacotes.close()

    print("\nResumo:")
    print(f"  processados: {pipeline.processados}")
    print(f"  descartados: {dict(pipeline.descartados)}")
    print(f"  sem src_ip: {sem_ip} | sem src_mac: {sem_mac}")

    print("\nOrigens mais frequentes (src_mac, src_ip):")
    for (mac, ip), quantidade in origens.most_common(ORIGENS_MOSTRADAS):
        print(f"  {mac} | {ip}: {quantidade}")

    com_origem = pipeline.processados - max(sem_ip, sem_mac)
    ok = pipeline.processados > 0 and com_origem > 0
    print("\nRESULTADO:", "PASSOU" if ok else "FALHOU (nenhum pacote com IP e MAC de origem)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

