<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

const route = useRoute()
const router = useRouter()
const feedbackCategory = ref('')

onMounted(() => {
  if (route.query.category) {
    feedbackCategory.value = route.query.category
  } else {
    feedbackCategory.value = 'Experience'
  }
})

const handleRatingClick = (stars, text) => {
  router.push({
    path: '/comments',
    query: { 
      stars: stars,
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
  <div class="feedback-layout">
    <div class="header-section">
      <ArrowBackButton @click="goBack" class="manual-back-btn" />
      <h1 class="title-text">Your Feedback Matters</h1>
    </div>

    <div class="sub-header">
      <h2 class="new-title-text">Rate our {{ feedbackCategory }}</h2>
      <p class="subtitle-text">Tap a star to rate your experience</p>
    </div>

    <div class="container-wrapper">
      <div class="feedback-box" @click="handleRatingClick(1, 'Very Poor')">
        <img src="@/assets/vectors/Star.svg" alt="Very Poor" class="box-logo" />
        <p class="box-title">Very Poor</p>
      </div>
      <div class="feedback-box" @click="handleRatingClick(2, 'Poor')">
        <img src="@/assets/vectors/Star.svg" alt="Poor" class="box-logo" />
        <p class="box-title">Poor</p>
      </div>
      <div class="feedback-box" @click="handleRatingClick(3, 'Average')">
        <img src="@/assets/vectors/Star.svg" alt="Average" class="box-logo" />
        <p class="box-title">Average</p>
      </div>
      <div class="feedback-box" @click="handleRatingClick(4, 'Good')">
        <img src="@/assets/vectors/Star.svg" alt="Good" class="box-logo" />
        <p class="box-title">Good</p>
      </div>
      <div class="feedback-box" @click="handleRatingClick(5, 'Excellent')">
        <img src="@/assets/vectors/Star.svg" alt="Excellent" class="box-logo" />
        <p class="box-title">Excellent</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* LAYOUT: Fixed position, Padding top to clear header, No Scrollbar */
.feedback-layout { position: fixed; top: 0; left: 0; display: flex; flex-direction: column; width: 100%; height: 100vh; overflow: hidden !important; background-color: #ffffff; font-family: 'Poppins'; color: #003a6b; box-sizing: border-box; padding: 160px 2rem 2rem 2rem; -ms-overflow-style: none; scrollbar-width: none; }
.feedback-layout::-webkit-scrollbar { display: none; }

.header-section { display: flex; align-items: center; width: 100%; gap: 1.5rem; margin-bottom: 1rem; }

/* TITLE: Aligned with margin-left to match your Feedback.vue style */
.title-text { font-size: 45px; font-weight: 700; line-height: 1; letter-spacing: -0.03em; color: #03335C; margin-top: -55px; margin-bottom: 44px; margin-left: 105px; }

/* SUBTITLES */
.new-title-text { font-size: 30px; font-weight: 700; line-height: 35px; letter-spacing: -0.03em; color: #003a6b; margin: 0 0 8px 0; text-align: center; width: 100%; }
.subtitle-text { font-size: 13px; text-align: center; margin-bottom: 17px; color: #003a6b; font-weight: 500; max-width: 100%; }
.sub-header { display: flex; flex-direction: column; align-items: center; width: 100%; margin-bottom: 22px; }

/* BOXES */
.container-wrapper { display: flex; gap: 17.6px; justify-content: center; flex-wrap: wrap; width: 100%; max-width: 900px; margin: 0 auto; }
.feedback-box { width: 165px; height: 220px; border-radius: 15px; box-shadow: inset 2px 2px 4px rgba(255,255,255,0.6), inset -2px -2px 6px rgba(0,0,0,0.15), 4px 4px 8px rgba(0,0,0,0.25); transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer; display: flex; flex-direction: column; justify-content: space-evenly; align-items: center; text-align: center; padding: 10px; box-sizing: border-box; }
.feedback-box:hover { transform: scale(1.05) translateY(-3px); box-shadow: inset 2px 2px 4px rgba(255, 255, 255, 0.7), inset -2px -2px 6px rgba(0, 0, 0, 0.2), 6px 6px 12px rgba(0, 0, 0, 0.35); }
.box-logo { width: 100px; height: 100px; margin-bottom: 5px; filter: drop-shadow(4px 4px 5px rgba(0, 0, 0, 0.4)); }
.box-title { font-family: 'Poppins'; font-weight: 700; font-size: 20px; line-height: 20px; letter-spacing: 0; color: #ffffff; margin: 0; }

/* COLORS */
.container-wrapper .feedback-box:nth-child(1) { background-color: #3F4B55; }
.container-wrapper .feedback-box:nth-child(2) { background-color: #475F73; }
.container-wrapper .feedback-box:nth-child(3) { background-color: #246195; }
.container-wrapper .feedback-box:nth-child(4) { background-color: #1574C3; }
.container-wrapper .feedback-box:nth-child(5) { background-color: #008AFF; }

/* MANUAL BUTTON: Edit top/left here to match your Feedback.vue exactly */
.manual-back-btn { position: absolute; top: 98px; left: 64px; z-index: 50; }
</style>