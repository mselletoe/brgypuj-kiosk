import { createRouter, createWebHistory } from 'vue-router'
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

const routes = [
  // Start with idle screen
  { path: '/', redirect: '/idle' },
  
  // Public routes (no authentication needed)
  { path: '/display', component: Display },
  { path: '/idle', component: Idle },
  { path: '/announcements', component: Announcements },
  { path: '/login', component: Login },
  { path: '/login-rfid', component: ScanRFID },
  { path: '/auth-pin', component: AuthPIN },
  
  // Layout routes (all pages inside the user layout)
  {
    path: '/',
    component: UserLayout,
    children: [
      { path: 'home', component: KioskHome },
      { 
        path: 'document-services', 
        component: DocumentServices,
        children: [
          { path: ':docType', component: DocumentFormWrapper }
        ]
      },
      { path: 'equipment-borrowing', component: EquipmentBorrowing },
      { path: 'help-and-support', component: HelpAndSupport },
      { path: 'feedback', component: Feedback },
      { path: 'rating', component: Rating },
      { path: 'comments', component: Comments },
      { path: 'register', component: Register },
      { path: 'component-showcase', component: ComponentShowcase },
    ]
  },
  
  // Catch all - redirect to idle
  { path: '/:pathMatch(.*)*', redirect: '/idle' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router