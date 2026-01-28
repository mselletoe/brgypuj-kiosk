/**
 * @file router/index.js
 * @description Centralized routing configuration with Navigation Guards.
 * Protects internal kiosk services from unauthorized access and manages 
 * the transition between Idle, Authentication, and Dashboard states.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserLayout from '@/layouts/UserLayout.vue'

// Views
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
import ComponentShowcase from '../components/ComponentShowcase.vue'
import InAnnouncements from '../views/announcements/Announcement.vue'

const routes = [
  // Root Redirect: Kiosk starts at the Idle/Welcome screen
  { path: '/', redirect: '/idle' },
  
  /**
   * PUBLIC ROUTES
   * Accessible without any authentication.
   */
  { path: '/display', name: 'Display', component: Display },
  { path: '/idle', name: 'Idle', component: Idle },
  { path: '/announcements', name: 'Announcements', component: Announcements },
  { path: '/login', name: 'LoginSelection', component: Login },
  { path: '/login-rfid', name: 'ScanRFID', component: ScanRFID },
  { path: '/auth-pin', name: 'VerifyPIN', component: AuthPIN },
  { path: '/inannouncements', name: 'InAnnouncements', component: InAnnouncements },
  /**
   * PROTECTED ROUTES (UserLayout)
   * Requires either Guest or RFID authentication.
   */
  {
    path: '/',
    component: UserLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'home', name: 'Home', component: KioskHome },
      { 
        path: 'document-services', 
        name: 'DocumentServices',
        component: DocumentServices,
        children: [
          { path: ':docType', component: DocumentFormWrapper }
        ]
      },
      { path: 'equipment-borrowing', name: 'EquipmentBorrowing', component: EquipmentBorrowing },
      { path: 'help-and-support', name: 'Support', component: HelpAndSupport },
      { path: 'feedback', name: 'Feedback', component: Feedback },
      { path: 'rating', name: 'Rating', component: Rating },
      { path: 'comments', name: 'Comments', component: Comments },
      { path: 'register', name: 'Register', component: Register },
      { path: 'component-showcase', name: 'DevShowcase', component: ComponentShowcase },
    ]
  },
  
  // Catch-all: Redirect unknown paths back to the safety of the Idle screen
  { path: '/:pathMatch(.*)*', redirect: '/idle' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * GLOBAL NAVIGATION GUARD
 * Intercepts every route change to check authentication status.
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Ensure the store is rehydrated from LocalStorage before checking
  if (!authStore.isAuthenticated) {
    authStore.restore()
  }

  /**
   * Scenario: Accessing a protected page without a session.
   * If the route has 'requiresAuth' and the user isn't logged in, send them to login.
   */
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } 
  /**
   * Scenario: Trying to access login pages while already authenticated.
   * If they are already logged in and try to go to /login, send them to /home.
   */
  else if ((to.path === '/login' || to.path === '/login-rfid') && authStore.isAuthenticated) {
    next('/home')
  }
  else {
    next() // Proceed as normal
  }
})

export default router