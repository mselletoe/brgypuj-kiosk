<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-4 border-[#003A6B]">
    <!-- Left: Logo -->
    <div class="flex items-center space-x-1">
      <img src="../assets/images/Pob1Logo.svg" alt="Poblacion 1, Amadeo, Cavite" class="w-[40px] h-[40px]" />

      <div class="flex flex-col font-poppins">
        <h1 class="text-[14px] font-bold leading-[1] tracking-tight">Brgy. Poblacion 1</h1> <br/>
        <h2 class="text-[14px] font-light -mt-5 leading-[1] tracking-tight">Amadeo, Cavite - Kiosk System</h2>
      </div>
    </div>

    <!-- Center: Time and Date -->
    <div class="text-center font-poppins">
      <p class="text-[14px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[14px] font-light mt-1 leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <!-- Right: Profile and Logout -->
    <div class="flex items-center space-x-4 font-poppins">

      <button class="px-4 py-2 bg-[#D1E5F1] border-2 border-[#003A6B] 
                    rounded-md font-semibold
                    transition-colors duration-300 ease-in-out flex flex-col items-center leading-[0.5]">
                    <span class="text-[12px] -mt-[3px] leading-[1]">Angela Dela Cruz</span> <br/>
                    <span class="text-[8px] font-normal -mt-[4px] leading-[1]">Authenticated via RFID</span>
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

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import '../assets/images/Pob1Logo.svg';
import '../assets/vectors/Logout.svg';

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
});
onUnmounted(() => clearInterval(interval));

const logout = () => {
  alert("You have been logged out!");
};
</script>

<style scoped>
header {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
}

</style>
