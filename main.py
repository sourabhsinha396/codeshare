from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
app = FastAPI()


@app.get("/{room_id}", response_class=HTMLResponse)
async def chatroom(request: Request, room_id: str):
    context = {"request": request, "room_id": room_id}
    return templates.TemplateResponse("chatroom.html", context)
