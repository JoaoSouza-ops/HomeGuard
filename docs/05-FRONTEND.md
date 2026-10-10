# 05 — Frontend (Dashboard "Casa Virtual")

**Responsável sugerido:** Desenvolvedor Frontend (Dashboard)

## 1. Setup do ambiente

> **Confirmar com a equipe:** versão do Node. Recomendação: Node 20 LTS.

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install axios
npm run dev
```

Usamos **Vite** em vez de Create React App por ser mais rápido e ser o padrão atual de mercado para SPAs React.

## 2. Estrutura de pastas sugerida

```
frontend/
├── src/
│   ├── components/
│   │   ├── DeviceCard.jsx        # card de um dispositivo (nome, IP, nível de risco)
│   │   ├── AlertFeed.jsx         # lista de alertas em tempo real
│   │   └── RiskBadge.jsx         # selo colorido (verde/amarelo/vermelho)
│   ├── pages/
│   │   └── Dashboard.jsx         # tela principal
│   ├── services/
│   │   ├── api.js                # chamadas REST (axios)
│   │   └── websocket.js          # conexão WebSocket
│   └── App.jsx
├── package.json
└── Dockerfile
```

## 3. Consumindo a API (contrato definido em `docs/03-BACKEND-API.md`)

```javascript
// src/services/api.js
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE_URL });

export async function listarDispositivos() {
  const { data } = await api.get("/devices");
  return data;
}

export async function mitigarDispositivo(deviceId, acao, justificativa) {
  const { data } = await api.post(`/devices/${deviceId}/mitigate`, {
    acao,
    justificativa,
  });
  return data;
}
```

```javascript
// src/services/websocket.js
export function conectarAlertas(onMensagem) {
  const ws = new WebSocket((import.meta.env.VITE_WS_URL || "ws://localhost:8000") + "/ws/alerts");
  ws.onmessage = (event) => onMensagem(JSON.parse(event.data));
  ws.onerror = (err) => console.error("Erro no WebSocket:", err);
  return ws;
}
```

## 4. Enquanto o backend não está pronto: trabalhem com mocks

Isso é o que torna a abordagem "API-First" valer a pena. Criem um arquivo de dados falsos que segue **exatamente** o schema `Dispositivo` de `docs/03-BACKEND-API.md`:

```javascript
// src/services/mockData.js
export const dispositivosMock = [
  {
    id: "AA:BB:CC:DD:EE:01",
    nome: "ESP32 - Sensor Temperatura",
    ip: "192.168.4.11",
    ultima_atividade: new Date().toISOString(),
    nivel_risco: "normal",
    score_risco: 0.12,
  },
  {
    id: "AA:BB:CC:DD:EE:02",
    nome: "ESP32 - Dispositivo Desconhecido",
    ip: "192.168.4.12",
    ultima_atividade: new Date().toISOString(),
    nivel_risco: "risco",
    score_risco: 0.87,
  },
];
```

Troquem `listarDispositivos()` por uma versão que devolve `dispositivosMock` durante o desenvolvimento paralelo, e substituam pela chamada real assim que o backend expuser o endpoint de verdade — **sem mudar nenhum componente visual**.

## 5. Componente exemplo: `RiskBadge`

```jsx
// src/components/RiskBadge.jsx
const CORES = {
  normal: "#2ecc71",
  atencao: "#f1c40f",
  risco: "#e74c3c",
};

const TEXTOS = {
  normal: "Normal",
  atencao: "Atenção",
  risco: "Risco",
};

export default function RiskBadge({ nivel }) {
  return (
    <span style={{ backgroundColor: CORES[nivel], padding: "4px 10px", borderRadius: "12px", color: "#fff" }}>
      {TEXTOS[nivel]}
    </span>
  );
}
```

## 6. Variáveis de ambiente

```
# frontend/.env.example
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 7. Testes

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```javascript
// src/components/RiskBadge.test.jsx
import { render, screen } from "@testing-library/react";
import RiskBadge from "./RiskBadge";

test("mostra o texto correto para nível de risco alto", () => {
  render(<RiskBadge nivel="risco" />);
  expect(screen.getByText("Risco")).toBeInTheDocument();
});
```

## 8. Checklist antes de abrir PR nesta camada

- [ ] Todo componente novo tem pelo menos um teste.
- [ ] Nenhuma URL de API está "hardcoded" — sempre via variável de ambiente.
- [ ] O componente foi testado tanto com dados mock quanto com o backend real rodando localmente.
