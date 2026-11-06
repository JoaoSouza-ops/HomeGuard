FROM node:20-alpine AS build
WORKDIR /app

# O Vite grava estas variáveis NO BUILD (não em runtime) — por isso são ARG.
ARG VITE_API_URL=/api
ARG VITE_WS_URL=ws://localhost:8080/api
ENV VITE_API_URL=$VITE_API_URL \
    VITE_WS_URL=$VITE_WS_URL

COPY . .
# Enquanto o frontend não existe, gera uma página provisória para o sistema já subir inteiro.
RUN if [ -f package.json ]; then \
      npm ci && npm run build; \
    else \
      mkdir -p dist && echo '<h1>HomeGuard</h1><p>Frontend em construcao. A API esta em /api/docs</p>' > dist/index.html; \
    fi

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
