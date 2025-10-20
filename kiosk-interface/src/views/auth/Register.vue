<script setup>
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

</script>

<template>
  <div class="py-0 pb-8">
    <div class="flex items-center gap-4 between">
      <ArrowBackButton @click="goBackToHome" />
        <div class="flex items-center justify-between w-full">
            <h1 class="text-3xl font-bold text-[#013C6D]">Register your RFID</h1>
            <h1 class="text-3xl font-bold text-[#013C6D]">0054973429</h1>
        </div>
    </div>
  </div>
</template>