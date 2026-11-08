"""Teste manual do banco: cria o arquivo SQLite de verdade, grava e le um dispositivo.

Uso (dentro de backend/, com a venv ativa):
    python scripts/testar_banco.py

Usa a DATABASE_URL do .env (ou sqlite:///./homeguard.db se nao existir).
O arquivo .db e ignorado pelo Git (*.db no .gitignore).
Pode rodar varias vezes: o dispositivo de teste e atualizado, nao duplicado.
"""
import sys
from datetime import datetime
from pathlib import Path

# Permite "from app..." mesmo rodando o arquivo direto de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.infra.config import obter_database_url  # noqa: E402
from app.infra.database import SessionLocal, criar_tabelas  # noqa: E402
from app.infra.models import DispositivoModel  # noqa: E402

ID_TESTE = "TESTE:BANCO:00:00:00:01"


def main() -> int:
    print(f"DATABASE_URL: {obter_database_url()}")

    criar_tabelas()
    print("Tabelas criadas (ou ja existiam).")

    with SessionLocal() as sessao:
        agora = datetime.now().replace(microsecond=0)
        sessao.merge(
            DispositivoModel(
                id=ID_TESTE,
                nome="Dispositivo de teste do banco",
                ip="192.168.4.99",
                ultima_atividade=agora,
                nivel_risco="normal",
                score_risco=0.5,
            )
        )
        sessao.commit()

        lido = sessao.get(DispositivoModel, ID_TESTE)
        total = sessao.query(DispositivoModel).count()

    print(f"Lido do banco: {lido.id} | {lido.nome} | {lido.ultima_atividade} | score {lido.score_risco}")
    print(f"Total de dispositivos na tabela: {total}")

    ok = lido is not None and lido.ultima_atividade == agora
    print("\nRESULTADO:", "PASSOU" if ok else "FALHOU")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
