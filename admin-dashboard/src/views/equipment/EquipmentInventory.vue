<script setup>
import { ref } from 'vue';
import { PencilIcon, CheckIcon } from '@heroicons/vue/24/outline';

const equipment = ref([
  { id: 1, name: 'Event Tent', total: 10, available: 8, rate: 500, editing: false },
  { id: 2, name: 'Monobloc Chairs', total: 200, available: 150, rate: 10, editing: false },
  { id: 3, name: 'Folding Tables', total: 5, available: 5, rate: 1500, editing: false },
  { id: 4, name: 'Sound System', total: 3, available: 2, rate: 300, editing: false },
]);

// --- Placeholder for saving changes ---
function saveChanges(item) {
  // Add a simple validation
  if (item.available > item.total) {
    alert('Error: "Available" count cannot be greater than "Total Owned".');
    return;
  }
  
  item.editing = false;
  // In a real app, you would send this 'item' object to your database
  console.log('Saving item to database:', item);
  alert(`Changes for "${item.name}" saved!`);
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
        v-for="item in equipment" 
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