<script setup>
/**
 * @file Header.vue
 * @description Administrative dashboard header component.
 * Provides the top navigation bar containing the global search placeholder
 * and the user profile dropdown. Integrates with the Admin Auth store
 * to display current session metadata and handle logout procedures.
 */
import { h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NDropdown } from 'naive-ui'
import { UserCircleIcon, Cog6ToothIcon, LockClosedIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/solid'
import { useAdminAuthStore } from '@/stores/auth'

const router = useRouter()
const adminAuth = useAdminAuthStore()

/**
 * Utility function to render Heroicons within Naive UI components.
 * @param {Component} icon - The Heroicon component to be rendered.
 * @returns {Function} A VNode rendering function.
 */
const renderIcon = (icon) => () => h(icon, { class: 'h-5 w-5' })

/**
 * Configuration for the user profile dropdown menu.
 * Includes labels, keys for event handling, and rendered icons.
 */
const dropdownOptions = [
  { label: 'Account Settings', key: 'profile', icon: renderIcon(UserCircleIcon) },
  { type: 'divider' },
  { label: 'Log Out', key: 'logout', icon: renderIcon(ArrowLeftOnRectangleIcon) }
]

/**
 * Orchestrates navigation and session actions based on dropdown selection.
 * @param {string} key - The unique identifier of the selected menu item.
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

/**
 * Reactive computed properties to display administrator metadata.
 * Fallbacks are provided for scenarios where the auth store is still rehydrating.
 */
const username = computed(() => adminAuth.admin?.username || 'Admin')
const role = computed(() => adminAuth.admin?.role || 'Administrator')
</script>

<template>
  <header class="pb-8 flex items-center justify-between w-[99%]">
    <div class="bg-white rounded-md w-[700px] h-[40px]"></div>
    <div>
      <n-dropdown
        trigger="click"
        :options="dropdownOptions"
        @select="handleSelect"
        placement="bottom-end"
      >
        <button class="btn btn-sm btn-ghost px-2 rounded-md w-[220px] h-[40px] hover:bg-[#D6E9FE] text-start flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center overflow-hidden">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-bold text-gray-800">{{ username }}</span>
              <span class="text-xs text-gray-500">{{ role }}</span>
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