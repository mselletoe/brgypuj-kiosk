<template>
  <div class="feedback-layout">
    <ArrowBackButton 
      @click="goBack"
      class="absolute top-0 left-6" 
    />
    <h1 class="title-text">Your Feedback Matters</h1>
    <h2 class="new-title-text">What would you like to rate?</h2>
    <p class="subtitle-text">Select the area you'd like to share your thoughts on</p>
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

<style scoped>
.feedback-layout{position:relative;display:flex;flex-direction:column;align-items:center;width:100%;height:100%;overflow:hidden;background-color:#ffffff;font-family:'Poppins';color:#003a6b;box-sizing:border-box;padding:0px 20px 20px 20px;}
.absolute{position:absolute;}
.top-6{top:1.5rem;}
.left-6{left:1.5rem;}
.title-text{font-size:45px;font-weight:700;line-height:50px;letter-spacing:-0.03em;color:#03335C;text-shadow:3px 3px 5px rgba(0,0,0,0.3),-2px -2px 4px rgba(255,255,255,0.6);margin:3px auto 50px 75px;text-align:left;width:auto;max-width:100%;}
.new-title-text{font-size:30px;font-weight:700;line-height:35px;letter-spacing:-0.03em;color:#003a6b;text-shadow:3px 3px 5px rgba(0,0,0,0.3),-2px -2px 4px rgba(255,255,255,0.6);margin:5px 0 5px 0;text-align:center;width:100%;}
.subtitle-text{font-size:13px;text-align:center;margin-bottom:23px;color:#003a6b;font-weight:500;max-width:100%;}
.container-wrapper{display:flex;gap:10px;justify-content:flex-start;flex-wrap:nowrap;width:869px;align-self:center;margin-top:15px;}
.feedback-box{width:165px;height:220px;border-radius:15px;background-color:#246195;box-shadow:inset 2px 2px 4px rgba(255,255,255,0.6),inset -2px -2px 6px rgba(0,0,0,0.15),4px 4px 8px rgba(0,0,0,0.25);transition:transform 0.15s ease,box-shadow 0.15s ease;cursor:pointer;flex-shrink:0;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;text-align:center;padding:10px;box-sizing:border-box;}
.feedback-box:hover{transform: scale(1.05) translateY(-3px); box-shadow: inset 2px 2px 4px rgba(255, 255, 255, 0.7), inset -2px -2px 6px rgba(0, 0, 0, 0.2), 6px 6px 12px rgba(0, 0, 0, 0.35);}
.box-logo{width:80px;height:80px;margin-bottom:5px;}
.box-title{font-family:'Poppins';font-weight:700;font-size:20px;line-height:20px;letter-spacing:0;color:#ffffff;margin:0;}
</style>