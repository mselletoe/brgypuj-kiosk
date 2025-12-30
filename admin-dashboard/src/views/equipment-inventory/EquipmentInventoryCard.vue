<script setup>
import { ref, watch } from 'vue';
import { TrashIcon, PencilSquareIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  equipment: { 
    type: Object, 
    default: () => ({ 
      id: null,
      item_name: '', 
      total_owned: 0, 
      available: 0, 
      rental_rate: 0 
    }) 
  },
  isEditing: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false },
  isSelected: { type: Boolean, default: false }
});

const emit = defineEmits(['save', 'cancel', 'delete', 'edit', 'toggle-select']);

// Internal form state
const form = ref({ ...props.equipment });

// Sync form if the equipment prop updates externally
watch(() => props.equipment, (newVal) => {
  form.value = { ...newVal };
}, { deep: true });

const handleToggle = () => {
  emit('toggle-select', props.equipment.id);
};
</script>

<template>
  <div 
    class="rounded-xl border-2 shadow-sm overflow-hidden flex flex-col h-full transition-all relative"
    :class="{
        'border-[#0957FF] bg-[#F0F5FF]': isEditing || isNew,
        'border-gray-200 bg-white': !isEditing && !isNew
    }"
  >
    <div v-if="!isEditing && !isNew" class="absolute top-4 right-4 z-10">
      <input 
        type="checkbox" 
        :checked="isSelected"
        @change="handleToggle"
        class="w-4 h-4 rounded border-gray-300 accent-blue-600 cursor-pointer" 
      />
    </div>

    <div class="p-6 flex-1 flex flex-col">
      <template v-if="!isEditing && !isNew">
        <div class="mb-6">
          <p class="text-gray-400 font-medium text-[11px] uppercase tracking-wider mb-1">Item Name</p>
          <h3 class="text-2xl font-bold text-slate-800 leading-tight">{{ equipment.item_name || 'N/A' }}</h3>
        </div>
        
        <div class="grid grid-cols-2 gap-6 flex-1">
          <div>
            <p class="text-gray-400 font-medium text-[11px] uppercase tracking-wider">Total Owned</p>
            <p class="font-bold text-slate-700 text-lg mt-0.5">{{ equipment.total_owned }}</p>
          </div>
          <div>
            <p class="text-gray-400 font-medium text-[11px] uppercase tracking-wider">Available</p>
            <p class="font-bold text-green-600 text-lg mt-0.5">{{ equipment.available }}</p>
          </div>
          <div class="col-span-2">
            <p class="text-gray-400 font-medium text-[11px] uppercase tracking-wider">Rental Rate per day</p>
            <p class="font-bold text-slate-700 text-lg mt-0.5">{{ equipment.rental_rate }}</p>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4">
          <button 
            @click="$emit('edit', equipment)" 
            class="p-2 border border-orange-200 rounded-lg text-orange-400 hover:bg-orange-50 transition-colors"
          >
            <PencilSquareIcon class="w-6 h-6" />
          </button>
          <button 
            @click="$emit('delete', equipment.id)" 
            class="p-2 border border-red-100 rounded-lg text-red-400 hover:bg-red-50 transition-colors"
          >
            <TrashIcon class="w-6 h-6" />
          </button>
        </div>
      </template>

      <template v-else>
        <div class="space-y-4">
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Item Name</label>
            <input 
              v-model="form.item_name" 
              placeholder="e.g. Monobloc Chairs" 
              class="bg-white w-full text-lg font-bold p-2 border border-gray-200 rounded-md focus:border-blue-500 outline-none"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase">Total Owned</label>
              <input v-model.number="form.total_owned" type="number" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none" />
            </div>
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase">Available</label>
              <input v-model.number="form.available" type="number" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none" />
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Rental Rate per day</label>
            <input v-model.number="form.rental_rate" type="number" placeholder="0" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none" />
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-8">
          <button @click="$emit('cancel')" class="px-5 py-2 border border-gray-300 rounded-md text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors">Cancel</button>
          <button @click="$emit('save', form)" class="px-7 py-2 bg-blue-600 text-white rounded-md text-sm font-bold hover:bg-blue-700 transition-colors shadow-sm">Save</button>
        </div>
      </template>
    </div>
  </div>
</template>