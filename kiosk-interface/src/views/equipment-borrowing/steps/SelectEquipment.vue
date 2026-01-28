<script setup>
// 1. IMPORT Keyboard and nextTick
import { ref, computed, onMounted, nextTick } from 'vue'; 
import { useRouter } from 'vue-router';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import PrimaryButton from '@/components/shared/Button.vue';
import { PlusIcon, MinusIcon } from '@heroicons/vue/24/solid';
import Keyboard from '@/components/shared/Keyboard.vue';

// --- Props & Emits ---
const props = defineProps({
  selectedEquipment: Array,
  goNext: Function,
});
const emit = defineEmits(['update:selected-equipment']);
const router = useRouter();
const isLoading = ref(true);

// --- Local State ---
const allEquipment = ref([]);

// 2. ADD KEYBOARD STATE
const showKeyboard = ref(false);
const activeEquipment = ref(null); // This will store the item being edited
const quantityWarning = ref(''); // This will hold the warning message

// --- Fetch inventory on mount ---
onMounted(async () => {
  isLoading.value = true;
  try {
    const inventoryData = await getInventory();
    allEquipment.value = inventoryData.map(item => ({
      id: item.id,
      name: item.name,
      available: item.available_quantity,
      total: item.total_quantity,
      rate: parseFloat(item.rate),
      ratePer: item.rate_per,
    }));
  } catch (error) {
    console.error("Failed to fetch equipment:", error);
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
  return `₱${parseFloat(value).toLocaleString()}`;
};
const hasSelection = computed(() => props.selectedEquipment.length > 0);
const summaryItems = computed(() => props.selectedEquipment);

// --- 3. REFACTORED LOGIC ---

// This new function is the single source of truth for updating quantity
const setQuantity = (equipment, newQuantity) => {
  // Validate and clamp the quantity
  if (newQuantity < 0) {
    newQuantity = 0;
  }
  
  if (newQuantity > equipment.available) {
    newQuantity = equipment.available;
    quantityWarning.value = `Max available: ${equipment.available}`;
  } else {
    quantityWarning.value = ''; // Clear warning
  }

  let newSelection = [...props.selectedEquipment];
  const item = getSelectedItem(equipment);

  if (newQuantity > 0) {
    if (item) {
      // Item already in cart, update its quantity
      const itemInNew = newSelection.find(i => i.id === item.id);
      itemInNew.quantity = newQuantity;
    } else {
      // Item not in cart, add it
      newSelection.push({
        id: equipment.id,
        name: equipment.name,
        rate: equipment.rate,
        ratePer: equipment.ratePer,
        quantity: newQuantity
      });
    }
  } else { // newQuantity is 0
    if (item) {
      // Remove item from cart
      newSelection = newSelection.filter(i => i.id !== equipment.id);
    }
  }
  emit('update:selected-equipment', newSelection);
};

// Refactored increment/decrement to use setQuantity
const increment = (equipment) => {
  const currentQuantity = getItemQuantity(equipment);
  setQuantity(equipment, currentQuantity + 1);
};

const decrement = (equipment) => {
  const currentQuantity = getItemQuantity(equipment);
  setQuantity(equipment, currentQuantity - 1);
};

// --- 4. NEW KEYBOARD HANDLERS ---
const openKeyboard = (equipment) => {
  activeEquipment.value = equipment;
  showKeyboard.value = true;
  quantityWarning.value = ''; // Clear warning when opening

  // Scroll logic
  nextTick(() => {
    const el = document.getElementById(`item-${equipment.id}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
};

const handleKeyboardKeyPress = (char) => {
  if (!activeEquipment.value) return;

  const item = activeEquipment.value;
  const currentQtyString = getItemQuantity(item).toString();
  
  // Handle leading zero (e.g., if current is 0, new char 5 becomes "5", not "05")
  const newQtyString = (currentQtyString === '0' ? '' : currentQtyString) + char;
  let newQuantity = parseInt(newQtyString, 10);

  if (isNaN(newQuantity)) {
    newQuantity = 0;
  }

  // Check for max available
  if (newQuantity > item.available) {
    newQuantity = item.available; // Clamp to max
    quantityWarning.value = `Max available: ${item.available}`;
  } else {
    quantityWarning.value = '';
  }

  setQuantity(item, newQuantity);
};

const handleKeyboardDelete = () => {
  if (!activeEquipment.value) return;

  const item = activeEquipment.value;
  let currentQtyString = getItemQuantity(item).toString();
  
  // Remove last character
  let newQtyString = currentQtyString.slice(0, -1);
  
  if (newQtyString === '') {
    newQtyString = '0';
  }

  const newQuantity = parseInt(newQtyString, 10);
  quantityWarning.value = ''; // Warning is cleared on delete
  setQuantity(item, newQuantity);
};

const handleKeyboardHide = () => {
  showKeyboard.value = false;
  activeEquipment.value = null;
  quantityWarning.value = '';
};
// --- END KEYBOARD HANDLERS ---

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
  <div class="flex flex-col w-full h-full" :class="{ 'content-with-keyboard': showKeyboard }">
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBackToHome" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Equipment Borrowing</h1>
        <p class="text-[#03335C] -mt-2">Below are list of available equipment:</p>
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
          :id="`item-${equipment.id}`" class="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 flex flex-col justify-between"
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
              <p v-if="activeEquipment?.id === equipment.id && quantityWarning" class="text-red-600 font-medium text-xs mt-1">
                {{ quantityWarning }}
              </p>
            </div>
          </div>
          
          <div class="mt-4 flex items-center justify-between">
            <button 
              @click="decrement(equipment)"
              :class="[
                'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
                getItemQuantity(equipment) === 0
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-red-100 text-red-600 hover:bg-red-200'
              ]"
              :disabled="getItemQuantity(equipment) === 0"
            >
              <MinusIcon class="w-6 h-6" />
            </button>
            
            <span 
              class="text-2xl font-bold w-12 text-center cursor-pointer hover:bg-gray-100 rounded-md"
              @click="openKeyboard(equipment)"
            >
              {{ getItemQuantity(equipment) }}
            </span>
            
            <button 
              @click="increment(equipment)"
              :class="[
                'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
                getItemQuantity(equipment) === equipment.available
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-green-100 text-green-600 hover:bg-green-200'
              ]"
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

  <Transition name="slide-up">
    <Keyboard
      v-if="showKeyboard"
      @key-press="handleKeyboardKeyPress"
      @delete="handleKeyboardDelete"
      @enter="handleKeyboardHide" @hide-keyboard="handleKeyboardHide"
      active-input-type="tel" class="fixed bottom-0 w-full"
    />
  </Transition>
</template>

<style scoped>
.content-with-keyboard {
  /* This value should be the height of your <Keyboard> component.
    320px is a common height. Adjust it if your keyboard is taller/shorter.
  */
  padding-bottom: 320px;
  
  /* This makes the padding animate in sync with the keyboard slide */
  transition: padding-bottom 0.3s ease-out;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>