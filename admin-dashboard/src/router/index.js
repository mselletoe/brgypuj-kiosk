/*
 * =================================================================================
 * File: router/index.js
 * Description: 
 * Main routing configuration for the Vue.js application.
 * - Defines all accessible URL paths (routes).
 * - Manages access control (Navigation Guards) to protect admin pages.
 * - Redirects unauthenticated users to the login page.
 * =================================================================================
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/authStore'

import AdminLayout from '@/layouts/AdminLayout.vue'
import Overview from '@/views/Overview.vue'
import DocumentRequests from '@/views/requests/document-requests/DocumentRequest.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import KioskAnnouncements from '@/views/announcements/KioskAnnouncements.vue'
import SMSAnnouncements from '@/views/announcements/SMSAnnouncements.vue'
import Residents from '@/views/Residents.vue'
import Auth from '@/views/Auth.vue'
import CreateAccount from '@/views/CreateAccount.vue'
import EquipmentInventory from '@/views/equipment-inventory/EquipmentInventory.vue'
import SystemSettings from '@/views/settings/SystemSettings.vue'
import EquipmentRequests from '@/views/requests/equipment-requests/EquipmentRequest.vue' 
import FeedbackAndReports from '@/views/feedback-and-reports/FeedbackAndReports.vue'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: Auth,
    meta: { requiresGuest: true }
  },
  {
    path: '/create-account',
    name: 'CreateAccount',
    component: CreateAccount,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/overview',
    meta: { requiresAuth: true },
    children: [
      { path: 'overview', component: Overview },
      { 
        path: 'document-requests/:status?', 
        name: 'DocumentRequests', 
        component: DocumentRequests,
        props: true 
      },
      { 
        path: 'equipment-requests/:status?', 
        name: 'EquipmentRequests', 
        component: EquipmentRequests,
        props: true 
      },
      { 
        path: 'feedback-and-reports/:status?', 
        name: 'FeedbackReports', 
        component: FeedbackAndReports,
        props: true 
      },
      { path: 'document-services', component: DocumentServices },
      { path: 'kiosk-announcements', component: KioskAnnouncements },
      { path: 'sms-announcements', component: SMSAnnouncements },
      { path: 'residents', component: Residents },  
      { path: 'equipment-inventory', component: EquipmentInventory },
      { path: 'system-settings', component: SystemSettings },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  
  if (!auth.token) {
    auth.loadToken()
  }

  const isAuthenticated = !!auth.token
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  if (requiresAuth && !isAuthenticated) {
    next('/auth')
  }
  else if (requiresGuest && isAuthenticated) {
    next('/overview')
  }
  else {
    next()
  }
})

export default router