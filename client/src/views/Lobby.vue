<template>
  <div class="lobby">
    <h1>🏓 Pong Multiplayer - Lobby</h1>

    <!-- Crear sala -->
    <div class="create-room">
      <input
        v-model="roomName"
        @keyup.enter="createRoom"
        placeholder="Nombre de la sala"
      />
      <button @click="createRoom">Crear sala</button>
    </div>

    <!-- Mensaje conexión -->
    <p v-if="status" class="status">{{ status }}</p>

    <!-- Lista de salas -->
    <div class="rooms">
      <h2>Salas públicas</h2>

      <div v-if="rooms.length === 0" class="empty">
        No hay salas creadas todavía
      </div>

      <div
        v-for="room in rooms"
        :key="room.name"
        class="room"
      >
        <div>
          <strong>{{ room.name }}</strong>
          <small>({{ room.players }} / 2 jugadores)</small>
        </div>

        <button
          :disabled="room.players >= 2"
          @click="joinRoom(room.name)"
        >
          Unirse
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const rooms = ref([])
const roomName = ref("")
const status = ref("")

let ws = null

onMounted(() => {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws"
  ws = new WebSocket(`${protocol}://localhost:8000/ws/lobby`)

  ws.onopen = () => {
    status.value = "✅ Conectado al lobby"
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === "lobby_update") {
      rooms.value = data.rooms
    }
  }

  ws.onclose = () => {
    status.value = "❌ Desconectado del lobby"
  }

  ws.onerror = () => {
    status.value = "⚠️ Error de conexión"
  }
})

onBeforeUnmount(() => {
  if (ws) ws.close()
})

// -----------------
// Crear sala
// -----------------
function createRoom() {
  if (!roomName.value.trim()) return

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: "create_room",
        name: roomName.value.trim()
      })
    )
  }

  roomName.value = ""
}

// -----------------
// Unirse a sala
// -----------------
function joinRoom(name) {
  router.push(`/game/${name}`)
}
</script>

<style scoped>
.lobby {
  min-height: 100vh;
  padding: 40px;
  background: linear-gradient(120deg, #020617, #0f172a, #020617);
  color: white;
  font-family: Arial, Helvetica, sans-serif;
  text-align: center;
}

h1 {
  margin-bottom: 20px;
  font-size: 36px;
}

.create-room {
  margin-bottom: 30px;
}

input {
  padding: 10px;
  width: 220px;
  border-radius: 6px;
  border: none;
  outline: none;
  margin-right: 8px;
  font-size: 14px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  background: #22c55e;
  color: black;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s ease;
}

button:hover {
  background: #16a34a;
  transform: scale(1.05);
}

button:disabled {
  background: #64748b;
  cursor: not-allowed;
  transform: none;
}

.status {
  margin-bottom: 20px;
  font-size: 14px;
  opacity: 0.8;
}

.rooms {
  max-width: 400px;
  margin: 0 auto;
}

.room {
  background: #1e293b;
  border-radius: 8px;
  padding: 12px 18px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty {
  opacity: 0.6;
  margin-top: 20px;
}
</style>
