<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import StarIcon from '@/assets/vectors/Star.svg'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const feedbackCategory = ref('')

// Applied a vibrant, semantic color scale that bridges with your KioskHome palette
const ratingKeys = ['veryPoor', 'poor', 'average', 'good', 'excellent']
const ratingColors = ['#E74C3C', '#F16C14', '#E69500', '#13B3A1', '#2C67E7']
// ratings is computed so text updates reactively on locale change
const ratings = computed(() =>
  ratingKeys.map((key, i) => ({
    stars: i + 1,
    text: t(key),
    color: ratingColors[i],
  }))
)

onMounted(() => {
  feedbackCategory.value = route.query.category || 'Experience'
})

const handleRatingClick = (stars, text) => {
  router.push({
    path: '/comments',
    query: { 
      stars, 
      ratingText: text, 
      category: feedbackCategory.value 
    }
  })
}

const goBack = () => {
  router.push({ path: '/feedback' })
}
</script>

<template>
  <div class="flex flex-col items-center w-full h-full">
    <div class="flex items-center w-full mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div class="flex flex-col text-left">
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('yourFeedbackMatters') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('tapStarRate') }}</p>
      </div>
    </div>

    <div class="text-center mt-2 mb-6 w-full">
      <h2 class="text-[42px] text-[#03335C] font-bold leading-none">
        {{ t('rateOur', { category: feedbackCategory }) }}
      </h2>
    </div>

    <div class="flex flex-col items-center w-full flex-1">
      <div class="mt-[22px] flex w-full flex-wrap justify-between gap-3">
        <div 
          v-for="rating in ratings" 
          :key="rating.stars"
          @click="handleRatingClick(rating.stars, rating.text)"
          class="flex h-[220px] min-w-[160px] flex-1 cursor-pointer flex-col items-center justify-center rounded-[15px] p-[10px] text-center shadow-[4px_4px_8px_rgba(0,0,0,0.25),inset_2px_2px_4px_rgba(255,255,255,0.6),inset_-2px_-2px_6px_rgba(0,0,0,0.15)] transition-all duration-150 active:scale-[0.97]"
          :style="{ backgroundColor: rating.color }"
        >
          <img 
            :src="StarIcon" 
            :alt="rating.text" 
            class="mb-[5px] h-[105px] w-[105px] filter drop-shadow-lg" 
          />
          <p class="m-0 flex h-[40px] items-center justify-center text-[17px] font-bold leading-[20px] text-white drop-shadow-md">
            {{ rating.text }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>