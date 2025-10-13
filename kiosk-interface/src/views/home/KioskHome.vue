<template>
  <div class="flex flex-col items-center justify-center h-screen bg-blue-200 space-y-8">
    <h1 class="text-4xl font-bold text-gray-800 mb-8">
      Welcome, Guest! This is the Kiosk Home 🏠
    </h1>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-3xl">
      <button
        @click="goTo('document-services')"
        class="bg-white text-blue-700 font-semibold py-6 px-8 rounded-2xl shadow-lg hover:bg-blue-100 transition"
      >
        📄 Document Services
      </button>

      <button
        @click="goTo('equipment-borrowing')"
        class="bg-white text-blue-700 font-semibold py-6 px-8 rounded-2xl shadow-lg hover:bg-blue-100 transition"
      >
        ⚙️ Equipment Borrowing
      </button>

      <button
        @click="goTo('appointments')"
        class="bg-white text-blue-700 font-semibold py-6 px-8 rounded-2xl shadow-lg hover:bg-blue-100 transition"
      >
        📅 Schedule Appointment
      </button>

      <button
        @click="goTo('help-and-support')"
        class="bg-white text-blue-700 font-semibold py-6 px-8 rounded-2xl shadow-lg hover:bg-blue-100 transition"
      >
        🆘 Help & Support
      </button>

      <button
        @click="goTo('feedback')"
        class="bg-white text-blue-700 font-semibold py-6 px-8 rounded-2xl shadow-lg hover:bg-blue-100 transition"
      >
        💬 Feedback
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goTo = (path) => {
  router.push(`/${path}`)
}
</script>

<style scoped>
button {
  font-size: 1.2rem;
}
</style>