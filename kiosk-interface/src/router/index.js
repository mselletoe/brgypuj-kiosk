import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'

// Screens
import Idle from '@/views/idle/Idle.vue'
import Announcements from '@/views/idle/Announcements.vue'
import Login from '@/views/login/Login.vue'
import LoginRFID from '@/views/login/LoginRFID.vue'
import KioskHome from '@/views/home/KioskHome.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'
import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'
import Feedback from '@/views/feedback/Feedback.vue'
import Appointments from '@/views/appointments/Appointments.vue'

const routes = [
  // Default Route
  {
    path: '/',
    redirect: '/idle',
  },

  // Non-layout Routes 
  {
    path: '/idle',
    name: 'Idle',
    component: Idle,
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: Announcements
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/login-rfid',
    name: 'LoginRFID',
    component: LoginRFID,
  },

  // Authenticated Routes
  {
    path: '/app',
    component: UserLayout,
    children: [
      { path: '', redirect: '/app/home' },
      { path: 'home', component: KioskHome },
      { path: 'document-services', component: DocumentServices },
      { path: 'equipment-borrowing', component: EquipmentBorrowing },
      { path: 'help-and-support', component: HelpAndSupport },
      { path: 'feedback', component: Feedback },
      { path: 'appointments', component: Appointments },
    ],
  },

  // Fallback
  {
    path: '/:pathMatch(.*)*',
    redirect: '/idle',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router