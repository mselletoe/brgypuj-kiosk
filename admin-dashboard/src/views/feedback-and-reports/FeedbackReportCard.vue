<script setup>
import { computed } from 'vue';
import { TrashIcon, StarIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/solid';
import { StarIcon as StarOutline } from '@heroicons/vue/24/outline';

const props = defineProps({
  id: { type: String, required: true },
  type: { 
    type: String, 
    required: true, 
    validator: (v) => ['feedback', 'report'].includes(v) 
  },
  title: { type: String, required: true },
  requester: { type: Object, required: true },
  rfidNo: { type: String, required: true },
  createdOn: { type: String, required: true },
  rating: { type: Number, default: 0 }, // 1-5
  ratingLabel: { type: String, default: '' },
  comment: { type: String, default: '' },
  isSelected: { type: Boolean, default: false },
  isResolved: { type: Boolean, default: false }
});

const emit = defineEmits(['delete', 'undo', 'update:selected']);

const accentColorClass = computed(() => {
  return props.type === 'report' ? 'border-l-[#FF2B3A]' : 'border-l-[#0957FF]';
});

const badgeColorClass = computed(() => {
  return props.type === 'report' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-blue-50 border-blue-200 text-blue-900';
});
</script>

<template>
  <div 
    class="rounded-lg border-l-[6px] border p-5 flex items-start gap-4 transition-all relative"
    :class="[
      accentColorClass,
      isSelected ? 'border-[#0957FF] ring-1 ring-[#0957FF]/10 shadow-sm bg-[#F0F5FF]' : 'border-[#CCCCCC] bg-white'
    ]"
  >
    <!-- Reference No. -->
    <div class="flex flex-col items-center justify-center space-y-1">
      <div 
        class="flex justify-center border rounded px-4 min-w-[90px]"
        :class="badgeColorClass"
      >
        <div class="text-lg font-bold">{{ id }}</div>        
      </div>
      <div class="text-[9px] text-gray-400 font-medium">Reference No.</div>
    </div>

    <div class="flex-1 flex flex-col gap-3">
      <!-- Category Name -->
      <h3 class="text-xl font-bold text-slate-800">{{ title }}</h3>
      
      <!-- Details -->
      <div class="flex gap-16">
        <!-- Column 1 -->
        <div class="flex flex-col gap-3">
          <!-- Full Name -->
          <div class="flex flex-col">
            <span class="block text-[11px] text-gray-400 font-medium">{{ type === 'report' ? 'Report from' : 'Feedback from' }}</span>
            <span class="text-sm text-slate-700 font-bold">
              {{ requester.firstName }} {{ requester.middleName }} {{ requester.surname }}
            </span>
          </div>
          <!-- RFID No./Guest -->
          <div class="flex flex-col">
            <span class="block text-[11px] text-gray-400 font-medium">RFID No.</span>
            <span :class="rfidNo === 'Guest Mode' ? 'text-orange-500' : 'text-blue-600'" class="text-sm font-bold">
              {{ rfidNo }}
            </span>
          </div>
        </div>

        <!-- Column 2 -->
        <div class="flex flex-col gap-3">
          <!-- Created Date -->
          <div class="flex flex-col">
            <span class="block text-[11px] text-gray-400 font-medium">Created on</span>
            <span class="text-sm text-slate-700 font-bold">{{ createdOn }}</span>
          </div>

          <!-- Rating (Feedback only) -->
          <div v-if="type === 'feedback'" class="flex flex-col">
            <span class="block text-[11px] text-gray-400 font-medium">Rating</span>
            <div class="flex items-center gap-1">
              <span class="text-sm text-blue-600 font-bold mr-1">{{ ratingLabel }}</span>
              <div class="flex text-yellow-400">
                <template v-for="i in 5" :key="i">
                  <StarIcon v-if="i <= rating" class="w-4 h-4" />
                  <StarOutline v-else class="w-4 h-4 text-gray-300" />
                </template>
              </div>
            </div>
          </div>          
        </div>

        <!-- Column 3 -->
        <div v-if="type === 'feedback'" class="flex flex-col">
          <span class="block text-[11px] text-gray-400 font-medium">Additional Comment</span>
          <p class="text-sm text-slate-600 leading-relaxed italic">
            {{ comment || 'No comments provided.' }}
          </p>
        </div>
      </div>
    </div>

    <div class="flex flex-col items-end justify-between self-stretch min-w-fit">
      <input 
        type="checkbox" 
        :checked="isSelected"
        @change="$emit('update:selected', $event.target.checked)"
        class="w-4 h-4 border-gray-300 rounded accent-[#0957FF] cursor-pointer"
      />

      <div class="flex items-center gap-2">
        <!-- Resolved badge — shown after undo has been applied -->
        <span
          v-if="type === 'report' && isResolved"
          class="px-4 h-9 flex items-center bg-green-50 text-green-700 border border-green-300 rounded-md text-sm font-semibold"
        >Resolved</span>

        <!-- Undo button — reactivates the resident's RFID card -->
        <button
          v-else-if="type === 'report'"
          @click="$emit('undo', id)"
          class="w-9 h-9 justify-center bg-white text-orange-600 border border-orange-400 hover:bg-orange-50 rounded-md text-sm font-semibold transition-all flex items-center gap-1.5"
        >
          <ArrowUturnLeftIcon class="w-4 h-4" />
        </button>

        <button
          @click="$emit('delete', id)"
          class="w-9 h-9 flex items-center justify-center bg-white text-red-500 border border-red-400 hover:bg-red-50 rounded-md transition-all"
        >
          <TrashIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>