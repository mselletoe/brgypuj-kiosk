import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'

// Screens
import Display from '@/views/idle/Display.vue'
import Idle from '@/views/idle/Idle.vue'
import Announcements from '@/views/idle/Announcements.vue'
import Login from '@/views/login/Login.vue'
import LoginRFID from '@/views/login/LoginRFID.vue'
import LoginPIN from '@/views/login/LoginPIN.vue'
import KioskHome from '@/views/home/KioskHome.vue'

// Document Services
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import DocumentFormWrapper from '@/views/document-services/DocumentFormWrapper.vue'

import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'

import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'

import Feedback from '@/views/feedback/Feedback.vue'
import FeedbackSelect from '@/views/feedback/FeedbackSelect.vue'
import Rating from '@/views/feedback/Rating.vue'
import ShareYourThoughts from '@/views/feedback/ShareYourThoughts.vue'

import Appointments from '@/views/appointments/Appointments.vue'
import Modal from '@/components/shared/Modal.vue'

import Modal from '../components/shared/Modal.vue'  

const routes = [
  // Default route
  { path: '/', redirect: '/idle' },

  // Non-layout routes (Idle, Announcements, Login)
  { path: '/display', component: Display},
  { path: '/idle', component: Idle },
  { path: '/announcements', component: Announcements },
  { path: '/login', component: Login },
  { path: '/login-rfid', component: LoginRFID },
  { path: '/login-pin', component: LoginPIN },
  { path: '/modal', component: Modal},

  // Authenticated routes (inside layout)
  {
    path: '/',
    component: UserLayout,
    children: [
      { path: 'home', component: KioskHome },
      {
        path: '/document-services', component: DocumentServices,
        children: [
          { path: ':docType', component: DocumentFormWrapper, },
        ],
      },
      { path: 'equipment-borrowing', component: EquipmentBorrowing },
      { path: 'help-and-support', component: HelpAndSupport },
      { path: 'feedback', component: Feedback,
          children: [
            { path: '', redirect: '/feedback/select' },
            { path: 'select', component: FeedbackSelect },
            { path: 'rating', component: Rating },
            { path: 'comments', component: ShareYourThoughts },
          ]
      },
      { path: 'appointments', component: Appointments },
      { path: '/modal', component: Modal },
    ],
  },

  // Fallback for unknown routes
  { path: '/:pathMatch(.*)*', redirect: '/idle' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router