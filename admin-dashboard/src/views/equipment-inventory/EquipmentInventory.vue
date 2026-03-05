<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { TrashIcon, CheckIcon } from '@heroicons/vue/24/outline'
import EquipmentInventoryCard from './EquipmentInventoryCard.vue';
import { useMessage, NInput } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import { 
  getEquipmentInventory, 
  createEquipmentItem, 
  updateEquipmentItem, 
  deleteEquipmentItem,
  bulkDeleteEquipmentItems 
} from '@/api/equipmentService';

const message = useMessage();
const emit = defineEmits(['inventory-updated']);

// --- State Management ---
const localInventory = ref([]);
const selectedIds = ref([]);
const isLoading = ref(false);
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)
const isBulkDelete = ref(false)
const searchQuery = ref('')

// --- Data Fetching & Mapping ---
async function fetchActualInventory() {
  isLoading.value = true;
  try {
    const response = await getEquipmentInventory();
    const inventoryData = response.data;
    
    localInventory.value = inventoryData.map(item => ({
      id: item.id,
      item_name: item.name,            
      total_owned: item.total_quantity, 
      available: item.available_quantity,
      rental_rate: item.rate_per_day,          
      editing: false,
      isNew: false,
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
  if (localInventory.value.some(item => item.isNew)) return;

  localInventory.value.unshift({
    id: Date.now(),
    item_name: '',
    total_owned: 0,
    available: 0,
    rental_rate: 0,
    editing: true,
    isNew: true
  });
}

async function handleSave(formData) {
  if (!formData.item_name || formData.item_name.trim() === '') {
    message.warning('Item name is required.');
    return;
  }

  if (formData.total_owned < 0) {
    message.warning('Total owned cannot be negative.');
    return;
  }

  if (formData.available < 0) {
    message.warning('Available quantity cannot be negative.');
    return;
  }

  if (formData.available > formData.total_owned) {
    message.warning('Available quantity cannot be greater than total owned.');
    return;
  }

  if (formData.rental_rate < 0) {
    message.warning('Rental rate cannot be negative.');
    return;
  }
  
  try {
    const apiPayload = {
      name: formData.item_name.trim(),
      total_quantity: formData.total_owned,
      available_quantity: formData.available,
      rate_per_day: formData.rental_rate
    };

    if (formData.isNew) {
      await createEquipmentItem(apiPayload);
      message.success(`"${formData.item_name}" added to inventory!`);
    } else {
      await updateEquipmentItem(formData.id, apiPayload);
      message.success(`Changes for "${formData.item_name}" saved!`);
    }
    
    await fetchActualInventory();
    emit('inventory-updated'); 
  } catch (error) {
    console.error('Failed to save:', error);
    
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail);
    } else {
      message.error('Failed to save changes.');
    }
  }
}

function handleEdit(item) {
  item.editing = true;
}

function handleCancel(item) {
  if (item.isNew) {
    localInventory.value.shift();
  } else {
    item.editing = false;
    fetchActualInventory();
  }
}

function toggleSelect(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id);
  } else {
    selectedIds.value.push(id);
  }
}

const filteredInventory = computed(() => {
  if (!searchQuery.value) return localInventory.value
  return localInventory.value.filter(item =>
    item.item_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const totalCount = computed(() => filteredInventory.value.length)
const selectedCount = computed(() => selectedIds.value.length)

const selectionState = computed(() => {
  if (totalCount.value === 0 || selectedCount.value === 0) return 'none'
  if (selectedCount.value < totalCount.value) return 'partial'
  return 'all'
})

function handleMainSelectToggle() {
  if (selectionState.value === 'all' || selectionState.value === 'partial') {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredInventory.value.map(i => i.id)
  }
}

watch(searchQuery, () => {
  selectedIds.value = []
})

function requestDelete(id) {
  deleteTargetId.value = id
  isBulkDelete.value = false
  showDeleteModal.value = true
}

function requestBulkDelete() {
  if (!selectedIds.value.length) return
  isBulkDelete.value = true
  showDeleteModal.value = true
}

async function confirmDelete() {
  try {
    if (isBulkDelete.value) {
      await bulkDeleteEquipmentItems(selectedIds.value)
      localInventory.value = localInventory.value.filter(
        i => !selectedIds.value.includes(i.id)
      )
      selectedIds.value = []
      message.success('Selected items deleted.')
    } else {
      await deleteEquipmentItem(deleteTargetId.value)
      localInventory.value = localInventory.value.filter(
        i => i.id !== deleteTargetId.value
      )
      message.success('Item deleted.')
    }

    emit('inventory-updated')
  } catch (err) {
    console.error(err)
    message.error(err.response?.data?.detail || 'Delete failed.')
  } finally {
    showDeleteModal.value = false
    deleteTargetId.value = null
  }
}

function cancelDelete() {
  showDeleteModal.value = false
  deleteTargetId.value = null
}

onMounted(fetchActualInventory)
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Equipment Inventory Management" />
        <p class="text-sm text-gray-500 mt-1">
          Track community assets, update stock levels, and set rental rates.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- Bulk Delete -->
        <button
          @click="requestBulkDelete"
          :disabled="selectionState === 'none'"
          class="p-2 border border-red-400 rounded-lg transition-colors"
          :class="
            selectionState === 'none'
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-red-50'
          "
        >
          <TrashIcon class="w-5 h-5 text-red-500" />
        </button>

        <!-- Select All / Partial -->
        <div
          class="flex items-center border rounded-lg overflow-hidden transition-colors"
          :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
        >
          <button
            @click="handleMainSelectToggle"
            class="p-2 hover:bg-gray-50 flex items-center"
          >
            <div
              class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
              :class="
                selectionState !== 'none'
                  ? 'bg-blue-600 border-blue-600'
                  : 'border-gray-400'
              "
            >
              <div
                v-if="selectionState === 'partial'"
                class="w-2 h-0.5 bg-white"
              ></div>
              <CheckIcon
                v-if="selectionState === 'all'"
                class="w-3 h-3 text-white"
              />
            </div>
          </button>
        </div>

        <!-- Add -->
        <button
          @click="startCreate"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto pr-2">
      <div v-if="isLoading" class="flex justify-center py-20">
        <div class="animate-spin h-10 w-10 border-b-2 border-blue-600 rounded-full"></div>
      </div>

      <div
        v-else-if="localInventory.length"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
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
          @delete="requestDelete(item.id)"
        />
      </div>

      <div
        v-if="!isLoading && !localInventory.length"
        class="text-center py-20 border-2 border-dashed rounded-xl"
      >
        <p class="text-gray-400">Your inventory is currently empty.</p>
      </div>
    </div>
  </div>

  <ConfirmModal
    :show="showDeleteModal"
    :title="
      isBulkDelete
        ? `Delete ${selectedIds.length} item(s)?`
        : 'Delete this item?'
    "
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />
</template>