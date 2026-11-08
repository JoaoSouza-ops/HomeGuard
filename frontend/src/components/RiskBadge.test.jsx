import { render, screen } from "@testing-library/react";
import RiskBadge from "./RiskBadge.jsx";

test.each([
  ["normal", "Normal"],
  ["atencao", "Atenção"],
  ["risco", "Risco"],
])("mostra o texto certo para %s", (nivel, texto) => {
  render(<RiskBadge nivel={nivel} />);
  expect(screen.getByText(texto)).toBeInTheDocument();
});
