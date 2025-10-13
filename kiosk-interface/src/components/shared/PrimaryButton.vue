<script setup>
// Define the properties (props) that the parent component can pass down
// to customize the button's appearance.
defineProps({
  bgColor: {
    type: String,
    default: 'bg-[#013C6D]' // Default background color is the specified blue
  },
  textColor: {
    type: String,
    default: 'text-white' // Default text color is white
  },
  borderColor: {
    type: String,
    default: 'border-[#013C6D]' // Default border color matches the background
  }
})
</script>

<template>
  <button
    :class="[
      // Base styles that are always applied
      'flex items-center justify-center',
      'border-2 rounded-[10px]',
      'transition-colors hover:opacity-90',
      'shadow-xl', // Shadow added for depth

      // Default dimensions (can be overridden by a class in the parent)
      'h-10 w-[100px]',
      
      // Dynamic styles from props
      bgColor,
      textColor,
      borderColor
    ]"
  >
    <slot></slot>
  </button>
</template>