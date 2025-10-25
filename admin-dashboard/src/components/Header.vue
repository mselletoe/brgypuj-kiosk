<script setup>
import { h, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NDropdown } from 'naive-ui'
import { useAuth } from '@/stores/authStore'
import { UserCircleIcon, Cog6ToothIcon, LockClosedIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/solid'

const router = useRouter()
const auth = useAuth()
auth.loadToken()

console.log('Auth user:', auth.user)
console.log('Token:', auth.token)

const renderIcon = (icon) => () => h(icon, { class: 'h-5 w-5' })

const dropdownOptions = [
  { label: 'My Profile', key: 'profile', icon: renderIcon(UserCircleIcon) },
  { label: 'Dashboard Settings', key: 'settings', icon: renderIcon(Cog6ToothIcon) },
  { label: 'Password and Security', key: 'security', icon: renderIcon(LockClosedIcon) },
  { type: 'divider' },
  { label: 'Log Out', key: 'logout', icon: renderIcon(ArrowLeftOnRectangleIcon) }
]

// Handle dropdown selection
const handleSelect = (key) => {
  switch(key) {
    case 'profile':
      console.log('Navigate to My Profile')
      break
    case 'settings':
      console.log('Navigate to Dashboard Settings')
      break
    case 'security':
      console.log('Navigate to Password and Security')
      break
    case 'logout':
      console.log('Logging out...')
      auth.logout()
      router.replace('/auth')
      break
  }
}
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
              <span class="text-sm font-bold text-gray-800">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
              <span class="text-xs text-gray-500">{{ auth.user?.role }}</span>
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