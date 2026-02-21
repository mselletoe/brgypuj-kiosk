<script setup>
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import {
  HomeIcon, // For Overview
  DocumentTextIcon, // For Document Request
  WrenchScrewdriverIcon, // For Equipment Request
  ChatBubbleLeftRightIcon, // For Feedback
  SpeakerWaveIcon, // For Announcements
  FolderOpenIcon, // For Document Services
  CircleStackIcon, // For Equipment Inventory
  QuestionMarkCircleIcon, // For FAQs
  UserGroupIcon, // For Residents
  Cog6ToothIcon, // For Settings
  UserCircleIcon // For Account
} from '@heroicons/vue/24/solid'

const router = useRouter()
const route = useRoute()

const menuGroups = [
  {
    title: null, // Top section has no header
    items: [
      { label: 'Overview', icon: HomeIcon, to: '/overview' },
      { label: 'Document Requests', icon: DocumentTextIcon, to: '/document-requests' },
      { label: 'Equipment Requests', icon: WrenchScrewdriverIcon, to: '/equipment-requests' },
      { label: 'Feedback and Reports', icon: ChatBubbleLeftRightIcon, to: '/feedback-and-reports' },
      // { label: 'SMS Announcements', icon: SpeakerWaveIcon, to: '/sms-announcements' },
    ]
  },
  {
    title: 'SYSTEM MANAGERS',
    items: [
      { label: 'Document Services', icon: FolderOpenIcon, to: '/document-services' },
      { label: 'Equipment Inventory', icon: CircleStackIcon, to: '/equipment-inventory' },
      { label: 'Kiosk Announcements', icon: SpeakerWaveIcon, to: '/kiosk-announcements' },
      { label: 'Blotter and KP Logs', icon: UserCircleIcon, to: '/blotter-kp-logs' },
      { label: 'Residents Information', icon: UserGroupIcon, to: '/residents-management' },
    ]
  },
  {
    title: 'HELP & SUPPORT',
    items: [
      { label: 'FAQs Management', icon: QuestionMarkCircleIcon, to: '/faqs-management' },
      { label: 'Contact Information', icon: UserCircleIcon, to: '/contact-information' },
      // { label: 'System Settings', icon: Cog6ToothIcon, to: '/system-settings' },
    ]
  }
]

const isActive = (path) => route.path.startsWith(path)
</script>

<template>
  <div class="w-full h-full select-none">
    <nav class="space-y-6">
      <div v-for="group in menuGroups" :key="group.title || 'top'">
        <h3 v-if="group.title" class="px-3 mb-2 text-[11px] font-bold text-gray-400 tracking-wider">
          {{ group.title }}
        </h3>

        <ul class="space-y-1">
          <li v-for="item in group.items" :key="item.to">
            <n-button
              quaternary
              block
              class="!justify-start !px-3 !py-5 !rounded-lg !border-none transition-all duration-200"
              :class="isActive(item.to) ? 'active-nav' : 'inactive-nav'"
              @click="router.push(item.to)"
            >
              <template #icon>
                <component :is="item.icon" class="w-5 h-5" />
              </template>
              <span class="font-semibold text-sm">{{ item.label }}</span>
            </n-button>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.active-nav {
  background-color: #0957FF !important;
  color: white !important;
}

.inactive-nav {
  color: #6b7280 !important;
}

.inactive-nav:hover {
  background-color: transparent !important;
  color: #0957FF !important;
}

:deep(.n-button__icon) {
  margin-right: 12px !important;
}
</style>