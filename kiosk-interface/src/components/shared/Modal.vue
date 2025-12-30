<script setup>
import PrimaryButton from '@/components/shared/Button.vue'

const props = defineProps({
  title: { type: String, default: 'Modal Title' },
  message: { 
    type: String,
    default: 'Modal message goes here. This is a sample message to demonstrate the modal component.'
  },
  referenceId: { type: String, default: '' },
  showReferenceId: { type: Boolean, default: false },
  showPrimaryButton: { type: Boolean, default: true },
  showSecondaryButton: { type: Boolean, default: true },
  primaryButtonText: { type: String, default: 'Yes' },
  secondaryButtonText: { type: String, default: 'No' }
})

const emit = defineEmits(['primary-click', 'secondary-click'])

const handlePrimaryClick = () => {
  emit('primary-click')
}

const handleSecondaryClick = () => {
  emit('secondary-click')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full">
    <div
      class="bg-white shadow-lg rounded-2xl p-10 text-center w-[75%]
              border-[#C1C1C1] border-[2px]"
    >
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

      <h1 class="text-[30px] font-extrabold tracking-tight text-[#1B5886] mb-3">
        {{ title }}
      </h1>

      <p class="text-[#003A6B] mb-6 text-[15px]">
        {{ message }}
      </p>

      <!-- Reference ID Box -->
      <div v-if="showReferenceId" class="mb-8 flex justify-center">
        <div class="border-2 border-dashed border-[#1B5886] rounded-xl px-8 py-4">
          <p class="text-[#1B5886] text-2xl font-bold tracking-wide">
            {{ referenceId }}
          </p>
        </div>
      </div>

      <div class="flex justify-center gap-4">
        <PrimaryButton
          v-if="showSecondaryButton"
          variant="outline"
          size="md"
          @click="handleSecondaryClick"
        >
          {{ secondaryButtonText }}
        </PrimaryButton>

        <PrimaryButton
          v-if="showPrimaryButton"
          variant="secondary"
          size="md"
          @click="handlePrimaryClick"
        >
          {{ primaryButtonText }}
        </PrimaryButton>
      </div>
    </div>
  </div>
</template>