from fastapi import WebSocket

from app.api.schemas import Alerta, Dispositivo


class ConnectionManager:
    """Guarda os clientes WebSocket conectados e envia mensagens a todos (Observer / Pub-Sub)."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        # Percorre uma cópia da lista: um cliente que caiu é removido no meio do laço
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


# Instância única, compartilhada pela rota /ws/alerts e por quem publicar eventos
manager = ConnectionManager()


async def publicar_dispositivo(dispositivo) -> None:
    """Envia o dispositivo (objeto do banco ou schema) a todos os clientes, no formato do contrato."""
    mensagem = Dispositivo.model_validate(dispositivo).model_dump(mode="json")
    await manager.broadcast(mensagem)


async def publicar_alerta(alerta) -> None:
    """Envia o alerta (objeto do banco ou schema) a todos os clientes, no formato do contrato."""
    mensagem = Alerta.model_validate(alerta).model_dump(mode="json")
    await manager.broadcast(mensagem)
