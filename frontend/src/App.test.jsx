import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App.jsx";
import * as api from "./services/api.js";

vi.mock("./services/api.js");

afterEach(() => vi.resetAllMocks());

test("com a API fora, cai no modo demonstração e mostra os dispositivos mock", async () => {
  api.listarDispositivos.mockRejectedValue(new Error("offline"));
  api.listarAlertas.mockRejectedValue(new Error("offline"));
  render(<App />);
  await waitFor(() => expect(screen.getByText(/Modo demonstração/)).toBeInTheDocument());
  expect(screen.getAllByText("ESP32 - Dispositivo Vulneravel").length).toBeGreaterThan(0);
  expect(screen.getByRole("button", { name: "Re-treinar" })).toBeDisabled();
});

test("com a API no ar, usa os dados dela e mitiga via POST", async () => {
  api.listarDispositivos.mockResolvedValue([
    { id: "X1", nome: "Câmera Real", ip: "10.0.0.5", ultima_atividade: new Date().toISOString(), nivel_risco: "risco", score_risco: 0.9 },
  ]);
  api.listarAlertas.mockResolvedValue([]);
  api.obterPso.mockRejectedValue(new Error("sem pso"));
  api.mitigarDispositivo.mockResolvedValue({ status: "mitigado" });

  render(<App />);
  await waitFor(() => expect(screen.getByText("API conectada")).toBeInTheDocument());
  await userEvent.click(screen.getByRole("button", { name: "Mitigar" }));
  await userEvent.click(screen.getByRole("button", { name: "Confirmar mitigação" }));

  await waitFor(() => expect(api.mitigarDispositivo).toHaveBeenCalledWith("X1", "bloquear_porta", ""));
  expect(await screen.findByText(/Mitigação enviada/)).toBeInTheDocument();
});
