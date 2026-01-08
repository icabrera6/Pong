<template>
  <div class="game-container">
    <h2>{{ status }}</h2>
    <p class="score">Score: {{ score.left }} - {{ score.right }}</p>
    <canvas ref="canvas" width="800" height="500"></canvas>

    <div v-if="winner" class="victory">
      🏆 {{ winner }} gana! 🏆
      <button @click="restart">Reiniciar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const canvas = ref(null)
const ctx = ref(null)
const socket = ref(null)
const status = ref('Esperando jugador...')
const score = ref({ left:0, right:0 })
let mySide = null
const gameState = { ball:{}, left:0, right:0 }
const ballTrail = []
const particles = []
const winner = ref(null)

// Sonidos opcionales
const bounceAudio = new Audio('/bounce.wav')
const scoreAudio = new Audio('/score.wav')
const victoryAudio = new Audio('/victory.wav')

onMounted(() => {
  ctx.value = canvas.value.getContext('2d')
  const room = route.params.room
  socket.value = new WebSocket(`ws://localhost:8000/ws/${room}`)

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type==='side') mySide=data.side
    if (data.type==='wait') status.value='Esperando segundo jugador...'
    if (data.type==='start') status.value='¡Partida iniciada!'

    if (data.type==='update'){
      if (data.reset){
        winner.value = null
        ballTrail.length=0
        particles.length=0
        score.value = data.score
        status.value = '¡Partida iniciada!'
        gameState.ball = data.ball
        gameState.left = data.left
        gameState.right = data.right
        return
      }

      // Actualización de estado
      gameState.ball = data.ball
      gameState.left = data.left
      gameState.right = data.right
      score.value = data.score

      // Efectos opcionales
      if (data.ball.x < 20 || data.ball.x > 780){
        createParticles(data.ball.x,data.ball.y,20)
        scoreAudio.play()
      }

      ballTrail.push({x:data.ball.x,y:data.ball.y})
      if (ballTrail.length>20) ballTrail.shift()

      if (!winner.value){
        if (score.value.left>=5) showWinner('Izquierda')
        if (score.value.right>=5) showWinner('Derecha')
      }
    }
  }

  window.addEventListener('mousemove', handleMouseMove)
  requestAnimationFrame(draw)
})

onBeforeUnmount(()=>{
  if (socket.value) socket.value.close()
  window.removeEventListener('mousemove', handleMouseMove)
})

// ===== MOVIMIENTO =====
function handleMouseMove(e){
  if (!socket.value || !mySide || winner.value) return
  const rect = canvas.value.getBoundingClientRect()
  const y = e.clientY - rect.top - 50
  socket.value.send(JSON.stringify({type:'move',y,side:mySide}))
}

// ===== PARTICLES =====
function createParticles(x,y,count=20){
  for(let i=0;i<count;i++){
    particles.push({
      x,y,
      vx:(Math.random()-0.5)*8,
      vy:(Math.random()-0.5)*8,
      alpha:1,
      size:4+Math.random()*4,
      color:`hsl(${Math.random()*360},100%,60%)`
    })
  }
}
function updateParticles(){
  for(let i=particles.length-1;i>=0;i--){
    const p=particles[i]
    p.x+=p.vx
    p.y+=p.vy
    p.alpha-=0.04
    if (p.alpha<=0) particles.splice(i,1)
  }
}

// ===== GANADOR =====
function showWinner(side){
  winner.value = side
  victoryAudio.play()
}

// ===== REINICIAR =====
function restart(){
  if (!socket.value) return
  socket.value.send(JSON.stringify({type:'reset'}))
}

// ===== DRAW =====
function draw(){
  if (!ctx.value) return
  updateParticles()
  const t = performance.now()/1000

  // Fondo gradiente
  const grad = ctx.value.createLinearGradient(0,0,0,500)
  grad.addColorStop(0,'#0a0a0a')
  grad.addColorStop(1,'#1a1a1a')
  ctx.value.fillStyle = grad
  ctx.value.fillRect(0,0,800,500)

  // Líneas de fondo
  ctx.value.strokeStyle='#222'
  ctx.value.lineWidth=1
  for(let i=0;i<50;i++){
    const y = ((i*50+t*120)%500)
    ctx.value.beginPath()
    ctx.value.moveTo(0,y)
    ctx.value.lineTo(800,y)
    ctx.value.stroke()
  }

  // Bola trail
  for(let i=0;i<ballTrail.length;i++){
    const alpha = i/ballTrail.length
    ctx.value.beginPath()
    ctx.value.arc(ballTrail[i].x,ballTrail[i].y,9,0,Math.PI*2)
    ctx.value.fillStyle=`rgba(255,255,0,${alpha*0.6})`
    ctx.value.fill()
  }

  // Bola
  ctx.value.beginPath()
  ctx.value.arc(gameState.ball.x,gameState.ball.y,9,0,Math.PI*2)
  ctx.value.fillStyle='#ffff00'
  ctx.value.shadowColor='#ffff00'
  ctx.value.shadowBlur=20
  ctx.value.fill()
  ctx.value.shadowBlur=0

  // Paletas
  ctx.value.fillStyle='#00ffff'
  ctx.value.fillRect(10,gameState.left,15,100)
  ctx.value.fillStyle='#ff00ff'
  ctx.value.fillRect(775,gameState.right,15,100)

  // Partículas
  particles.forEach(p=>{
    ctx.value.beginPath()
    ctx.value.arc(p.x,p.y,p.size,0,Math.PI*2)
    ctx.value.fillStyle=`hsla(${Math.random()*360},100%,60%,${p.alpha})`
    ctx.value.fill()
  })

  requestAnimationFrame(draw)
}
</script>

<style scoped>
.game-container{
  text-align:center;
  color:white;
  padding:20px;
  font-family:'Arial',sans-serif;
  position:relative;
}
canvas{
  border:3px solid white;
  border-radius:12px;
  margin-top:20px;
  background:#111;
}
.score{
  font-size:22px;
  font-weight:bold;
}
.victory{
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  background:rgba(0,0,0,0.85);
  padding:30px;
  border-radius:20px;
  text-align:center;
  font-size:32px;
  color:gold;
  animation:pulse 1s infinite alternate;
}
.victory button{
  margin-top:20px;
  padding:10px 20px;
  font-size:18px;
  border:none;
  border-radius:12px;
  cursor:pointer;
  background:linear-gradient(90deg,#00f,#0ff);
  color:white;
}
@keyframes pulse{
  0%{transform:translate(-50%,-50%) scale(1);}
  100%{transform:translate(-50%,-50%) scale(1.1);}
}
</style>
