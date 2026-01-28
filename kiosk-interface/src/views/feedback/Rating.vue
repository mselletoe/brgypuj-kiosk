<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import StarIcon from '@/assets/vectors/Star.svg'

const route = useRoute()
const router = useRouter()
const feedbackCategory = ref('')

const ratings = [
  { stars: 1, text: 'Very Poor', color: '#3F4B55' },
  { stars: 2, text: 'Poor', color: '#475F73' },
  { stars: 3, text: 'Average', color: '#246195' },
  { stars: 4, text: 'Good', color: '#1574C3' },
  { stars: 5, text: 'Excellent', color: '#008AFF' },
]

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
  <div class="flex flex-col w-full h-full">
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Your Feedback Matters</h1>
        <p class="text-[#03335C] -mt-2">Tell us more about your choice</p>
      </div>
    </div>

    <div class="text-center mb-12">
      <h2 class="text-[42px] text-[#03335C] font-bold leading-none">
        Rate our {{ feedbackCategory }}
      </h2>
      <p class="text-[20px] text-[#03335C] italic font-medium mt-2">
        Tap a star to rate your experience
      </p>
    </div>

    <div class="flex justify-center gap-5 px-6">
      <div 
        v-for="rating in ratings" 
        :key="rating.stars"
        @click="handleRatingClick(rating.stars, rating.text)"
        class="flex flex-col items-center justify-center flex-1 aspect-[4/5] rounded-[25px] cursor-pointer transition-all active:scale-95 shadow-xl p-4"
        :style="{ backgroundColor: rating.color }"
      >
        <img 
          :src="StarIcon" 
          :alt="rating.text" 
          class="w-1/2 mb-6 filter drop-shadow-lg" 
        />
        <p class="text-white text-[24px] font-bold text-center leading-tight">
          {{ rating.text }}
        </p>
      </div>
    </div>
  </div>
</template>