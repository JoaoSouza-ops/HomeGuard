import psoMock from "./psoMock.json";

// Dados falsos no MESMO formato dos schemas Dispositivo/Alerta da API
// (docs/03-BACKEND-API.md). Usados quando o backend está offline (modo demonstração).
const minutosAtras = (m) => new Date(Date.now() - m * 60_000).toISOString();

export function gerarDispositivosMock() {
  return [
    {
      id: "AA:BB:CC:DD:EE:01",
      nome: "ESP32 - Sensor Temperatura",
      ip: "192.168.4.11",
      ultima_atividade: minutosAtras(0),
      nivel_risco: "normal",
      score_risco: 0.12,
    },
    {
      id: "AA:BB:CC:DD:EE:02",
      nome: "ESP32 - Dispositivo Vulneravel",
      ip: "192.168.4.12",
      ultima_atividade: minutosAtras(1),
      nivel_risco: "risco",
      score_risco: 0.87,
    },
    {
      id: "AA:BB:CC:DD:EE:03",
      nome: "Câmera da Sala",
      ip: "192.168.4.21",
      ultima_atividade: minutosAtras(3),
      nivel_risco: "atencao",
      score_risco: 0.48,
    },
    {
      id: "AA:BB:CC:DD:EE:04",
      nome: "Lâmpada Inteligente",
      ip: "192.168.4.22",
      ultima_atividade: minutosAtras(2),
      nivel_risco: "normal",
      score_risco: 0.09,
    },
  ];
}

export function gerarAlertasMock() {
  return [
    {
      id: "alerta-3",
      dispositivo_id: "AA:BB:CC:DD:EE:03",
      descricao: "Volume de dados acima do histórico do dispositivo",
      nivel_risco: "atencao",
      timestamp: minutosAtras(4),
    },
    {
      id: "alerta-2",
      dispositivo_id: "AA:BB:CC:DD:EE:02",
      descricao: "Conexões repetidas na porta Telnet (23)",
      nivel_risco: "risco",
      timestamp: minutosAtras(6),
    },
    {
      id: "alerta-1",
      dispositivo_id: "AA:BB:CC:DD:EE:02",
      descricao: "Porta Telnet (23) aberta detectada",
      nivel_risco: "risco",
      timestamp: minutosAtras(9),
    },
  ];
}

// Relatório real de um treino do PSO (gerado por backend/scripts/treinar_pso.py).
export const psoRelatorioMock = psoMock;

// Histórico simulado de score (modo demonstração): 24 pontos, um a cada 5 min,
// terminando no score atual de cada dispositivo.
export function gerarHistoricoMock(dispositivos, pontos = 24) {
  const agora = Date.now();
  return Array.from({ length: pontos }, (_, i) => {
    const restante = pontos - 1 - i;
    const linha = { t: agora - restante * 300_000 };
    dispositivos.forEach((d, k) => {
      const ruido = Math.sin(i * 0.9 + k * 2) * 0.05 + Math.cos(i * 0.4 + k) * 0.03;
      const tendencia = d.score_risco > 0.7 ? (i / pontos) * 0.35 - 0.35 : 0;
      linha[d.id] = Math.min(1, Math.max(0, +(d.score_risco + tendencia * (restante / pontos) + ruido * (restante ? 1 : 0)).toFixed(3)));
    });
    return linha;
  });
}
