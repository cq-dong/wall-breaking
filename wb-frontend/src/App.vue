<script setup>
import { ref, computed } from 'vue'
import Home from './Home.vue'
import Chat from './Chat.vue'


const routes = {
  '/': Home,
  '/chat': Chat
}
const currentPath = ref(window.location.hash)
window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})
const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || Home
})

</script>


<template>
  <component :is="currentView" />
</template>


<style></style>