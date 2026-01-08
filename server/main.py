from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Clase Room
# -------------------
class Room:
    def __init__(self, name):
        self.name = name
        self.clients: List[WebSocket] = []
        self.left = 200
        self.right = 200
        self.score = {"left": 0, "right": 0}
        self.started = False

        self.task = None

        self.initial_speed = 4
        self.speed_increment = 0.01

        self.ball = {
            "x": 400,
            "y": 250,
            "vx": self.initial_speed,
            "vy": self.initial_speed
        }

    # -------------------
    # Envío a todos
    # -------------------
    async def broadcast(self, message):
        for ws in self.clients:
            try:
                await ws.send_text(json.dumps(message))
            except:
                pass

    # -------------------
    # Resetear partida
    # -------------------
    def reset_state(self):
        self.ball = {
            "x": 400,
            "y": 250,
            "vx": self.initial_speed,
            "vy": self.initial_speed
        }

        self.left = 200
        self.right = 200
        self.score = {"left": 0, "right": 0}

        self.started = len(self.clients) == 2

    # -------------------
    # Iniciar Loop
    # -------------------
    async def start_loop(self):
        if self.task is None:
            self.task = asyncio.create_task(self.wait_and_start_loop())

    async def wait_and_start_loop(self):
        # Esperar a que haya 2 jugadores
        while len(self.clients) < 2:
            await asyncio.sleep(0.1)

        self.started = True
        await self.broadcast({"type": "start"})

        await self.game_loop()

    # -------------------
    # Game Loop
    # -------------------
    async def game_loop(self):
        while self.started:
            # Movimiento
            self.ball["x"] += self.ball["vx"]
            self.ball["y"] += self.ball["vy"]

            # Aumentar velocidad progresiva
            self.ball["vx"] += self.speed_increment if self.ball["vx"] > 0 else -self.speed_increment
            self.ball["vy"] += self.speed_increment if self.ball["vy"] > 0 else -self.speed_increment

            # Rebotes superior / inferior
            if self.ball["y"] <= 0 or self.ball["y"] >= 500:
                self.ball["vy"] *= -1

            # Rebote en paletas
            if (self.ball["x"] <= 25 and self.left <= self.ball["y"] <= self.left + 100):
                self.ball["vx"] *= -1

            if (self.ball["x"] >= 775 and self.right <= self.ball["y"] <= self.right + 100):
                self.ball["vx"] *= -1

            # Gol derecha
            if self.ball["x"] < 0:
                self.score["right"] += 1
                self.ball = {
                    "x": 400,
                    "y": 250,
                    "vx": self.initial_speed,
                    "vy": self.initial_speed
                }

            # Gol izquierda
            if self.ball["x"] > 800:
                self.score["left"] += 1
                self.ball = {
                    "x": 400,
                    "y": 250,
                    "vx": -self.initial_speed,
                    "vy": self.initial_speed
                }

            # Estado a clientes
            await self.broadcast({
                "type": "update",
                "ball": self.ball,
                "left": self.left,
                "right": self.right,
                "score": self.score
            })

            await broadcast_lobby()

            await asyncio.sleep(1 / 60)


# -------------------
# Variables globales
# -------------------
rooms = {}
lobby_clients: List[WebSocket] = []


# -------------------
# Lobby
# -------------------
async def broadcast_lobby():
    rooms_list = [
        {"name": name, "players": len(room.clients)}
        for name, room in rooms.items()
    ]

    for ws in lobby_clients:
        try:
            await ws.send_text(json.dumps({
                "type": "lobby_update",
                "rooms": rooms_list
            }))
        except:
            pass


@app.websocket("/ws/lobby")
async def websocket_lobby(websocket: WebSocket):
    await websocket.accept()
    lobby_clients.append(websocket)

    await broadcast_lobby()

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            # Crear sala desde WebSocket
            if data.get("type") == "create_room":
                name = data.get("name")

                if name and name not in rooms:
                    rooms[name] = Room(name)
                    await broadcast_lobby()

    except:
        pass

    finally:
        if websocket in lobby_clients:
            lobby_clients.remove(websocket)


# -------------------
# WebSocket para salas
# -------------------
@app.websocket("/ws/{room_name}")
async def websocket_room(websocket: WebSocket, room_name: str):
    await websocket.accept()

    if room_name not in rooms:
        rooms[room_name] = Room(room_name)
        await broadcast_lobby()

    room = rooms[room_name]
    room.clients.append(websocket)

    await room.start_loop()
    await broadcast_lobby()

    # Asignar lado
    side = "left" if len(room.clients) == 1 else "right"
    await websocket.send_text(json.dumps({
        "type": "side",
        "side": side
    }))

    if len(room.clients) == 1:
        await websocket.send_text(json.dumps({"type": "wait"}))

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            if data.get("type") == "move":
                if data["side"] == "left":
                    room.left = data["y"]
                else:
                    room.right = data["y"]

            if data.get("type") == "reset":
                room.reset_state()

                if room.started and room.task is None:
                    await room.start_loop()

                await room.broadcast({
                    "type": "update",
                    "reset": True,
                    "ball": room.ball,
                    "left": room.left,
                    "right": room.right,
                    "score": room.score
                })

    except WebSocketDisconnect:
        if websocket in room.clients:
            room.clients.remove(websocket)

        if not room.clients:
            if room_name in rooms:
                del rooms[room_name]

        await broadcast_lobby()
