<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// Navigate to additional comments screen
const goToNextStep = () => {
  router.push('/feedback/comments')
}

// Optional: go back to category selection
const goBack = () => {
  router.push('/feedback/select')
}
</script>

<template>
  <!-- Step 2 content goes here -->
</template>