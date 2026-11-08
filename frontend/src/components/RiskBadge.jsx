import { TEXTOS } from "../services/risco.js";

// Cor nunca é o único sinal: cada nível tem ícone + texto.
const ICONES = {
  normal: <path d="M3.5 8.5l3 3 6-7" />,
  atencao: <path d="M8 3.5v5.5M8 11.5v.5" />,
  risco: <path d="M4.5 4.5l7 7M11.5 4.5l-7 7" />,
};

export default function RiskBadge({ nivel }) {
  const n = TEXTOS[nivel] ? nivel : "normal";
  return (
    <span className={`badge badge--${n}`}>
      <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true" className="badge__icone">
        {ICONES[n]}
      </svg>
      {TEXTOS[n]}
    </span>
  );
}
