<script setup>
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
</script>

<template>
  <div class="flex flex-col w-full h-full">
    
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          Transaction History
        </h1>
        <p class="text-[#03335C] -mt-2">
          See your previous transactions here.
        </p>
      </div>
    </div>

    <div>
      <!-- Transaction history content goes here -->
    </div>
  </div>
</template>