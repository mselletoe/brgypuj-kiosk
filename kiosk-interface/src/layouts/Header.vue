<script setup>
/**
 * @file Header.vue
 * @description Global navigation component for the Barangay Kiosk System.
 */

import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "@/stores/auth";
import { useRfidRegistrationStore } from "@/stores/registration";
import { useSystemConfig } from "@/composables/useSystemConfig";
import { useAutoLogout } from "@/composables/useAutoLogout";
import '../assets/vectors/Logout.svg';

const router       = useRouter();
const route        = useRoute();
const authStore    = useAuthStore();
const rfidRegStore = useRfidRegistrationStore();
const { t }        = useI18n();

const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig();
const { secondsRemaining } = useAutoLogout();

const countdownDisplay = computed(() => {
  const s = secondsRemaining.value;
  if (s <= 0) return null;
  if (s < 60) return t('sessionEndsIn', { time: `${s}s` });
  const m = Math.floor(s / 60);
  const rem = s % 60;
  const time = rem > 0 ? `${m}m ${rem}s` : `${m}m`;
  return t('sessionEndsIn', { time });
});

const countdownUrgent = computed(() => secondsRemaining.value > 0 && secondsRemaining.value <= 30);

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

const isAdminRegistration = computed(() => route.path === '/register');
const isGuest             = computed(() => authStore.isGuest);
const displayName         = computed(() => authStore.userName);
const userDetail          = computed(() =>
  authStore.isRFID ? t('authenticatedViaRFID') : t('loggedInAsGuest')
);

const logout = () => { authStore.logout(); router.push('/idle'); };

// --- Exit Kiosk Logic ---
const logoTapCount  = ref(0);
const showExitBtn   = ref(false);
const showExitModal = ref(false);
let tapTimer = null;

const handleLogoTap = () => {
  logoTapCount.value++;
  // Reset tap count after 3 seconds of inactivity
  clearTimeout(tapTimer);
  tapTimer = setTimeout(() => { logoTapCount.value = 0; }, 3000);

  if (logoTapCount.value >= 5) {
    showExitBtn.value = true;
    logoTapCount.value = 0;
    // Auto-hide exit button after 10 seconds
    setTimeout(() => { showExitBtn.value = false; }, 10000);
  }
};

const exitKiosk = () => { showExitModal.value = true; };
const cancelExit = () => { showExitModal.value = false; showExitBtn.value = false; };
const confirmExit = async () => {
  try {
    // Calls your backend to kill Chromium on the Raspberry Pi
    await fetch('http://localhost:8000/kiosk/system/exit-kiosk', { method: 'POST' });
  } catch {
    // Fallback: just close the window
    window.close();
  }
};
</script>

<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-2 border-[#003A6B]">

    <!-- Branding (tap 5x to reveal exit) -->
    <div class="flex items-center gap-2 select-none" @click="handleLogoTap">
      <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" alt="Barangay Logo" class="w-[40px] h-[40px] min-w-[40px] object-cover rounded-full overflow-hidden" />
      <div class="flex flex-col">
        <h1 class="text-[14px] font-bold leading-[1] tracking-tight">{{ brgyName }}</h1><br />
        <h2 class="text-[14px] font-light -mt-5 leading-[1] tracking-tight">{{ brgySubname }}</h2>
      </div>
    </div>

    <!-- Clock -->
    <div class="text-center">
      <p class="text-[14px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[14px] font-light mt-1 leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <!-- User badge + countdown + logout + exit -->
    <div class="flex items-center space-x-4">

      <div
        v-if="authStore.isAuthenticated && countdownDisplay"
        class="text-[10px] font-medium px-3 py-1 rounded-full border transition-colors duration-300"
        :class="countdownUrgent
          ? 'text-red-600 border-red-300 bg-red-50'
          : 'text-gray-400 border-gray-200 bg-gray-50'"
      >
        {{ countdownDisplay }}
      </div>

      <!-- Admin Registration Badge -->
      <div
        v-if="isAdminRegistration"
        class="flex flex-col items-center justify-center rounded-lg border-2 border-blue-500 bg-blue-50 px-4 py-1 min-w-[160px] leading-tight"
      >
        <span class="text-[13px] font-black text-blue-700">{{ $t('admin') }}</span>
        <span class="text-[9px] italic font-medium text-blue-700">{{ $t('rfidRegistrationMode') }}</span>
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

      <!-- Hidden Exit Button (appears after 5 taps on logo) -->
      <button
        v-if="showExitBtn"
        @click="exitKiosk"
        class="px-4 py-2 bg-gray-700 border-2 border-gray-700 hover:bg-gray-900
               text-white font-light rounded-md transition-colors duration-300 ease-in-out
               flex items-center space-x-2 text-[12px]"
      >
        <span>Exit Kiosk</span>
      </button>

      <button
        @click="logout"
        class="px-4 py-2 bg-[#FF2B3A] border-2 border-[#FF2B3A] hover:bg-[#CD000E]
               text-white font-light rounded-md transition-colors duration-300 ease-in-out
               flex items-center space-x-2 text-[12px]"
      >
        <span>{{ $t('logout') }}</span>
        <img src="../assets/vectors/Logout.svg" class="w-6" />
      </button>
    </div>

  </header>

  <!-- Exit Confirmation Modal -->
  <div
    v-if="showExitModal"
    class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
  >
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-[320px] text-center">
      <h2 class="text-[18px] font-bold text-[#003A6B] mb-2">Exit Kiosk Mode?</h2>
      <p class="text-[13px] text-gray-500 mb-6">This will close the kiosk and return to the desktop.</p>
      <div class="flex gap-3 justify-center">
        <button
          @click="cancelExit"
          class="px-5 py-2 rounded-lg border-2 border-gray-300 text-gray-600 text-[13px] hover:bg-gray-100"
        >
          Cancel
        </button>
        <button
          @click="confirmExit"
          class="px-5 py-2 rounded-lg bg-gray-700 text-white text-[13px] hover:bg-gray-900"
        >
          Yes, Exit
        </button>
      </div>
    </div>
  </div>

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