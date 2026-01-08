import { createRouter, createWebHistory } from "vue-router"
import Lobby from "@/views/Lobby.vue"
import PongGame from "@/components/PongGame.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/lobby" },
    { path: "/lobby", component: Lobby },
    { path: "/game/:room", component: PongGame }
  ]
})

export default router
