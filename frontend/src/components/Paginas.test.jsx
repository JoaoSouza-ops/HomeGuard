import { render, screen } from "@testing-library/react";
import MitigacoesPage from "./MitigacoesPage.jsx";

test("sem registro mostra o estado vazio", () => {
  render(<MitigacoesPage registro={[]} />);
  expect(screen.getByText(/Nenhuma mitigação ainda/)).toBeInTheDocument();
});

test("mostra antes e depois e a marca de simulado", () => {
  const registro = [{ id: "1", nome: "Câmera", acao: "bloquear_porta", justificativa: "Telnet", em: new Date().toISOString(), score_antes: 0.87, score_depois: 0.15, simulado: true }];
  render(<MitigacoesPage registro={registro} />);
  expect(screen.getByText("Bloquear porta")).toBeInTheDocument();
  expect(screen.getByText("simulado")).toBeInTheDocument();
  expect(screen.getByText("0.87")).toBeInTheDocument();
});
