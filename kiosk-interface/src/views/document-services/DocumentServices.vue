<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const isParent = () => !route.params.docType

const documents = [
  { name: 'Barangay Certificate', type: 'barangay-certificate', icon: '📄' },
  { name: 'Barangay ID', type: 'barangay-id', icon: '🪪' },
  { name: 'Cedula', type: 'cedula', icon: '📋' },
  { name: 'Certificate of Indigency', type: 'certificate-indigency', icon: '📃' },
  { name: 'Business Permit', type: 'business-permit', icon: '💼' },
]
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto">
    <!-- Document list -->
    <div v-if="isParent()">
      <h1 class="text-3xl font-bold mb-6">Request a Document</h1>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <router-link
          v-for="doc in documents"
          :key="doc.type"
          :to="`/document-services/${doc.type}`"
          class="bg-blue-600 text-white font-semibold py-8 rounded-lg shadow hover:bg-blue-700 transition flex flex-col justify-center items-center gap-3"
        >
          <span class="text-5xl">{{ doc.icon }}</span>
          <span class="text-lg">{{ doc.name }}</span>
        </router-link>
      </div>
    </div>

    <!-- Render form wrapper for child routes -->
    <router-view v-else />
  </div>
</template>