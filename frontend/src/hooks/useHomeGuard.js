import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../services/api.js";
import {
  gerarAlertasMock,
  gerarDispositivosMock,
  gerarHistoricoMock,
  psoRelatorioMock,
} from "../services/mockData.js";
import { classificar } from "../services/risco.js";

const INTERVALO_MS = 5000;
const MAX_HISTORICO = 60;
const CHAVE_REGISTRO = "homeguard.mitigacoes";

function lerRegistro() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE_REGISTRO)) ?? [];
  } catch {
    return [];
  }
}

function gravarRegistro(registro) {
  try {
    localStorage.setItem(CHAVE_REGISTRO, JSON.stringify(registro));
  } catch {
    /* sem localStorage: o registro vale só para esta sessão */
  }
}

/**
 * Carrega dispositivos, alertas e o relatório do PSO.
 * - API no ar  -> modo "online" (atualiza a cada 5 s).
 * - API fora   -> modo "demo": usa dados mock e avisa na tela.
 * Os componentes não sabem de onde vêm os dados.
 */
export function useHomeGuard() {
  const [modo, setModo] = useState("carregando");
  const [dispositivos, setDispositivos] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [pso, setPso] = useState(null);
  const [atualizadoEm, setAtualizadoEm] = useState(null);
  const [registro, setRegistro] = useState(lerRegistro);
  const [historico, setHistorico] = useState([]);
  const modoRef = useRef("carregando");
  const mockRef = useRef(null);

  const definirModo = (m) => {
    modoRef.current = m;
    setModo(m);
  };

  const carregar = useCallback(async () => {
    try {
      const [d, a] = await Promise.all([api.listarDispositivos(), api.listarAlertas()]);
      setDispositivos(d);
      setAlertas(a);
      definirModo("online");
      setHistorico((h) => {
        if (modoRef.current === "demo") h = []; // saiu do modo demo: descarta o histórico simulado
        const linha = { t: Date.now() };
        d.forEach((x) => (linha[x.id] = x.score_risco));
        return [...h, linha].slice(-MAX_HISTORICO);
      });
      // o PSO é opcional: se a rota não existir, usa o relatório de exemplo
      try {
        setPso(await api.obterPso());
      } catch {
        setPso((atual) => atual ?? psoRelatorioMock);
      }
    } catch {
      if (!mockRef.current) {
        const d = gerarDispositivosMock();
        mockRef.current = { d, a: gerarAlertasMock() };
        setHistorico(gerarHistoricoMock(d));
      }
      setDispositivos((atual) => (modoRef.current === "demo" && atual.length ? atual : mockRef.current.d));
      setAlertas((atual) => (modoRef.current === "demo" && atual.length ? atual : mockRef.current.a));
      setPso((atual) => atual ?? psoRelatorioMock);
      definirModo("demo");
    }
    setAtualizadoEm(new Date());
  }, []);

  useEffect(() => {
    // setState acontece depois do await dentro de carregar(), nunca de forma síncrona
    // eslint-disable-next-line react-hooks/set-state-in-effect
    carregar();
    const t = setInterval(carregar, INTERVALO_MS);
    return () => clearInterval(t);
  }, [carregar]);

  const mitigar = useCallback(async (dispositivo, acao, justificativa) => {
    if (modoRef.current === "online") {
      await api.mitigarDispositivo(dispositivo.id, acao, justificativa);
    }
    const simulado = modoRef.current === "demo";
    const agora = new Date().toISOString();
    const entrada = {
      id: `${dispositivo.id}-${agora}`,
      dispositivo_id: dispositivo.id,
      nome: dispositivo.nome,
      acao,
      justificativa: justificativa || "",
      em: agora,
      score_antes: dispositivo.score_risco,
      // a API real não recalcula o score ao mitigar; só a demonstração simula o efeito
      score_depois: simulado ? 0.15 : null,
      simulado,
    };
    setRegistro((r) => {
      const novo = [entrada, ...r].slice(0, 100);
      gravarRegistro(novo);
      return novo;
    });
    setAlertas((lista) => [
      {
        id: `local-${entrada.id}`,
        dispositivo_id: dispositivo.id,
        descricao: `Mitigação solicitada: ${acao.replace("_", " ")}`,
        nivel_risco: "normal",
        timestamp: agora,
      },
      ...lista,
    ]);
    if (simulado) {
      setDispositivos((lista) =>
        lista.map((x) =>
          x.id === dispositivo.id ? { ...x, score_risco: 0.15, nivel_risco: classificar(0.15) } : x,
        ),
      );
    }
  }, []);

  const treinar = useCallback(async () => {
    const relatorio = await api.treinarPso({});
    setPso(relatorio);
  }, []);

  const mitigados = Object.fromEntries([...registro].reverse().map((e) => [e.dispositivo_id, e]));

  return { modo, dispositivos, alertas, pso, atualizadoEm, historico, registro, mitigados, mitigar, treinar, recarregar: carregar };
}
