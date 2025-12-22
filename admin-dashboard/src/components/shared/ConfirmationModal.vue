<script setup>
import { QuestionMarkCircleIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Are you sure?'
  },
  confirmText: {
    type: String,
    default: 'Yes'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  confirmButtonClass: {
    type: String,
    default: 'bg-[#0957FF] hover:bg-blue-700'
  }
});

const emit = defineEmits(['confirm', 'cancel']);
</script>

<template>
  <Transition name="fade">
    <div 
      v-if="show" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="emit('cancel')"
    >
      <div class="bg-white rounded-2xl px-10 py-8 max-w-sm w-full shadow-xl transform transition-all flex flex-col items-center text-center">
        
        <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mb-6">
          <QuestionMarkCircleIcon class="w-12 h-12 text-blue-600" />
        </div>

        <h3 class="text-xl font-bold text-slate-800 leading-tight mb-8">
          {{ title }}
        </h3>

        <div class="flex space-x-3 w-full">
          <button 
            @click="emit('cancel')"
            class="flex-1 py-2 px-4 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            {{ cancelText }}
          </button>
          <button 
            @click="emit('confirm')"
            :class="[confirmButtonClass]"
            class="flex-1 py-2 px-4 rounded-lg font-semibold text-white transition-colors shadow-sm"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>