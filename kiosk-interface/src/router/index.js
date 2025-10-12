import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
import KioskHome from '@/views/KioskHome.vue'
import Login from '@/views/Login.vue'
import EquipmentBorrowing from '@/views/EquipmentBorrowing.vue'
import HelpAndSupport from '@/views/HelpAndSupport.vue'
import Feedback from '@/views/Feedback.vue'
import Appointments from '@/views/Appointments.vue'
import Idle from '@/views/Idle.vue'

const routes = [
  { 
    path: '/', 
    component: UserLayout,
    redirect: '/kiosk-home',
    children: [
      { path: '/kiosk-home', component: KioskHome },
      { path: '/login', component: Login },
      { path: '/equipment-borrowing', component: EquipmentBorrowing },
      { path: '/help-and-support', component: HelpAndSupport },
      { path: '/feedback', component: Feedback },
      { path: '/appointments', component: Appointments },
    ]
  },
  {
    path: '/login',
    component: Login
  },

  {
    path: '/idle',
    component: Idle
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router