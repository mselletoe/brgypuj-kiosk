<script setup>
import { ref } from 'vue';
import EquipmentRequestsList from './EquipmentRequestsList.vue';
import EquipmentCreateForm from './EquipmentCreateForm.vue';
import EquipmentInventory from './EquipmentInventory.vue';

const mainTab = ref('manage'); // 'manage', 'create', or 'inventory'

// This is the "single source of truth" for your inventory.
const masterEquipmentList = ref([
  { id: 1, name: 'Event Tent', total: 10, available: 8, rate: 500, editing: false },
  { id: 2, name: 'Monobloc Chairs', total: 200, available: 150, rate: 10, editing: false },
  { id: 3, name: 'Folding Tables', total: 5, available: 5, rate: 1500, editing: false },
  { id: 4, name: 'Sound System', total: 3, available: 2, rate: 300, editing: false },
]);

</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
      <h1 class="text-3xl font-bold text-gray-800">
        Equipment Request Management
      </h1>
      
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
        <EquipmentRequestsList /> 
      </div>
      
      <div v-if="mainTab === 'create'">
        <EquipmentCreateForm :inventory="masterEquipmentList" />
      </div>
      <div v-if="mainTab === 'inventory'">
        <EquipmentInventory :inventory="masterEquipmentList" />
      </div>
    </div>
  </div>
</template>