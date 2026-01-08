Pong Multiplayer (FastAPI + Vue + WebSockets)

Juego Pong multijugador en tiempo real usando FastAPI + WebSockets para el backend y Vue 3 + Vite para el frontend.
Incluye lobby con salas públicas, matchmaking manual y partidas 1vs1.

------- Características -------

Pong clásico 1 vs 1

Multijugador en tiempo real con WebSockets

Lobby con salas públicas

Creación de salas en tiempo real (sin HTTP)

La partida empieza cuando hay 2 jugadores

La pelota acelera con el tiempo

Reinicio de partida funcional

Pausa y control correcto del estado del juego

Interfaz visual mejorada

------- Tecnologías usadas -------

BACKEND

- Python 3.10+

- FastAPI

- Uvicorn

- WebSockets (estado en memoria)

FRONTEND

- Vue 3

- Vite

- Vue Router

- WebSocket API

------- Estructura del proyecto -------

pong/
├── server/
│   ├── main.py
│   └── requirements.txt
│
└── client/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/
        │   └── index.js
        └── views/
            ├── Lobby.vue
            └── PongGame.vue

------- Instalación -------

BACKEND

cd server
python -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

pip install -r requirements.txt

FRONTEND

cd client
npm install

------- Iniciar backend -------

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000


Backend disponible en:
http://localhost:8000

WebSocket:
ws://localhost:8000/ws

------- Iniciar frontend -------

cd client
npm run dev


Frontend disponible en:
http://localhost:5173

------- Cómo jugar -------

Abre el frontend en el navegador.

Entra al Lobby.

Crea una sala o únete a una existente.

La partida comienza automáticamente cuando entran 2 jugadores.

Controles:

W / S → Paleta izquierda

↑ / ↓ → Paleta derecha

Gana el jugador que alcance el puntaje máximo.

Usa Reiniciar para volver a empezar la partida.

------- WebSockets -------

Lobby y salas se gestionan por WebSocket.

No se usan endpoints HTTP para crear salas.

El estado del juego se mantiene en memoria.

Cada sala tiene:

Jugadores conectados

Estado del juego

Pelota, paletas y puntuación

------- Requisitos -------

Node.js 18+

Python 3.10+

Navegador moderno (Chrome, Firefox)
