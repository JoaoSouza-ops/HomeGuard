import RiskBadge from "./RiskBadge.jsx";
import { tempoRelativo } from "../services/risco.js";

export default function DeviceCard({ dispositivo, selecionado, mitigacao, onSelecionar, onMitigar }) {
  const { nome, ip, id, ultima_atividade, nivel_risco, score_risco } = dispositivo;
  const pct = Math.round(score_risco * 100);

  return (
    <article
      className={`card card--${nivel_risco}${selecionado ? " card--selecionado" : ""}`}
      onClick={() => onSelecionar?.(id)}
    >
      <header className="card__topo">
        <h3 className="card__nome">{nome}</h3>
        <RiskBadge nivel={nivel_risco} />
      </header>
      <p className="card__meta">
        <span>{ip}</span>
        <span className="card__mac">{id}</span>
      </p>
      <div className="meter" role="img" aria-label={`Score de risco ${score_risco.toFixed(2)}`}>
        <div className={`meter__preenchimento meter__preenchimento--${nivel_risco}`} style={{ width: `${pct}%` }} />
      </div>
      <footer className="card__rodape">
        <span className="card__score">
          Score <strong>{score_risco.toFixed(2)}</strong>
        </span>
        <span className="card__tempo">{tempoRelativo(ultima_atividade)}</span>
      </footer>
      {mitigacao ? (
        <p className="card__mitigado">Mitigação enviada: {mitigacao.acao.replace("_", " ")}</p>
      ) : (
        nivel_risco !== "normal" && (
          <button
            type="button"
            className="btn btn--perigo"
            onClick={(e) => {
              e.stopPropagation();
              onMitigar(dispositivo);
            }}
          >
            Mitigar
          </button>
        )
      )}
    </article>
  );
}
