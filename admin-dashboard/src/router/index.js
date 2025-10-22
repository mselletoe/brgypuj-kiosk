import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/authStore'

import AdminLayout from '@/layouts/AdminLayout.vue'
import Overview from '@/views/Overview.vue'
import Requests from '@/views/Requests.vue'
import Documenttemplates from '@/views/DocumentTemplates.vue'
import Announcements from '@/views/Announcements.vue'
import Appointments from '@/views/Appointments.vue'
import CommunityFeedback from '@/views/CommunityFeedback.vue'
import InformationHub from '@/views/InformationHub.vue'
import Residents from '@/views/Residents.vue'
import Utilities from '@/views/Utilities.vue'
import Auth from '@/views/Auth.vue'
import CreateAccount from '@/views/CreateAccount.vue'

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
      { path: 'document-templates', component: Documenttemplates },
      { path: 'announcements', component: Announcements },
      { path: 'appointments', component: Appointments },
      { path: 'community-feedback', component: CommunityFeedback },
      { path: 'information-hub', component: InformationHub },
      { path: 'residents', component: Residents },
      { path: 'utilities', component: Utilities }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  
  // Load token from localStorage if not already loaded
  if (!auth.token) {
    auth.loadToken()
  }

  const isAuthenticated = !!auth.token
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  // If page requires auth and user is NOT authenticated
  if (requiresAuth && !isAuthenticated) {
    next('/auth')
  }
  // If page requires guest (auth/create-account) and user IS authenticated
  else if (requiresGuest && isAuthenticated) {
    next('/overview')
  }
  // Otherwise, allow navigation
  else {
    next()
  }
})

export default router