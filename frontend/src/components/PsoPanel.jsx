import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import RiskBadge from "./RiskBadge.jsx";
import {
  FEATURES,
  NIVEIS,
  TEXTOS,
  calcularScore,
  classificar,
  contribuicoes,
} from "../services/risco.js";

const CORES = { linha: "var(--chart-1)", barra: "var(--chart-1)", grade: "var(--grade)", texto: "var(--texto-2)" };
const eixo = { fontSize: 12, fill: CORES.texto };
const dica = {
  contentStyle: {
    background: "var(--superficie)",
    border: "1px solid var(--borda)",
    borderRadius: 8,
    color: "var(--texto)",
    fontSize: 13,
  },
};

const ESTADO_INICIAL = {
  taxa_pacotes_suspeitos: 0.2,
  uso_porta_insegura: 0,
  volume_anomalo: 0.2,
  dispositivo_desconhecido: 0,
  frequencia_conexoes: 0.2,
};

function Simulador({ pesos }) {
  const [valores, setValores] = useState(ESTADO_INICIAL);
  const score = calcularScore(pesos, valores);
  const nivel = classificar(score);
  const partes = contribuicoes(pesos, valores);

  return (
    <div className="simulador">
      <h3 className="subtitulo">Simulador de score</h3>
      <p className="ajuda">Mexa nas features de uma janela de 30 s e veja o score com os pesos aprendidos.</p>
      <div className="simulador__corpo">
        <div className="simulador__controles">
          {FEATURES.map((f) =>
            f.binaria ? (
              <label className="controle controle--chk" key={f.chave}>
                <input
                  type="checkbox"
                  checked={valores[f.chave] === 1}
                  onChange={(e) => setValores({ ...valores, [f.chave]: e.target.checked ? 1 : 0 })}
                />
                {f.rotulo}
              </label>
            ) : (
              <label className="controle" key={f.chave}>
                <span>
                  {f.rotulo} <output>{valores[f.chave].toFixed(2)}</output>
                </span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={valores[f.chave]}
                  onChange={(e) => setValores({ ...valores, [f.chave]: Number(e.target.value) })}
                />
              </label>
            ),
          )}
        </div>
        <div className="simulador__resultado" aria-live="polite">
          <span className="simulador__score">{score.toFixed(2)}</span>
          <RiskBadge nivel={nivel} />
          <ul className="contribs">
            {partes.map((p) => (
              <li key={p.chave}>
                <span>{p.rotulo}</span>
                <span className="contribs__barra">
                  <span style={{ width: `${Math.round(p.valor * 100)}%` }} />
                </span>
                <span className="contribs__valor">{p.valor.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function Confusao({ matriz }) {
  const max = Math.max(1, ...NIVEIS.flatMap((r) => NIVEIS.map((p) => matriz[r][p])));
  return (
    <table className="confusao">
      <caption>Matriz de confusão (teste)</caption>
      <thead>
        <tr>
          <th scope="col">real \ previsto</th>
          {NIVEIS.map((n) => (
            <th scope="col" key={n}>
              {TEXTOS[n]}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {NIVEIS.map((real) => (
          <tr key={real}>
            <th scope="row">{TEXTOS[real]}</th>
            {NIVEIS.map((prev) => (
              <td
                key={prev}
                className={real === prev ? "confusao__acerto" : ""}
                style={{ "--intensidade": matriz[real][prev] / max }}
              >
                {matriz[real][prev]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function PsoPanel({ pso, modo, onTreinar }) {
  const [treinando, setTreinando] = useState(false);
  const [erro, setErro] = useState(null);
  if (!pso) return null;

  const convergencia = pso.historico_erro.map((erroMse, i) => ({ iteracao: i, erro: erroMse }));
  const pesos = FEATURES.map((f, i) => ({ nome: f.rotulo, peso: pso.pesos[i] }));
  const teste = pso.metricas_teste;

  async function treinar() {
    setTreinando(true);
    setErro(null);
    try {
      await onTreinar();
    } catch {
      setErro("Falha ao treinar. O backend está no ar?");
    } finally {
      setTreinando(false);
    }
  }

  return (
    <section className="painel painel--largo" aria-labelledby="titulo-pso">
      <header className="painel__cabecalho">
        <div>
          <h2 id="titulo-pso" className="painel__titulo">
            Motor PSO
          </h2>
          <p className="ajuda">
            Otimização por enxame de partículas que aprende o peso de cada feature no score de risco.
            {pso.fonte_dados === "sintetico" && " Treinado com dados sintéticos."}
          </p>
        </div>
        <button
          type="button"
          className="btn"
          onClick={treinar}
          disabled={treinando || modo !== "online"}
          title={modo !== "online" ? "Disponível quando a API está no ar" : undefined}
        >
          {treinando ? "Treinando…" : "Re-treinar"}
        </button>
      </header>
      {erro && <p role="alert" className="dialogo__erro">{erro}</p>}

      {teste && (
        <div className="metricas">
          <div className="metrica">
            <span>Acurácia (teste)</span>
            <strong>{(teste.acuracia * 100).toFixed(1)}%</strong>
          </div>
          <div className="metrica">
            <span>Erro MSE (teste)</span>
            <strong>{teste.mse.toFixed(4)}</strong>
          </div>
          <div className="metrica">
            <span>Erro MAE (teste)</span>
            <strong>{teste.mae.toFixed(3)}</strong>
          </div>
          <div className="metrica">
            <span>Enxame</span>
            <strong>
              {pso.particulas} × {pso.iteracoes}
            </strong>
          </div>
        </div>
      )}

      <div className="graficos">
        <figure className="grafico">
          <figcaption>Convergência: erro do melhor palpite por iteração</figcaption>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={convergencia} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
              <CartesianGrid stroke={CORES.grade} vertical={false} />
              <XAxis dataKey="iteracao" tick={eixo} tickLine={false} axisLine={{ stroke: CORES.grade }} />
              <YAxis tick={eixo} tickLine={false} axisLine={false} width={48} tickFormatter={(v) => v.toFixed(3)} />
              <Tooltip {...dica} formatter={(v) => [Number(v).toFixed(5), "Erro (MSE)"]} labelFormatter={(l) => `Iteração ${l}`} />
              <Line type="monotone" dataKey="erro" stroke={CORES.linha} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </figure>
        <figure className="grafico">
          <figcaption>Pesos aprendidos por feature</figcaption>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={pesos} layout="vertical" margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
              <CartesianGrid stroke={CORES.grade} horizontal={false} />
              <XAxis type="number" domain={[0, 1]} tick={eixo} tickLine={false} axisLine={{ stroke: CORES.grade }} />
              <YAxis type="category" dataKey="nome" tick={eixo} tickLine={false} axisLine={false} width={150} />
              <Tooltip {...dica} cursor={{ fill: "var(--grade)", opacity: 0.4 }} formatter={(v) => [Number(v).toFixed(3), "Peso"]} />
              <Bar dataKey="peso" fill={CORES.barra} radius={[0, 4, 4, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </figure>
      </div>

      <div className="pso__baixo">
        {teste && <Confusao matriz={teste.matriz_confusao} />}
        <Simulador pesos={pso.pesos} />
      </div>
    </section>
  );
}
