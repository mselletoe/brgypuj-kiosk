<script setup>
const props = defineProps({
  selectedEquipment: Array,
  goNext: Function,
})

const continueStep = () => props.goNext('dates')
</script>

<template>
  <div class="p-8">
    <h2 class="text-2xl font-bold mb-4">Select Equipment</h2>
    <!-- Equipment selection UI goes here -->

    <button
      @click="continueStep"
      class="mt-4 px-6 py-2 bg-blue-600 text-white rounded"
    >
      Next
    </button>
  </div>
</template>