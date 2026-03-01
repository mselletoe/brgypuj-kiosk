<script setup>
import { ref, watch, computed } from 'vue';
import { NInput, NDatePicker, NTimePicker, NSwitch, NButton } from 'naive-ui';
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

// ── NDatePicker uses timestamps (ms); backend uses "YYYY-MM-DD" strings ──
const dateTimestamp = computed({
  get() {
    if (!form.value.event_date) return null;
    return new Date(form.value.event_date + 'T00:00:00').getTime();
  },
  set(ts) {
    if (!ts) { form.value.event_date = ''; return; }
    const d = new Date(ts);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    form.value.event_date = `${yyyy}-${mm}-${dd}`;
  }
});

// ── NTimePicker uses timestamps (ms); backend uses "HH:MM" strings ──
const timeTimestamp = computed({
  get() {
    if (!form.value.event_time) return null;
    const [h, m] = form.value.event_time.split(':').map(Number);
    const base = new Date();
    base.setHours(h, m, 0, 0);
    return base.getTime();
  },
  set(ts) {
    if (!ts) { form.value.event_time = ''; return; }
    const d = new Date(ts);
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    form.value.event_time = `${h}:${m}`;
  }
});

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }
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
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });
};

const formatDay = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', { weekday: 'long' });
};

// Converts "HH:MM" to "h:MM AM/PM"
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const [h, m] = timeStr.split(':').map(Number);
  const period = h >= 12 ? 'PM' : 'AM';
  const hour = h % 12 || 12;
  return `${hour}:${String(m).padStart(2, '0')} ${period}`;
};

const handleSave = () => {
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
            <p class="font-bold text-slate-700 text-sm mt-0.5">{{ formatTime(announcement.event_time) }}</p>
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
            class="p-2 border border-orange-300 rounded-lg text-orange-400 hover:bg-orange-50 transition-colors"
          >
            <PencilSquareIcon class="w-4 h-4" />
          </button>
          <button 
            @click="$emit('delete', announcement.id)" 
            class="p-2 border border-red-300 rounded-lg text-red-400 hover:bg-red-50 transition-colors"
          >
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>
      </template>

      <!-- Edit Mode -->
      <template v-else>
        <div class="space-y-3">
          <!-- Title -->
          <NInput
            v-model:value="form.title"
            placeholder="Announcement Title"
            maxlength="255"
            :input-props="{ style: 'font-weight: bold; font-size: 1.125rem;' }"
          />

          <!-- Description -->
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="Description (optional)"
            :rows="2"
            :resizable="false"
          />

          <!-- Event Date -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Event Date</label>
            <NDatePicker
              v-model:value="dateTimestamp"
              type="date"
              placeholder="Select date"
              class="w-full"
              :to="false"
              clearable
            />
          </div>

          <!-- Event Time -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Event Time (optional)</label>
            <NTimePicker
              v-model:value="timeTimestamp"
              :use12-hours="true"
              format="hh:mm a"
              placeholder="Select time"
              class="w-full"
              :to="false"
              clearable
            />
          </div>

          <!-- Location -->
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-gray-400 uppercase">Location</label>
            <NInput
              v-model:value="form.location"
              placeholder="Event Location"
              maxlength="255"
            />
          </div>

          <!-- Active Status -->
          <div class="flex items-center gap-3">
            <NSwitch v-model:value="form.is_active" />
            <span class="text-sm text-gray-700">Active (visible on kiosk)</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 mt-6">
          <NButton @click="$emit('cancel')" secondary>
            Cancel
          </NButton>
          <NButton @click="handleSave" type="primary">
            Save
          </NButton>
        </div>
      </template>
    </div>
  </div>
</template>