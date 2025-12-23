<script setup>
import { ref, watch } from 'vue';
import { TrashIcon, PencilSquareIcon, PhotoIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  announcement: { 
    type: Object, 
    default: () => ({ title: '', date: '', start: '', end: '', location: '', image: null }) 
  },
  isEditing: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false }
});

const emit = defineEmits(['save', 'cancel', 'delete', 'edit', 'image-upload']);

// Internal form state to avoid mutating props directly
const form = ref({ ...props.announcement });

// Sync form if the announcement prop updates externally
watch(() => props.announcement, (newVal) => {
  form.value = { ...newVal };
}, { deep: true });

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const url = URL.createObjectURL(file);
    form.value.image = url;
    emit('image-upload', { file, url });
  }
};

const timeOptions = [
  '07:00 AM', '08:00 AM', '09:00 AM', '10:30 AM', '12:00 PM', 
  '01:30 PM', '03:00 PM', '04:30 PM', '06:30 PM', '08:00 PM'
];
</script>

<template>
  <div 
    class="rounded-xl border-2 shadow-sm overflow-hidden flex flex-col h-full transition-all"
    :class="{
        'border-[#0957FF] bg-[#F0F5FF]': isEditing || isNew,
        'border-gray-200 bg-white': !isEditing && !isNew
    }"
  >
    <div class="relative h-36 bg-[#D0D0D0] group">
      <img v-if="form.image" :src="form.image" class="w-full h-full object-cover" />
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-white">
        <PhotoIcon class="w-10 h-10 opacity-50" />
      </div>

      <div v-if="isEditing || isNew" class="absolute inset-0 bg-black/10 flex items-center justify-center">
        <label class="bg-white/90 hover:bg-white px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 cursor-pointer shadow-sm transition-colors">
          <PhotoIcon class="w-4 h-4 text-gray-600" />
          <span>Add Photo</span>
          <input type="file" class="hidden" @change="handleFileUpload" accept="image/*" />
        </label>
      </div>

      <input v-if="!isEditing && !isNew" type="checkbox" class="absolute top-3 right-3 w-4 h-4 rounded border-gray-300 accent-blue-600 cursor-pointer" />
    </div>

    <div class="p-5 flex-1 flex flex-col">
      <template v-if="!isEditing && !isNew">
        <h3 class="text-xl font-bold text-slate-800 leading-tight mb-5">{{ announcement.title }}</h3>
        
        <div class="space-y-4 flex-1">
          <div>
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Date</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ announcement.date || 'December 18, 2025' }}</p>
          </div>
          <div>
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Time</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ announcement.start }} - {{ announcement.end }}</p>
          </div>
          <div>
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Location</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ announcement.location }}</p>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4">
          <button @click="$emit('edit', announcement)" class="p-2 border border-orange-200 rounded-lg text-orange-400 hover:bg-orange-50 transition-colors">
            <PencilSquareIcon class="w-5 h-5" />
          </button>
          <button @click="$emit('delete', announcement.id)" class="p-2 border border-red-100 rounded-lg text-red-400 hover:bg-red-50 transition-colors">
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>
      </template>

      <template v-else>
        <div class="space-y-3">
          <input 
            v-model="form.title" 
            placeholder="Announcement Title" 
            class="bg-white w-full text-lg font-bold p-2 border border-gray-200 rounded-md focus:border-blue-500 outline-none"
          />
          
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Date</label>
            <input v-model="form.date" type="text" placeholder="December 18, 2025" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none" />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase">Time</label>
              <select v-model="form.start" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none">
                <option v-for="t in timeOptions" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase invisible">End</label>
              <div class="flex items-center gap-2">
                <span class="text-gray-400">-</span>
                <select v-model="form.end" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none">
                  <option v-for="t in timeOptions" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Location</label>
            <input v-model="form.location" placeholder="PUP CEA" class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none" />
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button @click="$emit('cancel')" class="px-5 py-2 border border-gray-300 rounded-md text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors">Cancel</button>
          <button @click="$emit('save', form)" class="px-7 py-2 bg-blue-600 text-white rounded-md text-sm font-bold hover:bg-blue-700 transition-colors shadow-sm">Save</button>
        </div>
      </template>
    </div>
  </div>
</template>