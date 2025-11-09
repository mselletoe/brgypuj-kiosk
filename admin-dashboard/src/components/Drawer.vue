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
  { label: 'Requests', icon: DocumentTextIcon, to: '/requests' },
  { label: 'Document Services', icon: FolderIcon, to: '/document-services' },
  { label: 'Announcements', icon: BellIcon, to: '/announcements' },
  { label: 'Community Feedback', icon: ChatBubbleBottomCenterTextIcon, to: '/community-feedback' },
  { label: 'Residents', icon: UsersIcon, to: '/residents' },
  { label: 'Equipment Request', icon: DocumentCheckIcon, to: '/equipment-management' }
]
</script>

<template>
  <div class="drawer drawer-open">
    <div class="drawer-side">
      <ul class="w-full space-y-2">
        <li v-for="item in menuItems" :key="item.to" class="w-full">
          <n-button
            quaternary
            block
            size="large"
            class="!justify-start !px-4 !py-3 !rounded-md !w-full transition-all duration-200"
            :style="route.path === item.to
              ? 'background-color: #0957FF; color: white; font-weight: 500;'
              : 'background-color: transparent; color: #535353; font-weight: 500;'"
            @click="router.push(item.to)"
          >
            <component :is="item.icon" class="w-5 h-5 mr-3" />
            {{ item.label }}
          </n-button>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.n-button:hover {
  background-color: rgba(9, 87, 255, 0.08);
  transition: background-color 0.2s ease;
}
</style>