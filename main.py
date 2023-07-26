from fastapi import FastAPI, WebSocket


app = FastAPI()


@app.websocket("/ws")
async def health_check(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_json({"msg":data})