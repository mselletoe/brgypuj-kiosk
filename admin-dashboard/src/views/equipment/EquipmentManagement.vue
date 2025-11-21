<script setup>
import { ref, onMounted } from 'vue'; // Import onMounted
import EquipmentRequestsList from './EquipmentRequestsList.vue';
import EquipmentCreateForm from './EquipmentCreateForm.vue';
import EquipmentInventory from './EquipmentInventory.vue';
import PageTitle from '@/components/shared/PageTitle.vue'
import { getInventory } from '@/api/equipmentApi'; // Import the API function

const mainTab = ref('manage');

// This starts empty and will be filled from the API
const masterEquipmentList = ref([]);

// Fetch the inventory when the page loads
onMounted(async () => {
  try {
    const inventoryData = await getInventory();
    // Map backend names to frontend names
    masterEquipmentList.value = inventoryData.map(item => ({
      id: item.id,
      name: item.name,
      total: item.total_quantity,
      available: item.available_quantity,
      rate: item.rate,
      editing: false 
    }));
  } catch (error) {
    console.error('Failed to load inventory:', error);
    alert('Error: Could not load equipment inventory from the server.');
  }
});

// This function will be passed to the children to refresh data
async function refreshData() {
  try {
    const inventoryData = await getInventory();
    masterEquipmentList.value = inventoryData.map(item => ({
      id: item.id,
      name: item.name,
      total: item.total_quantity,
      available: item.available_quantity,
      rate: item.rate,
      editing: false
    }));
    // We also set the mainTab back to 'manage' after creation
    mainTab.value = 'manage';
  } catch (error) {
    console.error('Failed to refresh inventory:', error);
  }
}

</script>

<template>
  <div class="p-6 bg-white min-h-screen rounded-md w-full space-y-5">
    
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
      <PageTitle title="Equipment Management" />
      
      <div class="flex space-x-2 flex-shrink-0">
        <button
          @click="mainTab = 'manage'"
          :class="[
            'px-4 py-2 rounded-md font-medium text-sm',
            mainTab === 'manage' 
              ? 'bg-[#0957FF] text-white shadow-md' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          Manage Requests
        </button>
        <button
          @click="mainTab = 'create'"
          :class="[
            'px-4 py-2 rounded-md font-medium text-sm',
            mainTab === 'create' 
              ? 'bg-[#0957FF] text-white shadow-md' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          Create New Request
        </button>
        <button
          @click="mainTab = 'inventory'"
          :class="[
            'px-4 py-2 rounded-md font-medium text-sm',
            mainTab === 'inventory' 
              ? 'bg-[#0957FF] text-white shadow-md' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          Manage Inventory
        </button>
      </div>
    </div>

    <div>
      <div v-if="mainTab === 'manage'">
        <EquipmentRequestsList :key="mainTab" /> 
      </div>
      
      <div v-if="mainTab === 'create'">
        <EquipmentCreateForm 
          :inventory="masterEquipmentList" 
          @request-created="refreshData" 
        />
      </div>
      <div v-if="mainTab === 'inventory'">
        <EquipmentInventory 
          :inventory="masterEquipmentList" 
          @inventory-updated="refreshData" 
        />
      </div>
    </div>
  </div>
</template>