<script setup>
import { XMarkIcon } from '@heroicons/vue/24/solid';

defineProps({
  show: Boolean
});
const emit = defineEmits(['close', 'upload']);
</script>

<template>
  <transition name="fade">
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <transition name="pop">
        <div v-if="show" class="bg-white rounded-lg shadow-xl w-full max-w-lg">
          
          <div class="flex justify-between items-center p-4 border-b">
            <h3 class="text-xl font-semibold text-gray-800">Upload New Template</h3>
            <button @click="$emit('close')" class="p-1 rounded-full hover:bg-gray-200">
              <XMarkIcon class="w-5 h-5 text-gray-600" />
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label for="template-name" class="block text-sm font-medium text-gray-700">Template Name</label>
              <input type="text" id="template-name" placeholder="e.g., Barangay Clearance" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label for="template-file" class="block text-sm font-medium text-gray-700">Template File (.docx)</label>
              <input type="file" id="template-file" accept=".doc,.docx" class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
          </div>

          <div class="flex justify-end gap-3 p-4 bg-gray-50 border-t">
            <button 
              @click="$emit('close')"
              class="px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="$emit('upload')"
              class="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-blue-700"
            >
              Upload
            </button>
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.pop-enter-active {
  transition: all 0.3s ease-out;
}
.pop-leave-active {
  transition: all 0.3s ease-in;
}
.pop-enter-from, .pop-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>