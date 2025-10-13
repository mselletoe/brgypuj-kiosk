<script setup>
defineProps({
  selectedDates: Object,
  goNext: Function,
  goBack: Function,
})
</script>

<template>
  <div class="p-8">
    <h2 class="text-2xl font-bold mb-4">Select Dates</h2>
    <!-- Date selection UI -->

    <div class="flex gap-2 mt-4">
      <button @click="goBack('select')" class="px-6 py-2 bg-gray-300 rounded">Back</button>
      <button @click="goNext('info')" class="px-6 py-2 bg-blue-600 text-white rounded">Next</button>
    </div>
  </div>
</template>