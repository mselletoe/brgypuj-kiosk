import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/authStore'

import AdminLayout from '@/layouts/AdminLayout.vue'
import Overview from '@/views/Overview.vue'
import Requests from '@/views/requests/RequestsManagement.vue'
import Documenttemplates from '@/views/docutemp/DocumentTemplates.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import Announcements from '@/views/Announcements.vue'
import Appointments from '@/views/Appointments.vue'
import CommunityFeedback from '@/views/CommunityFeedback.vue'
import InformationHub from '@/views/InformationHub.vue'
import Residents from '@/views/Residents.vue'
import Auth from '@/views/Auth.vue'
import CreateAccount from '@/views/CreateAccount.vue'
import EquipmentManagement from '@/views/equipment/EquipmentManagement.vue'


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
      { path: 'requests', component: Requests },
      { path: 'document-services', component: DocumentServices },
      { path: 'announcements', component: Announcements },
      { path: 'appointments', component: Appointments },
      { path: 'community-feedback', component: CommunityFeedback },
      { path: 'information-hub', component: InformationHub },
      { path: 'residents', component: Residents },  
      { path: 'equipment-management', component: EquipmentManagement }
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