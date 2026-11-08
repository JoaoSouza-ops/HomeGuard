import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import RiskBadge from "./RiskBadge.jsx";
import { LIMIAR_ATENCAO, LIMIAR_RISCO, NIVEIS, TEXTOS } from "../services/risco.js";

// Paleta categórica validada (scripts/validate_palette.js): azul, laranja, verde-água, violeta.
const SERIES = ["var(--serie-1)", "var(--serie-2)", "var(--serie-3)", "var(--serie-4)"];
const eixo = { fontSize: 12, fill: "var(--texto-2)" };
const dica = {
  contentStyle: {
    background: "var(--superficie)", border: "1px solid var(--borda)",
    borderRadius: 8, color: "var(--texto)", fontSize: 13,
  },
};
const hora = (t) => new Date(t).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

export default function AnalisePage({ dispositivos, alertas, historico, modo }) {
  const porScore = [...dispositivos].sort((a, b) => b.score_risco - a.score_risco);
  const nomes = Object.fromEntries(dispositivos.map((d) => [d.id, d.nome]));

  // alertas por dispositivo, empilhados por nível
  const contagem = dispositivos.map((d) => {
    const linha = { nome: d.nome };
    NIVEIS.forEach((n) => (linha[n] = alertas.filter((a) => a.dispositivo_id === d.id && a.nivel_risco === n).length));
    return linha;
  });

  return (
    <div className="analise">
      <section className="painel painel--largo" aria-labelledby="t-hist">
        <h2 id="t-hist" className="painel__titulo">Evolução do score no tempo</h2>
        <p className="ajuda">
          {modo === "demo"
            ? "Histórico simulado (modo demonstração)."
            : `Pontos coletados desde que esta página abriu (${historico.length}). A API ainda não guarda histórico.`}
        </p>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={historico} margin={{ top: 12, right: 16, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="var(--grade)" vertical={false} />
            <XAxis dataKey="t" tickFormatter={hora} tick={eixo} tickLine={false} axisLine={{ stroke: "var(--grade)" }} minTickGap={32} />
            <YAxis domain={[0, 1]} tick={eixo} tickLine={false} axisLine={false} width={36} />
            <ReferenceLine y={LIMIAR_ATENCAO} stroke="var(--atencao)" strokeDasharray="4 4" />
            <ReferenceLine y={LIMIAR_RISCO} stroke="var(--risco)" strokeDasharray="4 4" />
            <Tooltip {...dica} labelFormatter={hora} formatter={(v, id) => [Number(v).toFixed(2), nomes[id] ?? id]} />
            <Legend formatter={(id) => <span style={{ color: "var(--texto-2)" }}>{nomes[id] ?? id}</span>} />
            {dispositivos.slice(0, 4).map((d, i) => (
              <Line key={d.id} type="monotone" dataKey={d.id} stroke={SERIES[i]} strokeWidth={2} dot={historico.length < 3} activeDot={{ r: 4 }} isAnimationActive={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
        <p className="ajuda ajuda--limiar">Linhas tracejadas: limiar de Atenção (0,30) e de Risco (0,70).</p>
      </section>

      <div className="grade-dupla">
        <section className="painel" aria-labelledby="t-score">
          <h2 id="t-score" className="painel__titulo">Score atual por dispositivo</h2>
          <ResponsiveContainer width="100%" height={Math.max(160, porScore.length * 48)}>
            <BarChart data={porScore} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
              <CartesianGrid stroke="var(--grade)" horizontal={false} />
              <XAxis type="number" domain={[0, 1]} tick={eixo} tickLine={false} axisLine={{ stroke: "var(--grade)" }} />
              <YAxis type="category" dataKey="nome" tick={eixo} tickLine={false} axisLine={false} width={150} />
              <ReferenceLine x={LIMIAR_ATENCAO} stroke="var(--atencao)" strokeDasharray="4 4" />
              <ReferenceLine x={LIMIAR_RISCO} stroke="var(--risco)" strokeDasharray="4 4" />
              <Tooltip {...dica} cursor={{ fill: "var(--grade)", opacity: 0.4 }} formatter={(v) => [Number(v).toFixed(2), "Score"]} />
              <Bar dataKey="score_risco" radius={[0, 4, 4, 0]} barSize={20} isAnimationActive={false}>
                {porScore.map((d) => (
                  <Cell key={d.id} fill={`var(--${d.nivel_risco})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <details className="tabela-alt">
            <summary>Ver como tabela</summary>
            <table>
              <thead><tr><th scope="col">Dispositivo</th><th scope="col">Score</th><th scope="col">Nível</th></tr></thead>
              <tbody>
                {porScore.map((d) => (
                  <tr key={d.id}><td>{d.nome}</td><td>{d.score_risco.toFixed(2)}</td><td><RiskBadge nivel={d.nivel_risco} /></td></tr>
                ))}
              </tbody>
            </table>
          </details>
        </section>

        <section className="painel" aria-labelledby="t-alertas">
          <h2 id="t-alertas" className="painel__titulo">Alertas por dispositivo</h2>
          {alertas.length === 0 ? (
            <p className="vazio">Sem alertas para analisar.</p>
          ) : (
            <ResponsiveContainer width="100%" height={Math.max(160, contagem.length * 48)}>
              <BarChart data={contagem} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid stroke="var(--grade)" horizontal={false} />
                <XAxis type="number" allowDecimals={false} tick={eixo} tickLine={false} axisLine={{ stroke: "var(--grade)" }} />
                <YAxis type="category" dataKey="nome" tick={eixo} tickLine={false} axisLine={false} width={150} />
                <Tooltip {...dica} cursor={{ fill: "var(--grade)", opacity: 0.4 }} />
                <Legend formatter={(n) => <span style={{ color: "var(--texto-2)" }}>{TEXTOS[n]}</span>} />
                {NIVEIS.map((n) => (
                  <Bar key={n} dataKey={n} name={n} stackId="a" fill={`var(--${n})`} stroke="var(--superficie)" strokeWidth={2} barSize={20} isAnimationActive={false} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          )}
        </section>
      </div>
    </div>
  );
}
