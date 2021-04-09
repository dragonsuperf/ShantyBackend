import os
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


async def youtube_dl(url: str):
    return os.system(f"youtube-dl -o ./static/%(id)s.%(ext)s https://youtube.com/watch?v={url}")


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/video")
async def create_video(url: str):
    ret = await youtube_dl(url)
    return {"result": ret}


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.send_personal_message(f"Message text was: {data}", websocket)
        await manager.broadcast(f"Someone Said: {data}")

