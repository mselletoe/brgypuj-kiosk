<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import ServiceQualityIcon from '@/assets/vectors/ServiceQuality.svg'
import InterfaceDesignIcon from '@/assets/vectors/InterfaceDesign.svg'
import SystemSpeedIcon from '@/assets/vectors/SystemSpeed.svg'
import AccessibilityIcon from '@/assets/vectors/Accessibility.svg'
import GeneralExperienceIcon from '@/assets/vectors/GeneralExperience.svg'

const router = useRouter()
const { t } = useI18n()

// Category `name` stays English — passed as route query param
// `labelKey` is used for translated display
const categories = [
  { name: 'Service Quality',    labelKey: 'serviceQuality',     icon: ServiceQualityIcon,    color: 'bg-[#E74C3C]' },
  { name: 'Interface Design',   labelKey: 'interfaceDesign',    icon: InterfaceDesignIcon,   color: 'bg-[#F16C14]' },
  { name: 'System Speed',       labelKey: 'systemSpeed',        icon: SystemSpeedIcon,       color: 'bg-[#E69500]' },
  { name: 'Accessibility',      labelKey: 'accessibility',      icon: AccessibilityIcon,     color: 'bg-[#13B3A1]' },
  { name: 'General Experience', labelKey: 'generalExperience',  icon: GeneralExperienceIcon, color: 'bg-[#2C67E7]' },
]

const goToRating = (category) => {
  router.push({ path: '/rating/', query: { category } })
}

const goBack = () => {
  router.push({ path: 'home' })
}
</script>

<template>
  <div class="flex flex-col items-center w-full h-full">
    <div class="flex items-center w-full mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div class="flex flex-col text-left">
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('yourFeedbackMatters') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('selectAreaFeedback') }}</p>
      </div>
    </div>

    <div class="text-center mt-2 mb-6 w-full">
      <h2 class="text-[42px] text-[#03335C] font-bold leading-none">{{ t('whatWouldYouLikeToRate') }}</h2>
    </div>

    <div class="flex flex-col items-center w-full flex-1">
      <div class="mt-[22px] flex w-full flex-wrap justify-between gap-3">
        <div 
          v-for="item in categories" 
          :key="item.name"
          @click="goToRating(item.name)"
          :class="[
            'flex h-[220px] min-w-[160px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 active:scale-[0.97]',
            item.color
          ]"
        >
          <img 
            :src="item.icon" 
            :alt="item.name" 
            class="mb-[5px] h-[105px] w-[105px] brightness-0 invert" 
          />
          <p 
            class="m-0 flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white" 
            v-html="t(item.labelKey).replace(' ', '<br>')"
          ></p>
        </div>
      </div>
    </div>
  </div>
</template>