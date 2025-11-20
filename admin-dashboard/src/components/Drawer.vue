<script setup>
import {
  HomeIcon,
  DocumentTextIcon,
  BellIcon,
  CalendarDaysIcon,
  UsersIcon,
  ChatBubbleBottomCenterTextIcon,
  FolderIcon,
  DocumentCheckIcon
} from '@heroicons/vue/24/solid'

import { NButton } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuItems = [
  { label: 'Overview', icon: HomeIcon, to: '/overview' },
  { label: 'Document Requests', icon: DocumentTextIcon, to: '/requests' },
  { label: 'Document Services', icon: FolderIcon, to: '/document-services' },
  { label: 'Announcements Manager', icon: BellIcon, to: '/announcements' },
  { label: 'Community Feedback', icon: ChatBubbleBottomCenterTextIcon, to: '/community-feedback' },
  { label: 'Residents Management', icon: UsersIcon, to: '/residents' },
  { label: 'Equipment Request', icon: DocumentCheckIcon, to: '/equipment-management' },
  { label: 'Help & Support', icon: DocumentCheckIcon, to: '/help-support' }
]
</script>

<template>
  <div class="w-full h-full">
    <ul class="w-full space-y-1">
      <li v-for="item in menuItems" :key="item.to" class="w-full">
        <n-button
          quaternary
          block
          size="medium"
          class="!justify-start !px-4 !py-4 !rounded-md !w-full transition-all duration-200 text-sm"
          :style="route.path === item.to
            ? 'background-color: #0957FF; color: white; font-weight: 600;'
            : 'background-color: transparent; color: #535353; font-weight: 500;'"
          @click="router.push(item.to)"
        >
          <component :is="item.icon" class="w-4 h-4 mr-3" />
          {{ item.label }}
        </n-button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.n-button:hover {
  background-color: rgba(9, 87, 255, 0.08);
  transition: background-color 0.2s ease;
}
</style>