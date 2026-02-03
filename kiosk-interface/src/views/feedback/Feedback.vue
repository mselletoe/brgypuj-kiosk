<script setup>
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

import ServiceQualityIcon from '@/assets/vectors/ServiceQuality.svg'
import InterfaceDesignIcon from '@/assets/vectors/InterfaceDesign.svg'
import SystemSpeedIcon from '@/assets/vectors/SystemSpeed.svg'
import AccessibilityIcon from '@/assets/vectors/Accessibility.svg'
import GeneralExperienceIcon from '@/assets/vectors/GeneralExperience.svg'

const router = useRouter()

const categories = [
  { name: 'Service Quality', label: 'Service<br>Quality', icon: ServiceQualityIcon },
  { name: 'Interface Design', label: 'Interface<br>Design', icon: InterfaceDesignIcon },
  { name: 'System Speed', label: 'System<br>Speed', icon: SystemSpeedIcon },
  { name: 'Accessibility', label: 'Accessibility', icon: AccessibilityIcon },
  { name: 'General Experience', label: 'General<br>Experience', icon: GeneralExperienceIcon },
]

const goToRating = (category) => {
  router.push({ path: '/rating/', query: { category } })
}

const goBack = () => {
  router.push({ path: 'home' })
}
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Your Feedback Matters</h1>
        <p class="text-[#03335C] -mt-2">Description</p>
      </div>
    </div>

    <div class="text-center mt-8 mb-12">
      <h2 class="text-[42px] text-[#03335C] font-bold leading-none">
        What would you like to rate?
      </h2>
      <p class="text-[20px] text-[#03335C] italic font-medium mt-2">
        Select the area you'd like to share your thoughts on
      </p>
    </div>

    <div class="flex justify-center gap-6 px-6">
      <div 
        v-for="item in categories" 
        :key="item.name"
        @click="goToRating(item.name)"
        class="flex flex-col items-center justify-center flex-1 aspect-[4/5] rounded-[25px] cursor-pointer transition-all active:scale-95 shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)]"
        style="background: linear-gradient(to bottom, #2B6194, #1E466B);"
      >
        <img :src="item.icon" :alt="item.name" class="w-1/2 mb-6 brightness-0 invert" />
        <p class="text-white text-[24px] font-bold text-center leading-tight px-4" v-html="item.label"></p>
      </div>

    </div>
  </div>
</template>