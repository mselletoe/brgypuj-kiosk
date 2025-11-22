<script setup>
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

const router = useRouter()

const goToRating = (category) => {
  router.push({ path: '/rating/', query: { category: category } })
}

const goBack = () => {
  router.push({ path: 'home' })
}
</script>

<template>
  <div class="feedback-layout">
    <div class="header-section">
      <ArrowBackButton @click="goBack" class="manual-back-btn" />
      <h1 class="title-text">Your Feedback Matters</h1>
    </div>

    <div class="sub-header">
      <h2 class="new-title-text">What would you like to rate?</h2>
      <p class="subtitle-text">Select the area you'd like to share your thoughts on</p>
    </div>

    <div class="container-wrapper">
      <div class="feedback-box" @click="goToRating('Service Quality')">
        <img src="@/assets/vectors/ServiceQuality.svg" alt="Service Quality" class="box-logo" />
        <p class="box-title">Service<br>Quality</p>
      </div>
      <div class="feedback-box" @click="goToRating('Interface Design')">
        <img src="@/assets/vectors/InterfaceDesign.svg" alt="Interface Design" class="box-logo" />
        <p class="box-title">Interface Design</p>
      </div>
      <div class="feedback-box" @click="goToRating('System Speed')">
        <img src="@/assets/vectors/SystemSpeed.svg" alt="System Speed" class="box-logo" />
        <p class="box-title">System<br>Speed</p>
      </div>
      <div class="feedback-box" @click="goToRating('Accessibility')">
        <img src="@/assets/vectors/Accessibility.svg" alt="Accessibility" class="box-logo" />
        <p class="box-title">Accessibility</p>
      </div>
      <div class="feedback-box" @click="goToRating('General Experience')">
        <img src="@/assets/vectors/GeneralExperience.svg" alt="General Experience" class="box-logo" />
        <p class="box-title">General Experience</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feedback-layout { position: fixed; top: 0; left: 0; display: flex; flex-direction: column; width: 100%; height: 100vh; overflow: hidden !important; background-color: #ffffff; font-family: 'Poppins'; color: #003a6b; box-sizing: border-box; padding: 2rem; -ms-overflow-style: none; scrollbar-width: none; }
.feedback-layout::-webkit-scrollbar { display: none; }

.header-section { display: flex; align-items: center; width: 100%; gap: 1.5rem; margin-bottom: 1rem; }
.title-text { font-size: 45px; font-weight: 700; line-height: 1; letter-spacing: -0.03em; color: #03335C; margin-top: 73px; margin-bottom: 44px; margin-left: 105px;}
.new-title-text { font-size: 30px; font-weight: 700; line-height: 35px; letter-spacing: -0.03em; color: #003a6b; margin: 0 0 8px 0; text-align: center; width: 100%; }
.subtitle-text { font-size: 13px; text-align: center; margin-bottom: 17px; color: #003a6b; font-weight: 500; max-width: 100%; }
.sub-header { display: flex; flex-direction: column; align-items: center; width: 100%; margin-bottom: 22px; }
.container-wrapper { display: flex; gap: 17.6px; justify-content: center; flex-wrap: wrap; width: 100%; max-width: 900px; margin: 0 auto; }
.feedback-box { width: 165px; height: 220px; border-radius: 15px; background-color: #246195; box-shadow: inset 2px 2px 4px rgba(255,255,255,0.6), inset -2px -2px 6px rgba(0,0,0,0.15), 4px 4px 8px rgba(0,0,0,0.25); transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer; display: flex; flex-direction: column; justify-content: space-evenly; align-items: center; text-align: center; padding: 10px; box-sizing: border-box; }
.feedback-box:hover { transform: scale(1.05) translateY(-3px); box-shadow: inset 2px 2px 4px rgba(255, 255, 255, 0.7), inset -2px -2px 6px rgba(0, 0, 0, 0.2), 6px 6px 12px rgba(0, 0, 0, 0.35); }
.box-logo { width: 80px; height: 80px; margin-bottom: 5px; }
.box-title { font-family: 'Poppins'; font-weight: 700; font-size: 20px; line-height: 20px; letter-spacing: 0; color: #ffffff; margin: 0; }
.manual-back-btn { position: absolute; top: 98px; left: 64px; z-index: 50; }
</style>