<template>
  <header class="flex items-center justify-between px-5 py-2 bg-white text-[#003A6B] shadow-md border-b-4 border-[#003A6B]">
    <!-- Left: Logo -->
    <div class="flex items-center space-x-1">
      <img src="../assets/images/Pob1Logo.svg" alt="Poblacion 1, Amadeo, Cavite" class="w-[70px] h-[70px]" />

      <div class="flex flex-col font-poppins">
        <h1 class="text-[19px] font-bold leading-[1] tracking-tight">Brgy. Poblacion 1</h1> <br/>
        <h2 class="text-[18px] font-light -mt-5 leading-[1] tracking-tight">Amadeo, Cavite - Kiosk System</h2>
      </div>
    </div>

    <!-- Center: Time and Date -->
    <div class="text-center font-poppins">
      <p class="text-[19px] font-bold leading-none tracking-tight">{{ currentTime }}</p>
      <p class="text-[18px] font-light leading-[1] tracking-tight">{{ currentDate }}</p>
    </div>

    <!-- Right: Profile and Logout -->
    <div class="flex items-center space-x-4 font-poppins">

      <button class="px-4 py-2 bg-[#D1E5F1] border-2 border-[#003A6B] 
                    hover:bg-[#003A6B] hover:text-[white] rounded-md font-semibold
                    transition-colors duration-300 ease-in-out">Profile</button>

      <button @click="logout" class="px-4 py-2 bg-[#FF2B3A] border-2 border-[#FF2B3A] 
                                    hover:bg-[#CD000E] text-white font-light rounded-md
                                    transition-colors duration-300 ease-in-out
                                    flex items-center space-x-2"><span>Logout</span>
                                    <img src="../assets/vectors/Logout.svg" class="w-7" />
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

  currentDate.value = now.toLocaleDateString([], {
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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

header {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
}

.font-poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
