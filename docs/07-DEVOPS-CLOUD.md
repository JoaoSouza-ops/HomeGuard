# 07 — DevOps, CI/CD e Deploy na AWS

**Responsável sugerido:** Arquiteto DevOps / Tech Lead

> Depende das respostas aos itens 4, 5 e 8 de `00-PREMISSAS.md` (conta AWS, monorepo, banco de dados escolhido). Confirmem antes de seguir.

## 1. Containerização

### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `frontend/Dockerfile`
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### `infra/docker-compose.yml`
```yaml
version: "3.9"
services:
  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto/config:/mosquitto/config

  backend:
    build: ../backend
    ports:
      - "8000:8000"
    environment:
      - MQTT_BROKER_HOST=mosquitto
      - DATABASE_URL=${DATABASE_URL}   # confirmar formato conforme item 8 de 00-PREMISSAS.md
    depends_on:
      - mosquitto

  frontend:
    build: ../frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

Subir tudo localmente:
```bash
cd infra
docker compose up --build
```

## 2. CI/CD com GitHub Actions

Objetivo: a cada Pull Request, rodar lint e testes automaticamente. Ninguém faz merge com o pipeline vermelho.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt flake8
      - run: flake8 app/ --max-line-length=120
      - run: pytest tests/ -v

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --run
```

## 3. Deploy na AWS (EC2 — abordagem simples para equipe júnior)

> Não usaremos ECS/EKS por enquanto — complexidade desnecessária para o escopo do projeto. Uma instância EC2 rodando Docker Compose é suficiente e é o que a maioria dos projetos acadêmicos usa para "deploy em nuvem real".

### 3.1 Criar a instância
1. Console AWS → EC2 → "Launch Instance".
2. AMI: Ubuntu Server 22.04 LTS.
3. Tipo de instância: `t2.micro` ou `t3.micro` (elegível para free tier — **confirmar item 4 de `00-PREMISSAS.md`**).
4. Criar/usar um par de chaves (`.pem`) — guardem com segurança, **nunca commitem no Git**.
5. Security Group: liberar portas `22` (SSH — restrito ao IP da equipe, se possível), `8000` (API), `3000` ou `80` (frontend).

### 3.2 Configurar a instância
```bash
ssh -i chave.pem ubuntu@<IP_PUBLICO_DA_INSTANCIA>

sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# desconectar e reconectar o SSH para aplicar o grupo docker

git clone <url-do-repositorio>
cd homeguard/infra
docker compose up --build -d
```

### 3.3 Deploy automatizado (opcional, mas recomendado)
Adicionem um job no GitHub Actions que roda **após** o merge na `main` (não em todo PR) e faz o deploy via SSH:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.AWS_HOST }}
          username: ubuntu
          key: ${{ secrets.AWS_SSH_KEY }}
          script: |
            cd homeguard
            git pull origin main
            cd infra
            docker compose up --build -d
```

> Guardem `AWS_HOST` e `AWS_SSH_KEY` em **GitHub Secrets** (Settings → Secrets and variables → Actions), nunca no código.

## 4. Variáveis de ambiente e segredos

Criem um `.env.example` na raiz do monorepo listando todas as variáveis necessárias **sem valores reais**, e cada integrante cria seu próprio `.env` local (que fica no `.gitignore`).

```
# .env.example
DATABASE_URL=
MQTT_BROKER_HOST=mosquitto
AWS_HOST=
```

## 5. Checklist de "definition of done" de infraestrutura

- [ ] `docker compose up` sobe o sistema completo com um único comando, do zero.
- [ ] O pipeline de CI roda lint + testes em todo PR e bloqueia merge se falhar.
- [ ] Existe um endereço público (IP ou domínio) da AWS onde o professor/banca pode acessar o dashboard sem precisar de VPN ou configuração extra.
- [ ] Nenhuma credencial (chave AWS, senha de banco, chave SSH) está commitada no repositório — rodem `git log -p | grep -i "password\|secret\|key"` antes da entrega final como checagem.
