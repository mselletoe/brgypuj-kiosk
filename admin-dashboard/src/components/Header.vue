<script setup>
/**
 * @file Header.vue
 * @description Administrative dashboard header component.
 * Provides the top navigation bar containing the global search placeholder
 * and the user profile dropdown. Integrates with the Admin Auth store
 * to display current session metadata and handle logout procedures.
 */
import { ref, h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NDropdown } from 'naive-ui'
import { UserCircleIcon, QuestionMarkCircleIcon, BellIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/solid'
import { useAdminAuthStore } from '@/stores/auth'

const router = useRouter()
const adminAuth = useAdminAuthStore()

// Dropdown State
const showNotifications = ref(false)

// Mock Data for the dropdown preview
const recentNotifications = ref([
  { id: 1, title: 'New Document Request', time: '5 minutes ago', unread: true },
  { id: 2, title: 'New Document Request', time: '27 minutes ago', unread: false },
  { id: 3, title: 'Payment Completed', time: '1 hour ago', unread: true },
  { id: 4, title: 'Equipment Overdue', time: '2 hours ago', unread: true },
  { id: 5, title: 'New Feedback Received', time: 'Yesterday', unread: true }
])

// Dynamically calculate the number of unread notifications
const unreadCount = computed(() => recentNotifications.value.filter(n => n.unread).length)

/**
 * Utility function to render Heroicons within Naive UI components.
 * @param {Component} icon - The Heroicon component to be rendered.
 * @returns {Function} A VNode rendering function.
 */
const renderIcon = (icon) => () => h(icon, { class: 'h-5 w-5' })

/**
 * Configuration for the user profile dropdown menu.
 */
const dropdownOptions = [
  { label: 'Account Settings', key: 'profile', icon: renderIcon(UserCircleIcon) },
  { type: 'divider' },
  { label: 'Log Out', key: 'logout', icon: renderIcon(ArrowLeftOnRectangleIcon) }
]

/**
 * Orchestrates navigation and session actions based on dropdown selection.
 */
const handleSelect = (key) => {
  switch(key) {
    case 'profile':
      router.push('/account-settings')
      break
    case 'logout':
      adminAuth.logout()
      router.replace('/auth')
      break
  }
}

const goToHelp = () => {
  router.push('/help-and-support')
}

// Routes to full Notification view and closes the dropdown
const goToAllNotifications = () => {
  showNotifications.value = false
  router.push('/notifications')
}

const username = computed(() => adminAuth.admin?.username || 'Admin Account')
const role = computed(() => adminAuth.admin?.role || 'Brgy. Captain')
</script>

<template>
  <header class="pb-8 flex items-center justify-between w-[99%]">
    <div class="bg-white rounded-md w-[700px] h-[40px]"></div>

    <div class="flex items-center gap-2">
      <button @click="goToHelp" class="p-2 text-[#1F2937] hover:text-[#2D4465] rounded-full transition-colors">
        <QuestionMarkCircleIcon class="h-6 w-6" />
      </button>

      <div v-if="showNotifications" @click="showNotifications = false" class="fixed inset-0 z-40"></div>

      <div class="relative z-50">
        <button @click="showNotifications = !showNotifications" class="p-2 text-[#1F2937] rounded-full hover:text-[#2D4465] transition-colors relative">
          <BellIcon class="h-6 w-6" />
          <span v-if="unreadCount > 0" class="absolute top-1 right-1 bg-red-600 text-white text-[9px] font-bold px-1 rounded-full border border-white leading-none flex items-center justify-center min-w-[18px] h-[18px]">
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </button>

        <div v-if="showNotifications" class="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-[0_4px_20px_rgba(0,0,0,0.1)] border border-gray-200 overflow-hidden">
          <div class="px-4 py-3 border-b border-gray-100 font-bold text-gray-800 text-[13px]">
            Notifications
          </div>
          
          <div class="max-h-[320px] overflow-y-auto">
            <div 
              v-for="notif in recentNotifications" 
              :key="notif.id" 
              @click="notif.unread = false"
              class="px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer flex justify-between items-center transition-colors"
            >
              <div class="flex flex-col pr-4">
                <span class="text-[13px] text-gray-800 font-medium leading-tight">{{ notif.title }}</span>
                <span class="text-[11px] text-gray-400 mt-1">{{ notif.time }}</span>
              </div>
              <div v-if="notif.unread" class="w-2 h-2 rounded-full bg-[#0d6efd] flex-shrink-0"></div>
            </div>
          </div>
          
          <div 
            @click="goToAllNotifications" 
            class="py-3 text-center text-[#0d6efd] text-[12px] hover:underline cursor-pointer bg-white border-t border-gray-100 font-medium"
          >
            View All Notifications
          </div>
        </div>
      </div>
      
      <n-dropdown
        trigger="click"
        :options="dropdownOptions"
        @select="handleSelect"
        placement="bottom-end"
      >
        <button class="btn btn-sm btn-ghost px-2 rounded-md w-[220px] h-[40px] hover:bg-[#D6E9FE] text-start flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center overflow-hidden border border-gray-200">
              <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=Jett" alt="Avatar" class="w-full h-full object-cover bg-blue-50" />
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-bold text-gray-800">{{ username }}</span>
              <span class="text-[10px] text-gray-500">{{ role }}</span>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </n-dropdown>
    </div>
  </header>
</template>