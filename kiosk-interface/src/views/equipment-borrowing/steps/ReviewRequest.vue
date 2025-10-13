<script setup>
defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  borrowerInfo: Object,
  goNext: Function,
  goBack: Function,
})
</script>

<template>
  <div class="p-8">
    <h2 class="text-2xl font-bold mb-4">Review Request</h2>
    <!-- Review selected equipment, dates, and borrower info -->

    <div class="flex gap-2 mt-4">
      <button @click="goBack('info')" class="px-6 py-2 bg-gray-300 rounded">Back</button>
      <!-- <button @click="goNext('submitted')" class="px-6 py-2 bg-green-600 text-white rounded">Submit</button>  KUNG SAAN MO DALHEN -->
    </div>
  </div>
</template>