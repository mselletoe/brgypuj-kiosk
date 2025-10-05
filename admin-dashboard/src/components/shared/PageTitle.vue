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
    <h1 class="text-2xl font-semibold text-[#5B5B5B]">
      {{ title }}
    </h1>
  </div>
</template>