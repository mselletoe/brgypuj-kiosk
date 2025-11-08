<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-800">
      {{ title }}
    </h1>
  </div>
</template>