import axios from "axios";

// Sem URL fixa no código: vem do ambiente (padrão /api, ver .env.example).
export const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

export const api = axios.create({ baseURL: API_BASE_URL, timeout: 5000 });

export async function listarDispositivos() {
  const { data } = await api.get("/devices");
  return data;
}

export async function listarAlertas() {
  const { data } = await api.get("/alerts");
  return data;
}

export async function mitigarDispositivo(deviceId, acao, justificativa) {
  const { data } = await api.post(`/devices/${encodeURIComponent(deviceId)}/mitigate`, {
    acao,
    justificativa: justificativa || null,
  });
  return data;
}

export async function obterPso() {
  const { data } = await api.get("/pso/pesos");
  return data;
}

export async function treinarPso(parametros = {}) {
  const { data } = await api.post("/pso/treinar", parametros);
  return data;
}
