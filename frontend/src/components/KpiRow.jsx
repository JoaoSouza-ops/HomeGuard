import { NIVEIS, TEXTOS } from "../services/risco.js";

export default function KpiRow({ dispositivos }) {
  const contagem = Object.fromEntries(NIVEIS.map((n) => [n, 0]));
  dispositivos.forEach((d) => {
    if (contagem[d.nivel_risco] !== undefined) contagem[d.nivel_risco] += 1;
  });
  const media = dispositivos.length
    ? dispositivos.reduce((s, d) => s + d.score_risco, 0) / dispositivos.length
    : 0;

  return (
    <section className="kpis" aria-label="Resumo da rede">
      <div className="kpi">
        <span className="kpi__rotulo">Dispositivos</span>
        <span className="kpi__valor">{dispositivos.length}</span>
      </div>
      {NIVEIS.map((n) => (
        <div className={`kpi kpi--${n}`} key={n}>
          <span className="kpi__rotulo">{TEXTOS[n]}</span>
          <span className="kpi__valor">{contagem[n]}</span>
        </div>
      ))}
      <div className="kpi">
        <span className="kpi__rotulo">Score médio</span>
        <span className="kpi__valor">{media.toFixed(2)}</span>
      </div>
    </section>
  );
}
