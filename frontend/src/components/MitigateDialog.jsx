import { useEffect, useRef, useState } from "react";

const ACOES = [
  { valor: "bloquear_porta", rotulo: "Bloquear porta (ex.: Telnet 23)" },
  { valor: "bloquear_ip", rotulo: "Bloquear IP do dispositivo" },
];

export default function MitigateDialog({ dispositivo, onConfirmar, onCancelar }) {
  const [acao, setAcao] = useState(ACOES[0].valor);
  const [justificativa, setJustificativa] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || el.open) return;
    if (typeof el.showModal === "function") el.showModal();
    else el.setAttribute("open", ""); // jsdom não implementa showModal
  }, []);

  async function enviar(e) {
    e.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      await onConfirmar(dispositivo, acao, justificativa);
    } catch {
      setErro("Não foi possível enviar a mitigação. Tente novamente.");
      setEnviando(false);
    }
  }

  return (
    <dialog ref={ref} className="dialogo" onCancel={onCancelar} aria-labelledby="titulo-mitigar">
      <form onSubmit={enviar}>
        <h2 id="titulo-mitigar">Mitigar {dispositivo.nome}</h2>
        <p className="dialogo__aviso">
          Use apenas na rede de testes isolada. A ação bloqueia o tráfego do dispositivo ({dispositivo.ip}).
        </p>
        <label className="campo">
          Ação
          <select value={acao} onChange={(e) => setAcao(e.target.value)}>
            {ACOES.map((a) => (
              <option key={a.valor} value={a.valor}>
                {a.rotulo}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          Justificativa (opcional)
          <textarea
            rows="3"
            value={justificativa}
            onChange={(e) => setJustificativa(e.target.value)}
            placeholder="Ex.: Telnet exposto com senha em texto puro"
          />
        </label>
        {erro && (
          <p role="alert" className="dialogo__erro">
            {erro}
          </p>
        )}
        <div className="dialogo__acoes">
          <button type="button" className="btn" onClick={onCancelar} disabled={enviando}>
            Cancelar
          </button>
          <button type="submit" className="btn btn--perigo" disabled={enviando}>
            {enviando ? "Enviando…" : "Confirmar mitigação"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
