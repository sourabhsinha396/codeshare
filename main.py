from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
app = FastAPI()


@app.get("/{room_id}", response_class=HTMLResponse)
async def chatroom(request: Request, room_id: str):
    context = {"request": request, "room_id": room_id}
    return templates.TemplateResponse("chatroom.html", context)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[str,WebSocket]= {}
        print("Creating a list to hold active connections",self.active_connections)

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if not self.active_connections.get(room_id):
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        print("New Active connections are ",self.active_connections)

    async def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)
        print("After disconnect active connections are: ",self.active_connections)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        print("Sent a personal msg to , ",websocket)

    async def broadcast(self, message: str, room_id: str, websocket: WebSocket):
        for connection in self.active_connections[room_id]:
            if connection != websocket:
                await connection.send_text(message)
                print("In broadcast: sent msg to ",connection)

manager = ConnectionManager()


@app.websocket("/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}",websocket)
            await manager.broadcast(f"A client says: {data}", room_id, websocket)
    except Exception as e:
        print("Got an exception ",e)
        await manager.disconnect(room_id, websocket)


