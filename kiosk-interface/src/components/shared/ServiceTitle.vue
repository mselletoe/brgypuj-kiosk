<script setup>
// Define the properties the component accepts
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="py-6">
    <h1 class="text-4xl md:text-5xl font-extrabold text-[#013C6D] drop-shadow-md tracking-tight">
      {{ title }}
    </h1>
    
    <p v-if="subtitle" class="mt-2 text-lg text-[#013C6D] font-medium">
      {{ subtitle }}
    </p>
  </div>
</template>