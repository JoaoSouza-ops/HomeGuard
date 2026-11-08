"""Teste manual da captura: le um .pcap real e passa os pacotes pelos analisadores.

Uso (dentro de backend/, com a venv ativa):
    python scripts/testar_captura.py C:\\caminho\\para\\pequeno.pcap
    python scripts/testar_captura.py C:\\caminho\\para\\pequeno.pcap --limite 100

O caminho do TShark vem de TSHARK_PATH (arquivo .env na raiz do repositorio).
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

# Permite "from app..." mesmo rodando o arquivo direto de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.capture.file_capture import ler_pcap  # noqa: E402
from app.domain.analyzers.factory import AnalyzerFactory  # noqa: E402
from app.infra.config import obter_tshark_path  # noqa: E402

EXEMPLOS_POR_PROTOCOLO = 3


def main() -> int:
    parser = argparse.ArgumentParser(description="Testa captura + analisadores com um .pcap")
    parser.add_argument("pcap", help="caminho do arquivo .pcap")
    parser.add_argument("-n", "--limite", type=int, default=50,
                        help="quantos pacotes ler (padrao: 50)")
    args = parser.parse_args()

    if not Path(args.pcap).is_file():
        print(f"ERRO: arquivo nao encontrado: {args.pcap}")
        return 1

    tshark_path = obter_tshark_path()
    print(f"TSHARK_PATH: {tshark_path}")
    print(f"Arquivo: {args.pcap}")
    print(f"Lendo ate {args.limite} pacotes...\n")

    contagem = Counter()
    exemplos = Counter()
    pacotes = ler_pcap(args.pcap, tshark_path)

    try:
        for numero, pacote in enumerate(pacotes, start=1):
            if numero > args.limite:
                break

            protocolo = pacote.transport_layer
            if protocolo is None:
                contagem["sem TCP/UDP (ignorado)"] += 1
                continue

            try:
                analisador = AnalyzerFactory.get_analyzer(protocolo)
                features = analisador.extract_features(pacote)
            except ValueError:
                contagem[f"{protocolo} (nao suportado)"] += 1
                continue
            except AttributeError as erro:
                contagem[f"{protocolo} (erro ao ler campo)"] += 1
                print(f"[aviso] pacote {numero}: {erro}")
                continue

            contagem[protocolo] += 1
            if exemplos[protocolo] < EXEMPLOS_POR_PROTOCOLO:
                exemplos[protocolo] += 1
                print(f"{protocolo}: {features}")
    finally:
        pacotes.close()

    print("\nResumo:")
    for nome, quantidade in contagem.most_common():
        print(f"  {nome}: {quantidade}")

    ok = contagem["TCP"] > 0 and contagem["UDP"] > 0
    print("\nRESULTADO:", "PASSOU (TCP e UDP analisados)" if ok else "FALHOU (faltou TCP ou UDP)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
