"""Treina o PSO e salva app/domain/pso/pesos_treinados.json.

Uso (dentro de backend/):  python scripts/treinar_pso.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.domain.pso.servico import treinar_e_salvar  # noqa: E402


def main() -> int:
    r = treinar_e_salvar()
    print("Pesos:", dict(zip(r["features"], r["pesos"])))
    print(f"Erro final (treino): {r['historico_erro'][-1]:.5f}")
    t = r["metricas_teste"]
    print(f"Teste -> MSE {t['mse']:.5f} | MAE {t['mae']:.4f} | acuracia {t['acuracia']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
