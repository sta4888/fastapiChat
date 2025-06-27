from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, group_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(group_id, []).append(websocket)

    def disconnect(self, group_id: int, websocket: WebSocket):
        self.active_connections[group_id].remove(websocket)

    async def send_to_group(self, group_id: int, message: str):
        for connection in self.active_connections.get(group_id, []):
            await connection.send_text(message)
