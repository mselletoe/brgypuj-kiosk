<script setup>
import { ref, computed, onMounted } from 'vue'; // <-- Import onMounted
import { useRouter } from 'vue-router';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import PrimaryButton from '@/components/shared/PrimaryButton.vue';
import { PlusIcon, MinusIcon } from '@heroicons/vue/24/solid';
import { getInventory } from '@/api/equipmentApi'; // <-- Import API

// --- Props & Emits ---
const props = defineProps({
  selectedEquipment: Array,
  goNext: Function,
});
const emit = defineEmits(['update:selected-equipment']);
const router = useRouter();
const isLoading = ref(true);

// --- Local State ---
// MODIFIED: This is now an empty ref, will be filled by API
const allEquipment = ref([]);

// --- NEW: Fetch inventory on mount ---
onMounted(async () => {
  isLoading.value = true;
  try {
    const inventoryData = await getInventory();
    // Map backend data (e.g., 'total_quantity') to frontend data (e.g., 'total')
    allEquipment.value = inventoryData.map(item => ({
      id: item.id,
      name: item.name,
      available: item.available_quantity,
      total: item.total_quantity,
      rate: parseFloat(item.rate), // Ensure rate is a number
      ratePer: item.rate_per,
    }));
  } catch (error) {
    console.error("Failed to fetch equipment:", error);
    // You could show an error message to the user here
  } finally {
    isLoading.value = false;
  }
});

// --- Computed Properties ---
const getSelectedItem = (equipment) => {
  return props.selectedEquipment.find(item => item.id === equipment.id);
};
const getItemQuantity = (equipment) => {
  const item = getSelectedItem(equipment);
  return item ? item.quantity : 0;
};
const formatCurrency = (value) => {
  // Use 'P' for Pesos to match your admin panel
  return `₱${parseFloat(value).toLocaleString()}`;
};
const hasSelection = computed(() => props.selectedEquipment.length > 0);
const summaryItems = computed(() => props.selectedEquipment);

// --- Methods ---
const increment = (equipment) => {
  const item = getSelectedItem(equipment);
  const currentQuantity = item ? item.quantity : 0;
  if (currentQuantity < equipment.available) {
    let newSelection = [...props.selectedEquipment];
    if (item) {
      const itemInNew = newSelection.find(i => i.id === item.id);
      itemInNew.quantity++;
    } else {
      newSelection.push({
        id: equipment.id,
        name: equipment.name,
        rate: equipment.rate,
        ratePer: equipment.ratePer,
        quantity: 1
      });
    }
    emit('update:selected-equipment', newSelection);
  }
};
const decrement = (equipment) => {
  const item = getSelectedItem(equipment);
  if (item) {
    let newSelection = [...props.selectedEquipment];
    if (item.quantity > 1) {
      const itemInNew = newSelection.find(i => i.id === item.id);
      itemInNew.quantity--;
    } else {
      newSelection = newSelection.filter(i => i.id !== equipment.id);
    }
    emit('update:selected-equipment', newSelection);
  }
};
const resetSelection = () => {
  emit('update:selected-equipment', []);
};
const continueStep = () => {
  props.goNext('dates');
};
const goBackToHome = () => {
  router.push('/home');
};
</script>

<template>
  <div class="py-0 p-8">
    <div class="flex items-start gap-4">
      <ArrowBackButton @click="goBackToHome" />
      <div>
        <h1 class="text-[40px] font-bold text-[#013C6D]">Equipment Borrowing</h1>
        <p class="mt-0 text-lg text-gray-600">Below are list of available equipment:</p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-20">
      <p class="text-lg text-gray-600">Loading Equipment...</p>
    </div>

    <div v-else>
      <div class="grid grid-cols-4 gap-5 mt-6">
        <div 
          v-for="equipment in allEquipment" 
          :key="equipment.id"
          class="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 flex flex-col justify-between"
        >
          <div>
            <h3 class="text-xl font-bold text-[#013C6D] truncate">{{ equipment.name }}</h3>
            <div class="mt-2 text-sm">
              <div class="flex justify-between">
                <span>Available:</span>
                <span class="font-medium">{{ equipment.available }}/{{ equipment.total }}</span>
              </div>
              <div class="flex justify-between mt-1">
                <span>Rate:</span>
                <span class="font-bold text-green-600">
                  {{ formatCurrency(equipment.rate) }}/{{ equipment.ratePer }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="mt-4 flex items-center justify-between">
            <button 
              @click="decrement(equipment)"
              class="w-10 h-10 flex items-center justify-center bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors disabled:opacity-50"
              :disabled="getItemQuantity(equipment) === 0"
            >
              <MinusIcon class="w-6 h-6" />
            </button>
            <span class="text-2xl font-bold w-12 text-center">{{ getItemQuantity(equipment) }}</span>
            <button 
              @click="increment(equipment)"
              class="w-10 h-10 flex items-center justify-center bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50"
              :disabled="getItemQuantity(equipment) === equipment.available"
            >
              <PlusIcon class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-6 mt-6 items-stretch">
        <div class="flex-grow bg-white rounded-2xl shadow-lg border border-gray-200 p-4">
          <h4 class="text-lg font-bold text-[#013C6D]">Selected Items Summary</h4>
          <div class="mt-2 min-h-24">
            <p v-if="!hasSelection" class="text-gray-500 italic">
              No items selected.
            </p>
            <ul v-else class="space-y-1 text-sm">
              <li 
                v-for="item in summaryItems" 
                :key="item.id"
                class="flex justify-between"
              >
                <span class="truncate pr-2">{{ item.name }}</span>
                <span class="font-medium flex-shrink-0">
                  {{ item.quantity }} x {{ formatCurrency(item.rate) }}/{{ item.ratePer }}
                </span>
              </li>
            </ul>
          </div>
        </div>
        <div class="flex-shrink-0 w-[320px] flex flex-col gap-4">
          <PrimaryButton
            :bgColor="hasSelection ? 'bg-red-600' : 'bg-gray-400'"
            :borderColor="hasSelection ? 'border-red-600' : 'border-gray-400'"
            :disabled="!hasSelection"
            @click="resetSelection"
            class="py-3 text-lg font-bold flex-1"
          >
            Reset Selection
          </PrimaryButton>
          <PrimaryButton
            :bgColor="hasSelection ? 'bg-[#013C6D]' : 'bg-gray-400'"
            :borderColor="hasSelection ? 'border-[#013C6D]' : 'border-gray-400'"
            :disabled="!hasSelection"
            @click="continueStep"
            class="py-3 text-lg font-bold flex-1"
          >
            Continue to Dates
          </PrimaryButton>
        </div>
      </div> 
    </div>
  </div>
</template>