import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '@/stores/auth'
import UserLayout from '@/layouts/UserLayout.vue'

// views
import Display from '@/views/idle/Display.vue'
import Idle from '@/views/idle/Idle.vue'
import Announcements from '@/views/idle/Announcements.vue'
import Login from '@/views/auth/Login.vue'
import ScanRFID from '@/views/auth/ScanRFID.vue'
import LoginPIN from '@/views/auth/LoginPIN.vue'
import Register from '@/views/auth/Register.vue'
import KioskHome from '@/views/home/KioskHome.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import DocumentFormWrapper from '@/views/document-services/DocumentFormWrapper.vue'
import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'
import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'
import Feedback from '@/views/feedback/Feedback.vue'
import Rating from '@/views/feedback/Rating.vue'
import Comments from '@/views/feedback/Comments.vue'
import Appointments from '@/views/appointments/Appointments.vue'

const routes = [
  // Default route
  { path: '/', redirect: '/idle' },

  // Non-layout routes
  { path: '/display', component: Display},
  { path: '/idle', component: Idle },
  { path: '/announcements', component: Announcements },
  { path: '/login', component: Login },
  { path: '/login-rfid', component: ScanRFID },
  { path: '/login-pin', component: LoginPIN },

  // Authenticated & Inside-layout routes 
  {
    path: '/',
    component: UserLayout,
    children: [
      { path: '/home', component: KioskHome, meta: { requiresAuth: true } },
      { path: 'register', component: Register, meta: { requiresAuth: true }},
      {
        path: '/document-services', component: DocumentServices,
        children: [
          { path: ':docType', component: DocumentFormWrapper, },
        ],
      },
      { path: 'equipment-borrowing', component: EquipmentBorrowing },
      { path: 'help-and-support', component: HelpAndSupport },
      { path: 'feedback', component: Feedback },
      { path: 'rating', component: Rating },
      { path: 'comments', component: Comments },
      { path: 'appointments', component: Appointments },
    ],
  },

  // Fallback for unknown routes
  { path: '/:pathMatch(.*)*', redirect: '/idle' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


// Global guard
router.beforeEach((to, from, next) => {
  const stored = localStorage.getItem('auth_user')
  if (stored) {
    const parsed = JSON.parse(stored)
    auth.user = parsed.user
    auth.isGuest = parsed.isGuest
  }

  const loggedIn = !!auth.user
  const isGuest = auth.isGuest

  // Guest users go directly to /home
  if (isGuest && (to.path === '/login' || to.path === '/login-rfid' || to.path === '/login-pin')) {
    return next('/home')
  }

  // If logged in, prevent re-entering login or RFID
  if (loggedIn && (to.path === '/login' || to.path === '/login-rfid')) {
    return next('/home')
  }

  // Protect routes with requiresAuth
  if (!loggedIn && !isGuest && to.meta.requiresAuth) {
    return next('/login-rfid')
  }

  next()
})

export default router