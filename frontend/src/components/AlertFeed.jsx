import RiskBadge from "./RiskBadge.jsx";
import { tempoRelativo } from "../services/risco.js";

export default function AlertFeed({ alertas, dispositivos }) {
  const nomes = Object.fromEntries(dispositivos.map((d) => [d.id, d.nome]));
  return (
    <section className="painel" aria-labelledby="titulo-alertas">
      <h2 id="titulo-alertas" className="painel__titulo">
        Alertas recentes
      </h2>
      {alertas.length === 0 ? (
        <p className="vazio">Nenhum alerta. A rede está tranquila.</p>
      ) : (
        <ul className="alertas">
          {alertas.slice(0, 8).map((a) => (
            <li key={a.id} className="alerta">
              <div className="alerta__linha">
                <RiskBadge nivel={a.nivel_risco} />
                <time className="alerta__tempo" dateTime={a.timestamp}>
                  {tempoRelativo(a.timestamp)}
                </time>
              </div>
              <p className="alerta__texto">{a.descricao}</p>
              <p className="alerta__dispositivo">{nomes[a.dispositivo_id] ?? a.dispositivo_id}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
