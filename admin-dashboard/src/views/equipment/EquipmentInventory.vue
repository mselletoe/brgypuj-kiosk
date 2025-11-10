<script setup>
import { ref, watch } from 'vue'; // <-- 1. Import 'watch' instead of 'onMounted'
import { PencilIcon, CheckIcon } from '@heroicons/vue/24/outline';
import { updateInventory } from '@/api/equipmentApi';

const props = defineProps({
  inventory: Array
});
const emit = defineEmits(['inventory-updated']);

// This is still our local copy
const localInventory = ref([]);

// --- 2. THE FIX: Replaced onMounted with watch ---
// This function now "watches" the inventory prop.
// When the prop changes (i.e., when the API call finishes),
// this code will run and update localInventory.
watch(() => props.inventory, (newInventory) => {
  if (newInventory) {
    // We create our local copy, adding the 'editing' flag
    localInventory.value = newInventory.map(item => ({ 
      ...item, 
      editing: false 
    }));
  }
}, { immediate: true }); // 'immediate: true' runs this once on load

// --- END OF FIX ---

async function saveChanges(item) { // <-- Made this async
  if (item.available > item.total) {
    alert('Error: "Available" count cannot be greater than "Total Owned".');
    return;
  }
  
  try {
    // --- API CALL ---
    await updateInventory(item);
    // --- END CALL ---
    item.editing = false;
    alert(`Changes for "${item.name}" saved!`);
    // Tell the parent to refresh ALL data
    emit('inventory-updated'); 
  } catch (error) {
    console.error('Failed to save:', error);
    alert('Failed to save changes. Please try again.');
  }
}
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      Manage Equipment Inventory
    </h2>
    <p class="mb-6 text-gray-600">
      Edit the name, total quantity, and rental rate for each item. 
      The "available" count is updated automatically by requests.
    </p>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div 
        v-for="item in localInventory" 
        :key="item.id" 
        class="border border-gray-200 p-4 rounded-lg flex flex-col justify-between shadow-sm"
      >
        <div class="flex-grow w-full">
          
          <div>
            <label class="block text-sm font-medium text-gray-500">Item Name</label>
            <input
              v-if="item.editing"
              v-model="item.name"
              type="text"
              class="mt-1 w-full px-2 py-1 border border-gray-300 rounded-md shadow-sm text-lg font-bold"
            />
            <h3 v-else class="text-lg font-bold text-gray-800 pt-1">{{ item.name }}</h3>
          </div>

          <div class="grid grid-cols-2 gap-x-6 gap-y-4 mt-4">
            <div>
              <label class="block text-sm font-medium text-gray-500">Total Owned</label>
              <input 
                v-if="item.editing" 
                v-model.number="item.total" 
                type="number" 
                min="0"
                class="mt-1 w-full px-2 py-1 border border-gray-300 rounded-md shadow-sm"
              />
              <span v-else class="text-lg font-semibold text-gray-700">{{ item.total }}</span>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-500">Available</label>
              <input 
                v-if="item.editing" 
                v-model.number="item.available" 
                type="number" 
                min="0"
                :max="item.total"
                class="mt-1 w-full px-2 py-1 border border-gray-300 rounded-md shadow-sm"
                :class="{ 'border-red-500': item.available > item.total }"
              />
              <span v-else class="text-lg font-semibold text-green-600">{{ item.available }}</span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Rental Rate (₱)</label>
              <input 
                v-if="item.editing" 
                v-model.number="item.rate" 
                type="number" 
                min="0"
                class="mt-1 w-full px-2 py-1 border border-gray-300 rounded-md shadow-sm"
              />
              <span v-else class="text-lg font-semibold text-gray-700">{{ item.rate }}</span>
            </div>
          </div>
        </div>
        
        <div class="flex-shrink-0 mt-6 w-full">
          <button
            v-if="!item.editing"
            @click="item.editing = true"
            class="w-full px-4 py-2 bg-blue-500 text-white rounded-md shadow-sm hover:bg-blue-600 flex items-center justify-center gap-2"
          >
            <PencilIcon class="w-4 h-4" /> Edit
          </button>
          <button
            v-else
            @click="saveChanges(item)"
            class="w-full px-4 py-2 bg-green-500 text-white rounded-md shadow-sm hover:bg-green-600 flex items-center justify-center gap-2"
          >
            <CheckIcon class="w-4 h-4" /> Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>