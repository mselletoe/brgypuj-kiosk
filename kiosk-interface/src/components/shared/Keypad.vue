<script setup>
import { BackspaceIcon } from '@heroicons/vue/24/outline';
defineEmits(['press', 'clear', 'backspace']);
</script>

<template>
  <div class="grid grid-cols-3 gap-3 w-full max-w-xs">
    <button @click="$emit('press', '1')" class="btn-keypad">1</button>
    <button @click="$emit('press', '2')" class="btn-keypad">2</button>
    <button @click="$emit('press', '3')" class="btn-keypad">3</button>
    
    <button @click="$emit('press', '4')" class="btn-keypad">4</button>
    <button @click="$emit('press', '5')" class="btn-keypad">5</button>
    <button @click="$emit('press', '6')" class="btn-keypad">6</button>
    
    <button @click="$emit('press', '7')" class="btn-keypad">7</button>
    <button @click="$emit('press', '8')" class="btn-keypad">8</button>
    <button @click="$emit('press', '9')" class="btn-keypad">9</button>
    
    <button @click="$emit('clear')" class="btn-keypad !bg-pink-100/60 !text-red-500 hover:!bg-pink-200/60 text-base font-medium">
      clear
    </button>
    <button @click="$emit('press', '0')" class="btn-keypad">0</button>
    <button @click="$emit('backspace')" class="btn-keypad !bg-yellow-100/60 !text-yellow-700 hover:!bg-yellow-200/60 flex items-center justify-center">
      <BackspaceIcon class="w-6 h-6" />
    </button>
  </div>
</template>

<style scoped>
/* Scoped styles for the keypad buttons */
.btn-keypad {
  /* MODIFIED: Made buttons smaller (h-14) and text smaller (text-xl) */
  @apply h-14 bg-gray-100 rounded-xl text-xl text-[#03335C]
         hover:bg-gray-200 transition-colors
         focus:outline-none focus:ring-2 focus:ring-blue-500 font-bold;
}
</style>