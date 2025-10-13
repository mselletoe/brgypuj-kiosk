<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// Navigate to the rating screen
const goToNextStep = () => {
  router.push('/feedback/rating')
}
</script>

<template>
  <!-- Step 1 content goes here -->
</template>