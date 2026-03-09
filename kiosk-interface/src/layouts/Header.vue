<script setup>
/**
 * @file Header.vue
 * @description Global navigation component for the Barangay Kiosk System.
 * Displays real-time clock, branding (dynamic from system config), and user auth status.
 */

import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useRfidRegistrationStore } from "@/stores/registration";
import { useSystemConfig } from "@/composables/useSystemConfig";
import '../assets/vectors/Logout.svg';

const router       = useRouter();
const route        = useRoute();
const authStore    = useAuthStore();
const rfidRegStore = useRfidRegistrationStore();

// ── System config (logo + brgy name/subname) ──────────────────────────────────
const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig();

// ── Clock ─────────────────────────────────────────────────────────────────────
const currentTime = ref("");
const currentDate = ref("");

const updateDateTime = () => {
  const now = new Date();
  currentTime.value = now
    .toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true })
    .toUpperCase();
  currentDate.value = now.toLocaleDateString("en-US", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });
};

let interval;
onMounted(() => { updateDateTime(); interval = setInterval(updateDateTime, 1000); });
onUnmounted(() => { if (interval) clearInterval(interval); });

// ── Auth ──────────────────────────────────────────────────────────────────────
const isAdminRegistration = computed(() => route.path === '/register');
const isGuest             = computed(() => authStore.isGuest);
const displayName         = computed(() => authStore.userName);
const userDetail          = computed(() =>
  authStore.isRFID ? "Authenticated via RFID" : "Logged in as Guest User"
);

const logout = () => { authStore.logout(); router.push('/idle'); };
</script>

<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-2 border-[#003A6B]">

    <!-- ── Branding ───────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-2">
      <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" alt="Barangay Logo" class="w-[40px] h-[40px] min-w-[40px] object-cover rounded-full overflow-hidden" />
      <div class="flex flex-col">
        <h1 class="text-[14px] font-bold leading-[1] tracking-tight">{{ brgyName }}</h1><br />
        <h2 class="text-[14px] font-light -mt-5 leading-[1] tracking-tight">{{ brgySubname }}</h2>
      </div>
    </div>

    <!-- ── Clock ─────────────────────────────────────────────────────────── -->
    <div class="text-center">
      <p class="text-[14px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[14px] font-light mt-1 leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <!-- ── User badge + logout ────────────────────────────────────────────── -->
    <div class="flex items-center space-x-4">

      <!-- Admin Registration Badge -->
      <div
        v-if="isAdminRegistration"
        class="flex flex-col items-center justify-center rounded-lg border-2 border-blue-500 bg-blue-50 px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-blue-700">Admin</span>
        <span class="text-[9px] italic font-medium text-blue-700">RFID Registration Mode</span>
      </div>

      <!-- Guest Badge -->
      <div
        v-else-if="isGuest"
        class="flex flex-col items-center justify-center rounded-lg border-2 border-[#E8C462] bg-[#FFF9E5] px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-[#7A5C00]">{{ displayName }}</span>
        <span class="text-[9px] italic font-medium text-[#7A5C00]">{{ userDetail }}</span>
      </div>

      <!-- RFID Resident Badge -->
      <div
        v-else
        class="flex flex-col items-center justify-center rounded-lg border-2 border-[#003A6B] bg-[#D1E5F1] px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-[#003A6B]">{{ displayName }}</span>
        <span class="text-[9px] italic font-medium text-[#003A6B]">{{ userDetail }}</span>
      </div>

      <button
        @click="logout"
        class="px-4 py-2 bg-[#FF2B3A] border-2 border-[#FF2B3A] hover:bg-[#CD000E]
               text-white font-light rounded-md transition-colors duration-300 ease-in-out
               flex items-center space-x-2 text-[12px]"
      >
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