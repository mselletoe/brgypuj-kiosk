<script setup>
import { computed } from 'vue';
import { TrashIcon, StarIcon } from '@heroicons/vue/24/solid';
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

const emit = defineEmits(['delete', 'mark-lost', 'update:selected']);

const accentColorClass = computed(() => {
  return props.type === 'report' ? 'border-l-[#FF2B3A]' : 'border-l-[#0957FF]';
});

const badgeColorClass = computed(() => {
  return props.type === 'report' ? 'bg-[#FFF0F0] border-[#FBBABA]' : 'bg-[#F0F5FF] border-[#D4DFF6]';
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
    <div class="flex flex-col items-center justify-center space-y-1">
      <div 
        class="flex justify-center border rounded px-4 py-1 min-w-[90px]"
        :class="badgeColorClass"
      >
        <div class="text-lg font-bold text-slate-700">{{ id }}</div>        
      </div>
      <div class="text-[9px] text-gray-400 font-medium uppercase tracking-wider">Reference</div>
    </div>

    <div class="flex-1 grid grid-cols-12 gap-4">
      <div class="col-span-12">
        <h3 class="text-xl font-bold text-slate-800">{{ title }}</h3>
      </div>
      
      <div class="col-span-3 flex flex-col gap-3">
        <div>
          <span class="block text-[11px] text-gray-400 font-medium">Feedback from</span>
          <span class="text-sm text-slate-700 font-bold">
            {{ requester.firstName }} {{ requester.middleName }} {{ requester.surname }}
          </span>
        </div>
        <div>
          <span class="block text-[11px] text-gray-400 font-medium">RFID No.</span>
          <span :class="rfidNo === 'Guest Mode' ? 'text-orange-500' : 'text-blue-600'" class="text-sm font-bold">
            {{ rfidNo }}
          </span>
        </div>
      </div>

      <div class="col-span-3 flex flex-col gap-3">
        <div>
          <span class="block text-[11px] text-gray-400 font-medium">Created on</span>
          <span class="text-sm text-slate-700 font-bold">{{ createdOn }}</span>
        </div>
        <div v-if="type === 'feedback'">
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

      <div class="col-span-6">
        <span class="block text-[11px] text-gray-400 font-medium">Additional Comment</span>
        <p class="text-sm text-slate-600 leading-relaxed italic">
          {{ comment || 'No comments provided.' }}
        </p>
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
        <button
          v-if="type === 'report' && !isResolved"
          @click="$emit('mark-lost', id)"
          class="px-4 h-9 bg-white text-red-600 border border-[#FF2B3A] hover:bg-red-50 rounded-md text-sm font-semibold transition-all"
        >
          Mark as Lost
        </button>

        <button
          @click="$emit('delete', id)"
          class="w-9 h-9 flex items-center justify-center bg-white text-[#B1202A] border border-[#FBBABA] hover:bg-[#FFE6E6] rounded-md transition-all"
        >
          <TrashIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>