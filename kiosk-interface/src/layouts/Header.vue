<script setup>
/**
 * @file Header.vue
 * @description Global navigation component for the Barangay Kiosk System.
 * Displays real-time clock, branding, and dynamic user authentication status.
 * Interacts with the Pinia Auth Store to reflect live user data and handle session termination.
 */

import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import '../assets/images/Pob1Logo.svg';
import '../assets/vectors/Logout.svg';

// --- Component State & Composables ---
const router = useRouter();
const authStore = useAuthStore();

/** @type {import('vue').Ref<string>} Reactive string for formatted 12-hour time */
const currentTime = ref("");

/** @type {import('vue').Ref<string>} Reactive string for the full formatted date */
const currentDate = ref("");

// --- Computed Properties (Auth State) ---

/** @returns {boolean} True if the current session is in Guest mode */
const isGuest = computed(() => authStore.isGuest);

/** @returns {string} The name of the authenticated resident or 'Guest' */
const displayName = computed(() => authStore.userName);

/** @returns {string} Contextual string describing the current auth method for UI feedback */
const userDetail = computed(() => 
  authStore.isRFID ? "Authenticated via RFID" : "Logged in as Guest User"
);

// --- Logic & Handlers ---

/**
 * Manually reloads the application state.
 * Used as a fallback/reset mechanism for the Kiosk UI.
 */
const handleRefresh = () => {
  window.location.reload();
};

/**
 * Updates the reactive date and time refs with current system values.
 * Formats time to 'HH:MM:SS AM/PM' and date to 'Weekday, Month Day, Year'.
 */
const updateDateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true, 
  })
  .toUpperCase();

  currentDate.value = now.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

/** @type {ReturnType<typeof setInterval> | null} Reference to the clock sync timer */
let interval;

// --- Lifecycle Hooks ---

onMounted(() => {
  updateDateTime();
  // Start 1-second interval for the real-time clock
  interval = setInterval(updateDateTime, 1000);
});

onUnmounted(() => {
  // Clear clock interval to prevent background memory leaks
  if (interval) clearInterval(interval);
});

/**
 * Terminates the user session.
 * Clears global auth state (Pinia + LocalStorage) and redirects to the idle screen.
 */
const logout = () => {
  authStore.logout(); //
  router.push('/idle');
};
</script>

<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-2 border-[#003A6B]">
    <div class="flex items-center space-x-1">
      <img src="../assets/images/Pob1Logo.svg" alt="Poblacion 1, Amadeo, Cavite" class="w-[40px] h-[40px]" />
      <div class="flex flex-col">
        <h1 class="text-[14px] font-bold leading-[1] tracking-tight">Brgy. Poblacion 1</h1> <br/>
        <h2 class="text-[14px] font-light -mt-5 leading-[1] tracking-tight">Amadeo, Cavite - Kiosk System</h2>
      </div>
    </div>

    <div class="text-center">
      <p class="text-[14px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[14px] font-light mt-1 leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <div class="flex items-center space-x-4">
      <button 
        @click="handleRefresh"
        class="flex h-10 w-10 items-center justify-center rounded-lg border-2 border-[#003A6B] text-[#003A6B] transition-transform active:scale-90"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
          <path d="M21 3v5h-5"></path>
          <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
          <path d="M3 21v-5h5"></path>
        </svg>
      </button>

      <div 
        v-if="isGuest"
        class="flex flex-col items-center justify-center rounded-lg border-2 border-[#E8C462] bg-[#FFF9E5] px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-[#7A5C00]">{{ displayName }}</span>
        <span class="text-[9px] italic font-medium text-[#7A5C00]">{{ userDetail }}</span>
      </div>

      <div 
        v-else
        class="flex flex-col items-center justify-center rounded-lg border-2 border-[#003A6B] bg-[#D1E5F1] px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-[#003A6B]">{{ displayName }}</span>
        <span class="text-[9px] italic font-medium text-[#003A6B]">{{ userDetail }}</span>
      </div>

      <button @click="logout" class="px-4 py-2 bg-[#FF2B3A] border-2 border-[#FF2B3A] 
        hover:bg-[#CD000E] text-white font-light rounded-md
        transition-colors duration-300 ease-in-out
        flex items-center space-x-2 text-[12px]">
        <span>Logout</span>
        <img src="../assets/vectors/Logout.svg" class="w-6" />
      </button>
    </div>
  </header>
</template>

<style scoped>
header {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 50; 
}
</style>