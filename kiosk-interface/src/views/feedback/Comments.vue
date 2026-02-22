<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import commentSvg from '@/assets/vectors/Comment.svg?url' 
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'
import yellowStarSvg from '@/assets/vectors/YellowStar.svg?url'
import Modal from '@/components/shared/Modal.vue'
import { submitFeedback } from '@/api/feedbackService'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const starCount = ref(0)
const ratingText = ref('')
const experienceCategory = ref('general')
const additionalComments = ref('')
const isSubmitting = ref(false)

const isModalVisible = ref(false)

const closeModal = () => {
  isModalVisible.value = false
  router.push({ path: '/feedback' })
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

const ratingTextColor = computed(() => {
    switch (starCount.value) {
        case 1: return '#CF1331'
        case 2: return '#D36F28'
        case 3: return '#FFCE0A'
        case 4: return '#97B13B'
        case 5: return '#21C05C'
        default: return '#003a6b'
    }
})

const goBackToRating = () => {
  router.push({ path: '/rating', query: { category: experienceCategory.value } })
}

const handleCancel = () => {
  router.push({ path: '/feedback' })
}

const handleSubmit = async () => {
  if (isSubmitting.value) return

  isSubmitting.value = true

  try {
    const residentId = authStore.residentId

    const payload = {
      resident_id: residentId,
      category: experienceCategory.value,
      rating: starCount.value,
      additional_comments: additionalComments.value || null
    }

    await submitFeedback(payload)
    
    isModalVisible.value = true
  } catch (error) {
    console.error('Failed to submit feedback:', error)
    alert('Failed to submit feedback. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBackToRating"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Share Your Thoughts</h1>
        <p class="text-[#03335C] -mt-2">Tell us more about your experience</p>
      </div>
    </div>

    <!-- Main -->
    <div class="flex-1">
      <!-- Rating display -->
      <div class="flex flex-wrap items-center justify-center w-full mb-[23px] text-xl">
        <h2 class="font-bold mr-[5px] whitespace-nowrap">
          Your Rating:
        </h2>

        <template v-for="n in Number(starCount)" :key="n">
          <img
            :src="yellowStarSvg"
            alt="Yellow Star"
            class="w-[22px] h-[22px] mx-[1px]"
          />
        </template>

        <h2
          class="font-bold ml-[5px]"
          :style="{ color: ratingTextColor }"
        >
          {{ ratingText }}
        </h2>
      </div>

      <!-- Additional comments title -->
      <div class="flex items-center w-full mb-2">
        <img
          :src="commentSvg"
          alt="Comment Icon"
          class="w-6 h-6 mr-[5px]"
        />
        <h3 class="text-[13px] font-bold text-left text-[#003a6b]">
          Additional Comments (Optional)
        </h3>
      </div>

      <!-- Textarea -->
      <textarea
        v-model="additionalComments"
        class="w-full h-[200px] p-[15px]
              bg-white text-[13px] text-[#003a6b]
              border-2 border-[#003a6b] rounded-[10px]
              shadow-[3px_3px_6px_rgba(0,0,0,0.2)]
              resize-none outline-none box-border
              placeholder:text-[#003a6b]"
        placeholder="Share any specific suggestions, compliments, and concerns..."
      ></textarea>
    </div>

    <!-- Buttons -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        variant="outline"
        @click="handleCancel"
        :disabled="isSubmitting"
      >
        Cancel
      </Button>
      <Button
        variant="secondary"
        @click="handleSubmit"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit' }}
      </Button>
    </div>

    <!-- Modals -->
    <div
      v-if="isModalVisible"
      class="fixed inset-0 z-[1000]
            flex items-center justify-center
            bg-black/40"
    >
      <Modal
        title="Feedback Submitted!"
        message="Thank you for taking the time to share your thoughts with us."
        :showSecondaryButton="false"
        primaryButtonText="Done"
        @primary-click="closeModal"
      />
    </div>
  </div>
</template>
