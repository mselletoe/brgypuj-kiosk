import { createRouter, createWebHistory } from 'vue-router'
import KioskHome from '@/views/KioskHome.vue'

const routes = [
  { path: '/', component: KioskHome }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router  // <-- Make sure you export default
