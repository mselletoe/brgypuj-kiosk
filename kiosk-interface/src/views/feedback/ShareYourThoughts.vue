<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// Finish feedback and redirect (e.g., home or idle)
const finish = () => {
  router.push('/') // kung saan mo dalhen
}

// Optional: go back to rating
const goBack = () => {
  router.push('/feedback/rating')
}
</script>

<template>
  <!-- Step 3 content goes here -->
</template>