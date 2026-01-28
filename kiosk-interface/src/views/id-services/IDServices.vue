<script setup>
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

const router = useRouter()
const goBack = () => router.push('/home')
</script>

<template>
  <div class="flex flex-col w-full h-full">
    
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          I.D Services
        </h1>
        <p class="text-[#03335C] -mt-2">
          Description
        </p>
      </div>
    </div>

    <div>
      <!-- RFID No and registered goes here -->
    </div>
    <div>
        <!-- I.D Services content goes here -->
    </div>
  </div>
</template>