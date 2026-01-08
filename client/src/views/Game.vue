<template>
  <PongGame :room="$route.params.room"/>
</template>

<script setup>
import PongGame from '../components/PongGame.vue'
</script>
