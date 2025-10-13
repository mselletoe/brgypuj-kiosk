<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Request Submitted!' },
  message: {
    type: String,
    default: 'Your borrowing request has been submitted for approval. Pay the fee at the counter and you will be contacted for pickup details.'
  },
  showNewRequest: { type: Boolean, default: true },
  newRequestText: { type: String, default: 'New Request' },
  doneText: { type: String, default: 'Done' }
})

const emit = defineEmits(['done'])

const handleDone = () => {
  emit('done')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full">
    <!-- Modal Container -->
    <div
      class="bg-white shadow-lg rounded-2xl p-10 text-center w-[75%]
              border border-[#C1C1C1] border-[2px]"
    >
      <!-- Icon -->
      <div class="flex justify-center mb-6">
        <div class="w-[80px] h-[80px] rounded-full bg-[#E4F5FC] flex items-center justify-center">
          <div class="w-[65px] h-[65px] rounded-full border-[4px] border-[#1B5886] flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-10 h-10 text-[#1B5886]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Title -->
      <h1 class="text-[30px] font-extrabold tracking-tight text-[#1B5886] mb-3">
        {{ title }}
      </h1>

      <!-- Description --> 
      <p class="text-[#003A6B] mb-8">
        {{ message }}
      </p>

      <!-- Buttons -->
      <div class="flex justify-center gap-4">
        <button
          v-if="showNewRequest"
          class="px-7 py-3 rounded-xl bg-[#BBC3CE] text-[white] font-semibold shadow-md cursor-not-allowed"
          disabled
        >
          {{ newRequestText }}
        </button>

        <button
          @click="handleDone"
          class="px-12 py-3 rounded-xl border-2 border-[#1B5886] text-[#1B5886] font-semibold shadow-md
                 hover:bg-[#1B5886] hover:text-white transition-colors duration-300 ease-in-out"
        >
          {{ doneText }}
        </button>
      </div>
    </div>
  </div>
</template>