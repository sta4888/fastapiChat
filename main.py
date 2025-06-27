from fastapi import FastAPI, WebSocket
from typing import List

from starlette.websockets import WebSocketDisconnect

from utils import ConnectionManager

app = FastAPI()
clients: List[WebSocket] = []
manager = ConnectionManager()

from fastapi.responses import HTMLResponse

@app.get("/docs/ws", response_class=HTMLResponse)
def websocket_info():
    return """
    <h2>WebSocket API</h2>
    <p>Connect to <code>ws://localhost:8000/ws/{group_id}</code></p>
    <p>Send: <code>text</code></p>
    <p>Receive: <code>broadcasted messages from group</code></p>
    """


@app.websocket("/ws/alerts")
async def alerts(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # просто для поддержания соединения
    except:
        clients.remove(websocket)

@app.post("/notify")
async def notify_all(message: str):
    for ws in clients:
        await ws.send_text(f"[SERVER] {message}")
    return {"status": "sent"}


@app.websocket("/ws/{group_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: int):
    await manager.connect(group_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 1. Сохрани в БД (например, user_id, content, timestamp)
            # 2. Рассылай по WebSocket
            await manager.send_to_group(group_id, data)
    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)
