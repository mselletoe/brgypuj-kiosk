<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  placeholder: { type: String, default: 'Add notes here...' },
  modelValue: { type: String, default: '' }
});

const emit = defineEmits(['submit', 'update:modelValue'])

const isOpen = ref(false)
const noteText = ref(props.modelValue)
const containerRef = ref(null)

// Expose these so the external button can call them
const open = () => (isOpen.value = true)
const close = () => (isOpen.value = false)
const toggle = () => (isOpen.value = !isOpen.value)

defineExpose({ open, close, toggle })

watch(() => props.modelValue, (val) => {
  noteText.value = val
})

const handleSubmit = () => {
  if (noteText.value.trim()) {
    emit('submit', noteText.value)
    emit('update:modelValue', noteText.value)
    noteText.value = ''
    close()
  }
}

const handleClickOutside = (event) => {
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<template>
  <div ref="containerRef" class="relative inline-block">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-y-1 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-1 opacity-0"
    >
      <div 
        v-if="isOpen"
        class="absolute left-0 mt-2 z-[99] flex items-center gap-2 p-1.5 bg-white border border-gray-200 rounded-xl shadow-xl min-w-[350px]"
      >
        <input
          v-model="noteText"
          type="text"
          :placeholder="props.placeholder"
          class="flex-1 px-3 py-2 italic text-gray-500 bg-transparent focus:outline-none"
          @keyup.enter="handleSubmit"
          v-focus
        />
        
        <button
          @click="handleSubmit"
          class="flex items-center justify-center w-10 h-10 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
        >
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script>
export const vFocus = {
  mounted: (el) => el.focus()
}
</script>