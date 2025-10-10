import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
import KioskHome from '@/views/home/KioskHome.vue'
import Login from '@/views/login/Login.vue'
import Announcements from '@/views/announcements/Announcements.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'
import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'
import Feedback from '@/views/feedback/Feedback.vue'
import Appointments from '@/views/appointments/Appointments.vue'

const routes = [
  { 
    path: '/', 
    component: UserLayout,
    redirect: '/kiosk-home',
    children: [
      { path: '/kiosk-home', component: KioskHome },
      { path: '/login', component: Login },
      { path: '/announcements', component: Announcements },
      { path: '/document-services', component: DocumentServices },
      { path: '/equipment-borrowing', component: EquipmentBorrowing },
      { path: '/help-and-support', component: HelpAndSupport },
      { path: '/feedback', component: Feedback },
      { path: '/appointments', component: Appointments }
    ]
  },
  {
    path: '/login',
    component: Login
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router