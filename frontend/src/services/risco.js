// Rótulos, cores e regras de risco compartilhados pela interface.
// Os limiares espelham backend/app/domain/pso/modelo.py.
export const LIMIAR_ATENCAO = 0.3;
export const LIMIAR_RISCO = 0.7;

export const NIVEIS = ["normal", "atencao", "risco"];

export const TEXTOS = { normal: "Normal", atencao: "Atenção", risco: "Risco" };

export const FEATURES = [
  { chave: "taxa_pacotes_suspeitos", rotulo: "Pacotes suspeitos", binaria: false },
  { chave: "uso_porta_insegura", rotulo: "Porta insegura (Telnet/FTP)", binaria: true },
  { chave: "volume_anomalo", rotulo: "Volume anômalo", binaria: false },
  { chave: "dispositivo_desconhecido", rotulo: "Dispositivo desconhecido", binaria: true },
  { chave: "frequencia_conexoes", rotulo: "Frequência de conexões", binaria: false },
];

export function classificar(score) {
  if (score < LIMIAR_ATENCAO) return "normal";
  if (score < LIMIAR_RISCO) return "atencao";
  return "risco";
}

// Mesma fórmula de calcular_score_risco (backend): média ponderada normalizada.
export function calcularScore(pesos, features) {
  const soma = pesos.reduce((a, b) => a + b, 0);
  if (soma <= 0) return 0;
  const bruto = FEATURES.reduce((acc, f, i) => acc + pesos[i] * (features[f.chave] ?? 0), 0);
  return Math.min(Math.max(bruto / soma, 0), 1);
}

export function contribuicoes(pesos, features) {
  const soma = pesos.reduce((a, b) => a + b, 0) || 1;
  return FEATURES.map((f, i) => ({
    ...f,
    valor: (pesos[i] * (features[f.chave] ?? 0)) / soma,
  }));
}

export function tempoRelativo(iso, agora = Date.now()) {
  const seg = Math.max(0, Math.round((agora - new Date(iso).getTime()) / 1000));
  if (seg < 60) return "agora há pouco";
  if (seg < 3600) return `há ${Math.floor(seg / 60)} min`;
  if (seg < 86400) return `há ${Math.floor(seg / 3600)} h`;
  return `há ${Math.floor(seg / 86400)} d`;
}
