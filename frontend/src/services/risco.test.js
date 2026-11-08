import { calcularScore, classificar, tempoRelativo } from "./risco.js";
import psoMock from "./psoMock.json";

test("classificar respeita os limiares 0.3 e 0.7", () => {
  expect(classificar(0.29)).toBe("normal");
  expect(classificar(0.3)).toBe("atencao");
  expect(classificar(0.69)).toBe("atencao");
  expect(classificar(0.7)).toBe("risco");
});

test("score com pesos zerados é 0 (sem dividir por zero)", () => {
  expect(calcularScore([0, 0, 0, 0, 0], { taxa_pacotes_suspeitos: 1 })).toBe(0);
});

test("score é a média ponderada normalizada", () => {
  const f = { taxa_pacotes_suspeitos: 1, uso_porta_insegura: 0, volume_anomalo: 0, dispositivo_desconhecido: 0, frequencia_conexoes: 0 };
  expect(calcularScore([1, 1, 1, 1, 1], f)).toBeCloseTo(0.2);
});

test("com os pesos treinados, um cenário Telnet cai em Risco", () => {
  const telnet = { taxa_pacotes_suspeitos: 0.9, uso_porta_insegura: 1, volume_anomalo: 0.8, dispositivo_desconhecido: 0, frequencia_conexoes: 0.8 };
  expect(classificar(calcularScore(psoMock.pesos, telnet))).toBe("risco");
});

test("tempoRelativo", () => {
  const agora = Date.now();
  expect(tempoRelativo(new Date(agora - 5 * 60_000).toISOString(), agora)).toBe("há 5 min");
});
