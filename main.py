from broadcaster import Broadcast

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.concurrency import run_until_first_complete


broadcast = Broadcast("redis://redis:6379")
templates = Jinja2Templates(directory="templates")
app = FastAPI(on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect])


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    context = {"request":request}
    return templates.TemplateResponse("algoholic/home.html",context)


@app.get("/{room_id}/", response_class=HTMLResponse)
async def get(request: Request, room_id:str):
    context = {"room_id":room_id,"request":request}
    return templates.TemplateResponse("codeshare.html",context)


async def chatroom_ws_receiver(websocket: WebSocket, room_id: str):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=f"chatroom_{room_id}", message=message)


async def chatroom_ws_sender(websocket: WebSocket, room_id: str):
    async with broadcast.subscribe(channel=f"chatroom_{room_id}") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


@app.websocket("/ws/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket, "room_id":room_id}),
        (chatroom_ws_sender, {"websocket": websocket, "room_id":room_id}),
    )




