<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const isParent = () => !route.params.docType

const documents = [
  { name: 'Barangay Clearance', type: 'barangay-clearance', fee: 50 },
  { name: 'Cedula', type: 'cedula', fee: 50 },
  { name: 'Certificate of Indigency', type: 'indigency', fee: 100 },
  { name: 'Barangay ID  ', type: 'barangay-id', fee: 30 },
]
</script>

<template>
  <div>
    <div v-if="isParent()" class="max-w-6xl mx-auto">
      <h1 class="text-[45px] text-[#03335C] font-bold text-center -mb-2 tracking-tight">Document Services</h1>
      <p class="text-center text-[#03335C] mb-9">
        Select and apply for barangay documents
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <router-link
          v-for="doc in documents"
          :key="doc.type"
          :to="`/document-services/${doc.type}`"
          class="group block p-6 rounded-2xl border border-gray-300 shadow-md bg-white 
                 hover:bg-[#003A6B] hover:text-white transition-all duration-300 ease-in-out"
        >
          <h2 class="text-[30px] text-[#003A6B] font-bold mb-2 group-hover:text-white
          transition-all duration-300 ease-in-out">
            {{ doc.name }}
          </h2>
          <p class="text-gray-500 group-hover:text-gray-100 text-sm mb-4
                    transition-all duration-300 ease-in-out">
            Select what type of {{ doc.name.toLowerCase() }} you'd like to get
          </p>

          <!-- Fee row (updated only this part) -->
          <div class="flex justify-between items-center font-semibold text-[#003A6B] group-hover:text-white
                      transition-all duration-300 ease-in-out">
            <span>Fee:</span>
            <span>₱{{ doc.fee }}</span>
          </div>
        </router-link>
      </div>
    </div>

    <router-view v-else />
  </div>
</template>
