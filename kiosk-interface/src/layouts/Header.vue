<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { auth, logout as authLogout } from "@/stores/auth";
import { useRouter } from "vue-router";
import '../assets/images/Pob1Logo.svg';
import '../assets/vectors/Logout.svg';

const router = useRouter();
const currentTime = ref("");
const currentDate = ref("");

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

let interval;
onMounted(() => {
  updateDateTime();
  interval = setInterval(updateDateTime, 1000);

  // This logic is still correct.
  const stored = localStorage.getItem('auth_user');
  if (stored) {
    const parsed = JSON.parse(stored);
    auth.user = parsed.user;
    auth.isGuest = parsed.isGuest;
  }
});
onUnmounted(() => clearInterval(interval));

const logout = () => {
  authLogout();
  localStorage.removeItem('auth_user');
  window.location.href = '/idle';
};

// --- MODIFIED: This computed property is now fixed ---
const displayName = computed(() => {
  if (auth.user?.isAdmin) return "Admin";
  if (auth.isGuest) return "Guest User";
  
  // Check for the full resident object's fields first
  if (auth.user?.first_name && auth.user?.last_name) {
    return `${auth.user.first_name} ${auth.user.last_name}`;
  }
  
  // Fallback for older "Guest" or partial objects
  return auth.user?.name || "Guest";
});
// --- END OF MODIFICATION ---

const accessType = computed(() => {
  if (auth.user?.isAdmin) return "Admin Access";
  if (auth.isGuest) return "Public Access";
  return "Authenticated via RFID";
});
</script>

<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-2 border-[#003A6B]">
    <div class="flex items-center space-x-1">
      <img src="../assets/images/Pob1Logo.svg" alt="Poblacion 1, Amadeo, Cavite" class="w-[40px] h-[40px]" />

      <div class="flex flex-col font-poppins">
        <h1 class="text-[14px] font-bold leading-[1] tracking-tight">Brgy. Poblacion 1</h1> <br/>
        <h2 class="text-[14px] font-light -mt-5 leading-[1] tracking-tight">Amadeo, Cavite - Kiosk System</h2>
      </div>
    </div>

    <div class="text-center font-poppins">
      <p class="text-[14px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[14px] font-light mt-1 leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <div class="flex items-center space-x-4 font-poppins">

      <button class="px-4 py-2 bg-[#D1E5F1] border-2 border-[#003A6B] 
        rounded-md font-semibold
        transition-colors duration-300 ease-in-out flex flex-col items-center leading-[0.5]">
        <span class="text-[12px] leading-[1]">
          {{ displayName }}
        </span> <br/>
        <span class="text-[8px] font-normal -mt-[4px] leading-[1]">
          {{ accessType }}
        </span>
      </button>

      <button @click="logout" class="px-4 py-2 bg-[#FF2B3A] border-2 border-[#FF2B3A] 
        hover:bg-[#CD000E] text-white font-light rounded-md
        transition-colors duration-300 ease-in-out
        flex items-center space-x-2 text-[12px]"><span>Logout</span>
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