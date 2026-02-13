<script setup>
import { ref, watch } from 'vue';
import { TrashIcon, PencilSquareIcon, PhotoIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  announcement: { 
    type: Object, 
    default: () => ({ 
      title: '', 
      event_date: '', 
      event_time: '', 
      location: '', 
      description: '',
      image_base64: null,
      is_active: true 
    }) 
  },
  isEditing: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false },
  isSelected: { type: Boolean, default: false }
});

const emit = defineEmits(['save', 'cancel', 'delete', 'edit', 'image-upload', 'toggle-status', 'update:selected']);

// Internal form state to avoid mutating props directly
const form = ref({ ...props.announcement });
const imageFile = ref(null);
const imagePreview = ref(null);

// Set initial image preview if exists
if (props.announcement.image_base64) {
  imagePreview.value = `data:image/jpeg;base64,${props.announcement.image_base64}`;
}

// Sync form if the announcement prop updates externally
watch(() => props.announcement, (newVal) => {
  form.value = { ...newVal };
  if (newVal.image_base64) {
    imagePreview.value = `data:image/jpeg;base64,${newVal.image_base64}`;
  } else {
    imagePreview.value = null;
  }
}, { deep: true });

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB');
      return;
    }

    imageFile.value = file;
    const url = URL.createObjectURL(file);
    imagePreview.value = url;
    emit('image-upload', { file, url });
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });
};

const formatDay = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { weekday: 'long' });
};

const handleSave = () => {
  // Emit form data along with the image file
  emit('save', { 
    formData: form.value, 
    imageFile: imageFile.value 
  });
};
</script>

<template>
  <div 
    class="rounded-xl border-2 shadow-sm overflow-hidden flex flex-col h-full transition-all"
    :class="{
        'border-[#0957FF] bg-[#F0F5FF]': isEditing || isNew,
        'border-gray-200 bg-white': !isEditing && !isNew,
        'opacity-60': !announcement.is_active && !isEditing && !isNew
    }"
  >
    <!-- Image Section -->
    <div class="relative h-36 bg-[#D0D0D0] group">
      <img 
        v-if="imagePreview" 
        :src="imagePreview" 
        class="w-full h-full object-cover" 
        alt="Announcement image"
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-white">
        <PhotoIcon class="w-10 h-10 opacity-50" />
      </div>

      <!-- Image Upload Overlay (Edit Mode) -->
      <div v-if="isEditing || isNew" class="absolute inset-0 bg-black/10 flex items-center justify-center">
        <label class="bg-white/90 hover:bg-white px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 cursor-pointer shadow-sm transition-colors">
          <PhotoIcon class="w-4 h-4 text-gray-600" />
          <span>{{ imagePreview ? 'Change Photo' : 'Add Photo' }}</span>
          <input type="file" class="hidden" @change="handleFileUpload" accept="image/jpeg,image/png,image/gif,image/webp" />
        </label>
      </div>

      <!-- Status Badge (View Mode) -->
      <div v-if="!isEditing && !isNew" class="absolute top-3 left-3">
        <button
          @click="$emit('toggle-status', announcement)"
          :class="[
            'px-2 py-1 rounded-md text-xs font-bold transition-colors',
            announcement.is_active 
              ? 'bg-green-500 text-white hover:bg-green-600' 
              : 'bg-gray-400 text-white hover:bg-gray-500'
          ]"
        >
          {{ announcement.is_active ? 'Active' : 'Inactive' }}
        </button>
      </div>

      <!-- Selection Checkbox -->
      <div 
        v-if="!isEditing && !isNew"
        class="absolute top-3 right-3 z-10"
      >
        <input 
          type="checkbox" 
          :checked="isSelected"
          @change="$emit('update:selected', $event.target.checked)"
          class="w-5 h-5 border-gray-300 rounded accent-[#0957FF] cursor-pointer shadow-sm"
        />
      </div>
    </div>

    <!-- Content Section -->
    <div class="p-5 flex-1 flex flex-col">
      <!-- View Mode -->
      <template v-if="!isEditing && !isNew">
        <h3 class="text-xl font-bold text-slate-800 leading-tight mb-2">
          {{ announcement.title }}
        </h3>
        
        <p v-if="announcement.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
          {{ announcement.description }}
        </p>
        
        <div class="space-y-3 flex-1">
          <div>
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Date</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">
              {{ formatDate(announcement.event_date) }}
            </p>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ formatDay(announcement.event_date) }}
            </p>
          </div>
          
          <div v-if="announcement.event_time">
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Time</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ announcement.event_time }}</p>
          </div>
          
          <div>
            <p class="text-gray-400 font-medium text-[10px] uppercase tracking-wider">Location</p>
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ announcement.location }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 mt-4">
          <button 
            @click="$emit('edit', announcement)" 
            class="p-2 border border-orange-200 rounded-lg text-orange-400 hover:bg-orange-50 transition-colors"
          >
            <PencilSquareIcon class="w-5 h-5" />
          </button>
          <button 
            @click="$emit('delete', announcement.id)" 
            class="p-2 border border-red-100 rounded-lg text-red-400 hover:bg-red-50 transition-colors"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>
      </template>

      <!-- Edit Mode -->
      <template v-else>
        <div class="space-y-3">
          <!-- Title -->
          <input 
            v-model="form.title" 
            placeholder="Announcement Title" 
            maxlength="255"
            class="bg-white w-full text-lg font-bold p-2 border border-gray-200 rounded-md focus:border-blue-500 outline-none"
          />
          
          <!-- Description -->
          <textarea
            v-model="form.description"
            placeholder="Description (optional)"
            rows="2"
            class="bg-white w-full p-2 border border-gray-200 rounded-md text-sm outline-none resize-none focus:border-blue-500"
          ></textarea>
          
          <!-- Event Date -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Event Date</label>
            <input 
              v-model="form.event_date" 
              type="date" 
              class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none focus:border-blue-500" 
            />
          </div>

          <!-- Event Time -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Event Time (optional)</label>
            <input 
              v-model="form.event_time" 
              type="time"
              class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none focus:border-blue-500" 
            />
          </div>

          <!-- Location -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Location</label>
            <input 
              v-model="form.location" 
              placeholder="Event Location" 
              maxlength="255"
              class="w-full p-2 border border-gray-200 rounded-md text-sm outline-none focus:border-blue-500" 
            />
          </div>

          <!-- Active Status -->
          <div class="flex items-center gap-2">
            <input 
              v-model="form.is_active" 
              type="checkbox" 
              id="is_active"
              class="rounded"
            />
            <label for="is_active" class="text-sm text-gray-700">
              Active (visible on kiosk)
            </label>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 mt-6">
          <button 
            @click="$emit('cancel')" 
            class="px-5 py-2 border border-gray-300 rounded-md text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="handleSave" 
            class="px-7 py-2 bg-blue-600 text-white rounded-md text-sm font-bold hover:bg-blue-700 transition-colors shadow-sm"
          >
            Save
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
