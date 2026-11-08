import { TEXTOS } from "../services/risco.js";

// Planta da "Casa Virtual". O contrato da API não traz cômodo, então os
// dispositivos são distribuídos pelos cômodos na ordem em que chegam.
const COMODOS = [
  { nome: "Sala", x: 16, y: 16, w: 300, h: 170 },
  { nome: "Cozinha", x: 324, y: 16, w: 300, h: 170 },
  { nome: "Quarto", x: 16, y: 194, w: 300, h: 170 },
  { nome: "Escritório", x: 324, y: 194, w: 300, h: 170 },
];

export function posicionar(dispositivos) {
  const porComodo = COMODOS.map(() => []);
  dispositivos.forEach((d, i) => porComodo[i % COMODOS.length].push(d));
  return porComodo.flatMap((lista, c) =>
    lista.map((d, i) => {
      const r = COMODOS[c];
      const passo = r.w / (lista.length + 1);
      return { dispositivo: d, x: r.x + passo * (i + 1), y: r.y + r.h / 2 + 6 };
    }),
  );
}

export default function HouseMap({ dispositivos, selecionadoId, onSelecionar }) {
  const nos = posicionar(dispositivos);
  return (
    <svg
      className="casa"
      viewBox="0 0 640 380"
      role="group"
      aria-label="Planta da casa com os dispositivos IoT"
    >
      {COMODOS.map((c) => (
        <g key={c.nome}>
          <rect x={c.x} y={c.y} width={c.w} height={c.h} rx="14" className="casa__comodo" />
          <text x={c.x + 16} y={c.y + 28} className="casa__nome-comodo">
            {c.nome}
          </text>
        </g>
      ))}
      {nos.map(({ dispositivo: d, x, y }) => {
        const ativo = d.id === selecionadoId;
        return (
          <g
            key={d.id}
            className={`no no--${d.nivel_risco}${ativo ? " no--ativo" : ""}`}
            transform={`translate(${x} ${y})`}
            tabIndex={0}
            role="button"
            aria-label={`${d.nome}, ${TEXTOS[d.nivel_risco]}, score ${d.score_risco.toFixed(2)}`}
            onClick={() => onSelecionar(d.id)}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelecionar(d.id)}
          >
            {d.nivel_risco === "risco" && <circle r="26" className="no__pulso" />}
            <circle r="22" className="no__anel" />
            <circle r="16" className="no__miolo" />
            <text className="no__simbolo" y="5" textAnchor="middle">
              {d.nivel_risco === "normal" ? "✓" : d.nivel_risco === "atencao" ? "!" : "✕"}
            </text>
            <text className="no__rotulo" y="42" textAnchor="middle">
              {d.nome.length > 22 ? `${d.nome.slice(0, 21)}…` : d.nome}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
