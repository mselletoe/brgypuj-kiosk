<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: String, // 'document' or 'equipment'
  reference: String,
  title: String,
  createdAt: String,
  status: String // 'completed' or 'rejected'
})

const isDocument = computed(() => props.type === 'document')

const sideColor = computed(() =>
  isDocument.value ? '#2C67E7' : '#F97316'
)

const iconBg = computed(() =>
  isDocument.value ? '#E4F5FF' : '#FFEDD5'
)

const iconColor = computed(() =>
  isDocument.value ? '#2C67E7' : '#F97316'
)

const statusBg = computed(() =>
  props.status === 'completed' ? '#16A34A' : '#EF4444'
)

const statusText = computed(() =>
  props.status === 'completed' ? 'Completed' : 'Rejected'
)
</script>

<template>
  <div class="flex w-full rounded-2xl shadow-sm overflow-hidden border-[3px]"
  :style="{ borderColor: sideColor }" >

    <!-- LEFT SOLID COLOR STRIP -->
    <div
      class="w-3"
      :style="{ backgroundColor: sideColor }"
    ></div>

    <!-- MAIN CONTENT -->
    <div class="flex items-center justify-between w-full px-6 py-4"
         :style="{ borderColor: sideColor }">

      <!-- LEFT CONTENT -->
      <div class="flex items-center gap-5">

        <!-- ICON -->
        <div
          class="flex items-center justify-center w-14 h-14 rounded-full"
          :style="{ backgroundColor: iconBg }"
        >
          <!-- Document Icon -->
          <svg
            v-if="isDocument"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.8"
            stroke="currentColor"
            class="w-7 h-7"
            :style="{ color: iconColor }"
          >
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M7.5 3h6l3 3v13.5A1.5 1.5 0 0 1 15 21h-7.5A1.5 1.5 0 0 1 6 19.5V4.5A1.5 1.5 0 0 1 7.5 3z" />
          </svg>

          <!-- Equipment Icon -->
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.8"
            stroke="currentColor"
            class="w-7 h-7"
            :style="{ color: iconColor }"
          >
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 3v2m0 14v2m7-9h2M3 12H1m15.364-6.364l1.414-1.414M4.222 19.778l-1.414 1.414m0-16.97l1.414 1.414M19.778 19.778l1.414 1.414M12 7a5 5 0 100 10 5 5 0 000-10z" />
          </svg>
        </div>

        <!-- TEXT -->
        <div class="flex flex-col">
          <h2 class="text-lg font-bold text-[#003A6B]">
            {{ reference }}
          </h2>

          <p class="text-sm text-[#003A6B] font-medium italic">
            {{ title }}
          </p>
        </div>
      </div>

      <!-- RIGHT SIDE -->
      <div class="flex items-center gap-10">

        <p class="text-sm text-[#003A6B]">
          Created on: {{ createdAt }}
        </p>

        <div
          class="flex items-center justify-center px-5 py-1.5 rounded-full text-white text-sm font-semibold"
          :style="{ backgroundColor: statusBg }"
        >
          {{ statusText }}
        </div>

      </div>

    </div>
  </div>
</template>
