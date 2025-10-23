import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '@/stores/auth'
import UserLayout from '@/layouts/UserLayout.vue'

// views
import Display from '@/views/idle/Display.vue'
import Idle from '@/views/idle/Idle.vue'
import Announcements from '@/views/idle/Announcements.vue'
import Login from '@/views/auth/Login.vue'
import ScanRFID from '@/views/auth/ScanRFID.vue'
import AuthPIN from '@/views/auth/AuthPIN.vue'
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
  { path: '/', redirect: '/idle' },

  { path: '/display', component: Display},
  { path: '/idle', component: Idle },
  { path: '/announcements', component: Announcements },
  { path: '/login', component: Login },
  { path: '/login-rfid', component: ScanRFID },
  { path: '/auth-pin', component: AuthPIN },

  // Authenticated & Inside-layout routes 
  {
    path: '/',
    component: UserLayout,
    children: [
      { path: 'home', component: KioskHome, meta: { requiresAuth: true } },
      { path: 'document-services', component: DocumentServices, meta: { requiresAuth: true },
        children: [
          { path: ':docType', component: DocumentFormWrapper, meta: { requiresAuth: true } }
        ]
      },
      { path: 'equipment-borrowing', component: EquipmentBorrowing, meta: { requiresAuth: true } },
      { path: 'help-and-support', component: HelpAndSupport, meta: { requiresAuth: true } },
      { path: 'feedback', component: Feedback, meta: { requiresAuth: true } },
      { path: 'rating', component: Rating, meta: { requiresAuth: true } },
      { path: 'comments', component: Comments, meta: { requiresAuth: true } },
      { path: 'appointments', component: Appointments, meta: { requiresAuth: true } },
      { path: 'register', component: Register }
    ]
  },
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
  const loginPaths = ['/login', '/login-rfid']
  const nonAuthPaths = ['/login', '/login-rfid', '/auth-pin', '/idle', '/display', '/announcements']

  // Guests
  if (isGuest && loginPaths.includes(to.path)) return next('/home')

  // Logged-in users
  if (loggedIn && loginPaths.includes(to.path)) return next('/home')

  // Protect routes with requiresAuth
  if (!loggedIn && !isGuest && to.meta.requiresAuth) {
    if (to.path === '/register' && to.query.uid) return next()
    return next('/login-rfid')
  }

  // Prevent logged-in or guest from going back to non-auth pages
  if ((loggedIn || isGuest) && nonAuthPaths.includes(to.path)) {
    return next('/home') // always redirect to home
  }

  next()
})

export default router