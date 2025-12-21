<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // primary, outline, secondary, ghost
  },
  size: {
    type: String,
    default: 'md',
  },
  disabled: {
    type: Boolean,
    default: false,
  }
})

const variants = {
  primary: 'bg-[#013C6D] text-white shadow-md active:shadow-inner',

  secondary: 'bg-[#1B5886] text-white shadow-md hover:opacity-90',  

  outline: 'border-2 border-[#1B5886] text-[#1B5886] bg-transparent',
  
  disabled: 'bg-[#BBC3CE] text-white cursor-not-allowed shadow-sm',
}

const sizes = {
  sm: 'px-4 py-1.5 text-xs',
  md: 'px-8 py-3 text-base',
  lg: 'px-12 py-4 text-xl',
}

const buttonClass = computed(() => {
  return [
    'inline-flex items-center justify-center font-bold rounded-xl transition-all duration-200 select-none active:scale-95',
    variants[props.variant] || variants.primary,
    sizes[props.size],
    props.disabled ? 'opacity-50 cursor-not-allowed active:scale-100' : ''
  ]
})
</script>

<template>
  <button :class="buttonClass" :disabled="disabled">
    <slot /> </button>
</template>