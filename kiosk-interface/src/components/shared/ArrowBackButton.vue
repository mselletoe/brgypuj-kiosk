<script setup>
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

defineProps({
  bgColor: {
    type: String,
    default: 'bg-white' 
  },
  arrowColor: {
    type: String,
    default: 'text-[#1B5886]' 
  }
})
</script>

<template>
  <button
    :class="[
      'w-14 h-14 flex items-center justify-center rounded-[10px] border-[2px] border-[#1B5886] shadow-xl transition-colors hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary',
      bgColor 
    ]"
    @click="$emit('click')"
  >
    <ArrowLeftIcon 
      :class="[
        'w-6 h-6', 
        'stroke-[2px]',
        arrowColor 
      ]" 
    />
  </button>
</template>