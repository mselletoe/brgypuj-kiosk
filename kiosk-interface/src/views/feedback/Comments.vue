<template>
  <div class="feedback-layout">
    <h1 class="title-text">Share Your Thoughts</h1>
    <p class="subtitle-text">{{ correctedSubtitle }}</p>

    <div class="rating-display-wrapper">
        <h2 class="new-title-prefix">Your Rating: </h2>
        <template v-for="n in Number(starCount)" :key="n">
          <img :src="yellowStarSvg" alt="Yellow Star" class="yellow-star-icon" />
        </template>
        <h2 class="new-title-text" :style="{ color: ratingTextColor }">{{ ratingText }}</h2>
    </div>

    <div class="additional-title-wrapper">
      <img :src="commentSvg" alt="Comment Icon" class="comment-icon" />
      <h3 class="additional-title-text">Additional Comments (Optional)</h3>
    </div>
    
    <textarea 
      class="comments-input" 
      placeholder="Share any specific suggestions, compliments, and concerns..."
    ></textarea>

    <div class="buttons-container">
      <button class="back-button" @click="goBackToRating">Back to Rating</button>
      <button class="submit-button" @click="showModal">Submit Feedback</button>
    </div>

    <div v-if="isModalVisible" class="modal-overlay">
      <Modal
        title="Feedback Submitted!"
        message="Thank you for taking the time to share your thoughts with us."
        :showNewRequest="false" 
        doneText="Done"
        @done="closeModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import commentSvg from '@/assets/vectors/Comment.svg?url' 
import yellowStarSvg from '@/assets/vectors/YellowStar.svg?url'
// 1. Import your shared Modal component
import Modal from '@/components/shared/Modal.vue'

const route = useRoute()
const router = useRouter()
const starCount = ref(0)
const ratingText = ref('')
const experienceCategory = ref('general')

// 2. Add state and functions to control the modal
const isModalVisible = ref(false)

const showModal = () => {
  isModalVisible.value = true
}

const closeModal = () => {
  isModalVisible.value = false
  // Optional: you can redirect the user after they click "Done"
  router.push({ path: 'feedback' })
}

onMounted(() => {
  if (route.query.stars) {
    starCount.value = Number(route.query.stars)
  }
  if (route.query.ratingText) {
    ratingText.value = route.query.ratingText
  }
  if (route.query.category) {
    experienceCategory.value = route.query.category
  }
})

const correctedSubtitle = computed(() => {
    const category = experienceCategory.value
    const phrase = ' Experience'
    const fullPrefix = 'Tell us more about your '
    
    if (category.toLowerCase().endsWith('experience')) {
        return fullPrefix + category
    } else {
        return fullPrefix + category + phrase
    }
})

const ratingTextColor = computed(() => {
    switch (starCount.value) {
        case 1:
            return '#CF1331'
        case 2:
            return '#D36F28'
        case 3:
            return '#FFCE0A'
        case 4:
            return '#97B13B'
        case 5:
            return '#21C05C'
        default:
            return '#003a6b'
    }
})

const goBackToRating = () => {
    router.go(-1)
}
</script>

<style scoped>
/* --- RESPONSIVE LAYOUT CHANGES --- */
.feedback-layout{
  display:flex;
  flex-direction:column;
  align-items:center;
  width:100%;
  min-height:100vh; /* Added for vertical height */
  overflow-y:auto; /* Added for scrolling */
  overflow-x:hidden;
  background-color:#ffffff;
  font-family:'Poppins';
  color:#003a6b;
  box-sizing:border-box;
  padding: 20px; /* Adjusted padding */
}
/* --- END OF LAYOUT CHANGES --- */

.title-text{font-size:40px;font-weight:700;line-height:50px;letter-spacing:-0.03em;color:#003a6b;text-shadow:3px 3px 5px rgba(0,0,0,0.3),-2px -2px 4px rgba(255,255,255,0.6);margin:0 0 3px 0;text-align:center;width:auto;max-width:100%;}
.subtitle-text{font-size:13px;text-align:center;margin-bottom:10px;color:#003a6b;font-weight:500;max-width:100%;}

.rating-display-wrapper {display: flex;align-items: center;justify-content: center;margin-bottom: 23px;width: 100%; flex-wrap: wrap;} /* Added flex-wrap */
.new-title-prefix {font-size:13px;margin:0 5px 0 0;color:#003a6b;font-weight:bold;white-space: nowrap;}
.new-title-text{font-size:13px;margin:0 0 0 5px;font-weight:bold;max-width:100%;}
.yellow-star-icon {width: 22px;height: 22px;margin: 0 1px;}

/* --- RESPONSIVE CONTENT ALIGNMENT --- */
.additional-title-wrapper {
  display: flex;
  align-items: center;
  width: 100%; /* Changed from 816px */
  max-width: 816px; /* Added max-width */
  margin-bottom: 10px; /* Simplified margin */
}

.comment-icon {
  width: 24px;
  height: 24px;
  margin-right: 5px;
  /* margin-left: 20px; */ /* Removed margin-left */
}
.additional-title-text{font-size: 13px;margin: 0;text-align: left;color: #003a6b;font-weight: bold;}

.comments-input {
  width: 100%; /* Changed from 816px */
  max-width: 816px; /* Added max-width */
  height: 200px;
  background-color: #FFFFFF;
  border: 2px solid #003A6B;
  border-radius: 10px;
  box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
  font-family: 'Poppins';
  font-size: 13px;
  font-weight: regular;
  color: #003a6b;
  padding: 15px;
  resize: none;
  outline: none;
  flex-shrink: 0; 
  margin-bottom: 30px;
  box-sizing: border-box; /* Added for consistent padding behavior */
}
.comments-input::placeholder {color: #003a6b; opacity: 1; }

.buttons-container {
  display: flex;
  justify-content: space-between;
  width: 100%; /* Changed from 816px */
  max-width: 816px; /* Added max-width */
}
/* --- END OF RESPONSIVE ALIGNMENT --- */

.back-button, .submit-button {height: 40px;padding: 0 25px;border-radius: 10px;box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);font-family: 'Poppins';font-size: 16px;font-weight: 600;cursor: pointer;transition: background-color 0.2s, color 0.2s, border-color 0.2s;}
.back-button {background-color: #FFFFFF;border: 1px solid #003A6B;color: #003A6B;}
.back-button:hover {background-color: #f0f0f0;}

.submit-button {background-color: #003A6B;border: 1px solid #003A6B;color: #FFFFFF;}
.submit-button:hover {background-color: #002a4b;}

/* --- THIS IS THE NEW CSS FOR THE MODAL --- */
.modal-overlay {
  position: fixed; /* Stays in place relative to the viewport */
  top: 0;
  left: 0;
  width: 100vw; /* Full viewport width */
  height: 100vh; /* Full viewport height */
  background-color: rgba(0, 0, 0, 0.4); /* Semi-transparent black background */
  display: flex;
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  z-index: 1000; /* Ensures it's on top of all other content */
}
</style>