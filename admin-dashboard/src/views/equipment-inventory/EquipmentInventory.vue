<script setup>
import { ref, onMounted } from 'vue';
import { getInventory, updateInventory } from '@/api/equipmentApi';
import EquipmentInventoryCard from './EquipmentInventoryCard.vue';
import { useMessage } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue'

const message = useMessage();
const emit = defineEmits(['inventory-updated']);

// --- State Management ---
const localInventory = ref([]);
const selectedIds = ref([]);
const isLoading = ref(false);

// --- Data Fetching & Mapping ---
async function fetchActualInventory() {
  isLoading.value = true;
  try {
    const inventoryData = await getInventory();
    
    // Mapping backend fields to the Card Component expectations
    localInventory.value = inventoryData.map(item => ({
      id: item.id,
      item_name: item.name,            
      total_owned: item.total_quantity, 
      available: item.available_quantity,
      rental_rate: item.rate,          
      editing: false,
      isNew: false, // Flag to distinguish existing from newly added
      
      name: item.name,
      total: item.total_quantity,
      rate: item.rate
    }));
  } catch (error) {
    console.error('Failed to load inventory:', error);
    message.error('Could not load equipment inventory.');
  } finally {
    isLoading.value = false;
  }
}

// --- CRUD Actions ---
function startCreate() {
  // Prevent multiple "New" cards at once
  if (localInventory.value.some(item => item.isNew)) return;

  // Add a blank template to the start of the list
  localInventory.value.unshift({
    id: Date.now(), // temporary ID
    item_name: '',
    total_owned: 0,
    available: 0,
    rental_rate: 0,
    editing: true,
    isNew: true
  });
}

async function handleSave(formData) {
  if (formData.available > formData.total_owned) {
    message.warning('"Available" count cannot be greater than "Total Owned".');
    return;
  }
  
  try {
    const apiPayload = {
      id: formData.isNew ? undefined : formData.id,
      name: formData.item_name,
      total_quantity: formData.total_owned,
      rate: formData.rental_rate
    };

    // Note: You might need a createInventory API call here if formData.isNew is true
    await updateInventory(apiPayload);
    
    message.success(`Changes for "${formData.item_name}" saved!`);
    fetchActualInventory();
    emit('inventory-updated'); 
  } catch (error) {
    console.error('Failed to save:', error);
    message.error('Failed to save changes.');
  }
}

function handleEdit(item) {
  item.editing = true;
}

function handleCancel(item) {
  if (item.isNew) {
    localInventory.value.shift(); // Remove the temp card
  } else {
    item.editing = false;
    fetchActualInventory(); // Revert changes
  }
}

function toggleSelect(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id);
  } else {
    selectedIds.value.push(id);
  }
}

onMounted(fetchActualInventory);
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Equipment Inventory Management" />
        <p class="text-sm text-gray-500 mt-1">Track community assets, update stock levels, and set rental rates.</p>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="startCreate"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          Add Item
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar">
      <div v-if="isLoading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="localInventory.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-6">
        <EquipmentInventoryCard
          v-for="item in localInventory"
          :key="item.id"
          :equipment="item"
          :is-editing="item.editing"
          :is-new="item.isNew"
          :is-selected="selectedIds.includes(item.id)"
          @edit="handleEdit(item)"
          @cancel="handleCancel(item)"
          @save="handleSave"
          @toggle-select="toggleSelect"
          @delete="$emit('delete-requested', item.id)"
        />
      </div>

      <div v-if="!isLoading && localInventory.length === 0" class="text-center py-20 border-2 border-dashed border-gray-100 rounded-xl">
        <p class="text-gray-400">Your inventory is currently empty.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>