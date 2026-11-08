import RiskBadge from "./RiskBadge.jsx";
import { classificar } from "../services/risco.js";

const ROTULO_ACAO = { bloquear_porta: "Bloquear porta", bloquear_ip: "Bloquear IP" };

function Score({ valor }) {
  if (valor == null) return <span className="texto-3">sem nova leitura</span>;
  return (
    <span className="score-par">
      {valor.toFixed(2)} <RiskBadge nivel={classificar(valor)} />
    </span>
  );
}

export default function MitigacoesPage({ registro }) {
  return (
    <section className="painel painel--largo" aria-labelledby="t-mit">
      <h2 id="t-mit" className="painel__titulo">Histórico de mitigações</h2>
      <p className="ajuda">
        Registro das ações disparadas neste navegador. “Depois” só aparece na demonstração (simulado): a API real ainda
        não recalcula o score após a mitigação.
      </p>
      {registro.length === 0 ? (
        <p className="vazio">Nenhuma mitigação ainda. Use o botão Mitigar em um dispositivo em Atenção ou Risco.</p>
      ) : (
        <div className="tabela-rolagem">
          <table className="tabela">
            <thead>
              <tr>
                <th scope="col">Quando</th>
                <th scope="col">Dispositivo</th>
                <th scope="col">Ação</th>
                <th scope="col">Justificativa</th>
                <th scope="col">Antes</th>
                <th scope="col">Depois</th>
              </tr>
            </thead>
            <tbody>
              {registro.map((e) => (
                <tr key={e.id}>
                  <td>{new Date(e.em).toLocaleString("pt-BR")}</td>
                  <td>{e.nome}</td>
                  <td>{ROTULO_ACAO[e.acao] ?? e.acao}{e.simulado && <span className="tag-sim">simulado</span>}</td>
                  <td>{e.justificativa || "—"}</td>
                  <td><Score valor={e.score_antes} /></td>
                  <td><Score valor={e.score_depois} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
