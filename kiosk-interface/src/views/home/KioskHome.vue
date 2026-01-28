<script setup>
/**
 * @file KioskHome.vue
 * @description Central Dashboard of the Kiosk. 
 * Provides navigation to various Barangay services. Implements session recovery 
 * and authentication guards to ensure only authorized users access the dashboard.
 */

import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/shared/Button.vue'

// --- Component State & Composables ---
const router = useRouter()
const auth = useAuthStore()

// --- Lifecycle Hooks ---

onMounted(() => {
  /** * Attempt to restore session from LocalStorage (persistance).
   * This handles page refreshes or unexpected app restarts.
   */
  auth.restore()

  /**
   * Authentication Guard:
   * If no valid session is found after restoration, redirect to the login entry point.
   */
  if (!auth.isAuthenticated) {
    router.replace('/login')
  }
})

// --- Navigation Logic ---

/**
 * Navigates to a specific service route.
 * Uses 'replace' instead of 'push' for kiosk environments to prevent 
 * extensive back-stack history accumulation.
 * @param {string} path - The target route name or path.
 */
function goTo(path) {
  router.replace(path)
}
</script>

<template>
  <div class="flex flex-col items-center text-[#003a6b] w-full">
    <div class="flex w-full justify-between">
      <div class="flex flex-col text-left">
        <h2 class="text-[50px] font-normal tracking-[-0.03em] drop-shadow-[3px_3px_5px_rgba(0,0,0,0.3)]">
          Welcome to
        </h2>
        <h1 class="mb-8 text-[68px] font-bold leading-[0.6] tracking-[-0.03em] text-[#003a6b] drop-shadow-[3px_3px_5px_rgba(0,0,0,0.3)]">
          Barangay Services
        </h1>
        <p class="m-0 text-[17.5px] font-normal leading-tight">
          Select a service below to get started.<br>
          All services are designed for easy touch navigation.
        </p>
      </div>
      <div class="logo-section">
        <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="h-[180px] w-[180px]" />
      </div>          
    </div>

    <div class="flex flex-col items-center w-full">
      <div class="mt-12 flex w-full flex-wrap justify-between gap-4">
        
        <div 
          v-if="!auth.isGuest"
          class="flex h-[220px] min-w-[165px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] bg-[#2C67E7] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 hover:-translate-y-[3px] hover:scale-105 active:scale-[0.97]"
          @click="goTo('document-services')"
        >
          <img src="@/assets/vectors/DocumentServices.svg" alt="Document Services" class="mb-[5px] h-[105px] w-[105px]" />
          <p class="m-0 mb-[5px] flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white">Document<br>Services</p>
          <p class="m-0 text-[11px] font-normal leading-[12px] text-white">Barangay ID, Clearances,<br>Certificates, and Permits</p>
        </div>

        <div 
          v-if="!auth.isGuest"
          class="flex h-[220px] min-w-[165px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] bg-[#F16C14] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 hover:-translate-y-[3px] hover:scale-105 active:scale-[0.97]"
          @click="goTo('equipment-borrowing')"
        >
          <img src="@/assets/vectors/EquipmentBorrowing.svg" alt="Equipment Borrowing" class="mb-[5px] h-[105px] w-[105px]" />
          <p class="m-0 mb-[5px] flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white">Equipment<br>Borrowing</p>
          <p class="m-0 text-[11px] font-normal leading-[12px] text-white">Borrow tents, chairs, and<br>other Barangay utilities</p>
        </div>
        
        <div 
          class="flex h-[220px] min-w-[165px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] bg-[#21C05C] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 hover:-translate-y-[3px] hover:scale-105 active:scale-[0.97]"
          @click="goTo('id-services')"
        >
          <img alt="RFID Services" class="mb-[5px] h-[105px] w-[105px]" />
          <p class="m-0 mb-[5px] flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white">RFID Services</p>
          <p class="m-0 text-[11px] font-normal leading-[12px] text-white">Request or Manage your Barangay RFID card.</p>
        </div>

        <div 
          class="flex h-[220px] min-w-[165px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] bg-[#A451F3] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 hover:-translate-y-[3px] hover:scale-105 active:scale-[0.97]"
          @click="goTo('help-and-support')"
        >
          <img src="@/assets/vectors/HelpSupport.svg" alt="Help & Support" class="mb-[5px] h-[105px] w-[105px]" />
          <p class="m-0 mb-[5px] flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white">Help &<br>Support</p>
          <p class="m-0 text-[11px] font-normal leading-[12px] text-white">Find answers and<br>get assistance</p>
        </div>

        <div 
          class="flex h-[220px] min-w-[165px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] bg-[#13B3A1] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 hover:-translate-y-[3px] hover:scale-105 active:scale-[0.97]"
          @click="goTo('feedback')"
        >
          <img src="@/assets/vectors/Feedback.svg" alt="Feedback" class="mb-[5px] h-[105px] w-[105px]" />
          <p class="m-0 mb-[5px] flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white">Feedback</p>
          <p class="m-0 text-[11px] font-normal leading-[12px] text-white">Help us improve the<br>Barangay Kiosk<br>experience</p>
        </div>      
      </div>

      <div class="mt-8 flex gap-5 w-full">
        <Button 
          v-if="!auth.isGuest"
          variant="outline" 
          size="md" 
          class="flex-1 shadow-[4px_4px_8px_rgba(0,0,0,0.15)]"
          @click="goTo('transaction-history')"
        >
          Transactions
        </Button>

        <Button 
          variant="outline" 
          size="md" 
          class="flex-1 shadow-[4px_4px_8px_rgba(0,0,0,0.15)]"
          @click="goTo('inannouncements')"
        >
          Announcements
        </Button>
      </div>
    </div>
  </div>
</template>