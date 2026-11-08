import { useState } from "react";
import AnalisePage from "./components/AnalisePage.jsx";
import AlertFeed from "./components/AlertFeed.jsx";
import DeviceCard from "./components/DeviceCard.jsx";
import HouseMap from "./components/HouseMap.jsx";
import KpiRow from "./components/KpiRow.jsx";
import MitigacoesPage from "./components/MitigacoesPage.jsx";
import MitigateDialog from "./components/MitigateDialog.jsx";
import PsoPanel from "./components/PsoPanel.jsx";
import { useHomeGuard } from "./hooks/useHomeGuard.js";

function StatusConexao({ modo, atualizadoEm }) {
  const textos = {
    carregando: "Conectando…",
    online: "API conectada",
    demo: "Modo demonstração (API offline)",
  };
  return (
    <div className={`conexao conexao--${modo}`} role="status">
      <span className="conexao__ponto" aria-hidden="true" />
      {textos[modo]}
      {atualizadoEm && modo !== "carregando" && (
        <span className="conexao__hora"> · {atualizadoEm.toLocaleTimeString("pt-BR")}</span>
      )}
    </div>
  );
}

const ABAS = [
  { id: "casa", rotulo: "Casa Virtual" },
  { id: "analise", rotulo: "Análise de risco" },
  { id: "mitigacoes", rotulo: "Mitigações" },
];

export default function App() {
  const hg = useHomeGuard();
  const [selecionadoId, setSelecionadoId] = useState(null);
  const [alvoMitigacao, setAlvoMitigacao] = useState(null);
  const [aba, setAba] = useState("casa");

  async function confirmarMitigacao(dispositivo, acao, justificativa) {
    await hg.mitigar(dispositivo, acao, justificativa);
    setAlvoMitigacao(null);
  }

  return (
    <div className="app">
      <header className="topo">
        <div className="topo__marca">
          <svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">
            <rect width="32" height="32" rx="8" className="topo__logo" />
            <path d="M16 6 6 14v12h7v-7h6v7h7V14z" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinejoin="round" />
          </svg>
          <div>
            <h1>HomeGuard</h1>
            <p>Casa Virtual · monitoramento de risco IoT</p>
          </div>
        </div>
        <StatusConexao modo={hg.modo} atualizadoEm={hg.atualizadoEm} />
      </header>

      {hg.modo === "demo" && (
        <p className="aviso" role="note">
          O backend não respondeu, então estes são dados de exemplo. Suba a API (<code>uvicorn app.main:app</code>) e a
          página passa a usar os dados reais sozinha. A mitigação aqui é apenas simulada.
        </p>
      )}

      <nav className="abas" role="tablist" aria-label="Dashboards">
        {ABAS.map((a) => (
          <button
            key={a.id}
            type="button"
            role="tab"
            aria-selected={aba === a.id}
            className={`aba${aba === a.id ? " aba--ativa" : ""}`}
            onClick={() => setAba(a.id)}
          >
            {a.rotulo}
            {a.id === "mitigacoes" && hg.registro.length > 0 && <span className="aba__contador">{hg.registro.length}</span>}
          </button>
        ))}
      </nav>

      <main className="conteudo">
        <KpiRow dispositivos={hg.dispositivos} />

        {aba === "analise" && (
          <AnalisePage dispositivos={hg.dispositivos} alertas={hg.alertas} historico={hg.historico} modo={hg.modo} />
        )}
        {aba === "mitigacoes" && <MitigacoesPage registro={hg.registro} />}
        {aba === "casa" && (
          <>

        <div className="grade-principal">
          <section className="painel" aria-labelledby="titulo-casa">
            <h2 id="titulo-casa" className="painel__titulo">
              Casa Virtual
            </h2>
            <HouseMap dispositivos={hg.dispositivos} selecionadoId={selecionadoId} onSelecionar={setSelecionadoId} />
          </section>
          <AlertFeed alertas={hg.alertas} dispositivos={hg.dispositivos} />
        </div>

        <section aria-labelledby="titulo-dispositivos">
          <h2 id="titulo-dispositivos" className="painel__titulo painel__titulo--solto">
            Dispositivos
          </h2>
          {hg.dispositivos.length === 0 ? (
            <p className="vazio">{hg.modo === "carregando" ? "Carregando dispositivos…" : "Nenhum dispositivo visto na rede ainda."}</p>
          ) : (
            <div className="cards">
              {hg.dispositivos.map((d) => (
                <DeviceCard
                  key={d.id}
                  dispositivo={d}
                  selecionado={d.id === selecionadoId}
                  mitigacao={hg.mitigados[d.id]}
                  onSelecionar={setSelecionadoId}
                  onMitigar={setAlvoMitigacao}
                />
              ))}
            </div>
          )}
        </section>

        <PsoPanel pso={hg.pso} modo={hg.modo} onTreinar={hg.treinar} />
          </>
        )}
      </main>

      {alvoMitigacao && (
        <MitigateDialog
          dispositivo={alvoMitigacao}
          onConfirmar={confirmarMitigacao}
          onCancelar={() => setAlvoMitigacao(null)}
        />
      )}
    </div>
  );
}
