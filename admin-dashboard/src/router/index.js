import { createRouter, createWebHistory } from 'vue-router'
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
import Login from '@/views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },

  {
    path: '/',
    component: AdminLayout,
    redirect: '/overview',
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

export default router