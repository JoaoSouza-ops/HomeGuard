import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DeviceCard from "./DeviceCard.jsx";

const base = {
  id: "AA:01",
  nome: "ESP32 - Teste",
  ip: "192.168.4.12",
  ultima_atividade: new Date().toISOString(),
  nivel_risco: "risco",
  score_risco: 0.87,
};

test("mostra nome, ip e score", () => {
  render(<DeviceCard dispositivo={base} onMitigar={() => {}} />);
  expect(screen.getByText("ESP32 - Teste")).toBeInTheDocument();
  expect(screen.getByText("192.168.4.12")).toBeInTheDocument();
  expect(screen.getByText("0.87")).toBeInTheDocument();
});

test("botão Mitigar chama o callback com o dispositivo", async () => {
  const onMitigar = vi.fn();
  render(<DeviceCard dispositivo={base} onMitigar={onMitigar} />);
  await userEvent.click(screen.getByRole("button", { name: "Mitigar" }));
  expect(onMitigar).toHaveBeenCalledWith(base);
});

test("dispositivo normal não oferece mitigação", () => {
  render(<DeviceCard dispositivo={{ ...base, nivel_risco: "normal", score_risco: 0.1 }} onMitigar={() => {}} />);
  expect(screen.queryByRole("button", { name: "Mitigar" })).not.toBeInTheDocument();
});

test("depois de mitigado mostra o aviso no lugar do botão", () => {
  render(<DeviceCard dispositivo={base} mitigacao={{ acao: "bloquear_porta" }} onMitigar={() => {}} />);
  expect(screen.getByText(/bloquear porta/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Mitigar" })).not.toBeInTheDocument();
});
