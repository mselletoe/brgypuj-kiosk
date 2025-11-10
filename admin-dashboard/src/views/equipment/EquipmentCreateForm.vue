<script setup>
import { ref, computed } from 'vue';
import { createRequest } from '@/api/equipmentApi'; // <-- Import API

const props = defineProps({
  inventory: Array
});
const emit = defineEmits(['request-created']); // <-- Define emit

const newRequest = ref({
  borrowerName: '',
  contactNumber: '',
  borrowDate: null,
  returnDate: null,
  purpose: null,
  notes: '',
  selectedItem: null,
  quantity: 1
});

const purposeOptions = ref([ 'Barangay Event', 'Personal Event', 'Community Meeting', 'Emergency Use', 'Other' ]);
const selectedItemDetails = computed(() => {
  if (!newRequest.value.selectedItem || !props.inventory) return null;
  return props.inventory.find(item => item.id === newRequest.value.selectedItem);
});
const isQuantityInvalid = computed(() => {
  if (!selectedItemDetails.value) return false;
  return newRequest.value.quantity > selectedItemDetails.value.available;
});
const totalCost = computed(() => {
  if (!selectedItemDetails.value || !newRequest.value.borrowDate || !newRequest.value.returnDate || newRequest.value.quantity < 1) return 0;
  const date1 = new Date(newRequest.value.borrowDate);
  const date2 = new Date(newRequest.value.returnDate);
  if (date2 < date1) return 0;
  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const rentalDays = diffDays + 1;
  return selectedItemDetails.value.rate * newRequest.value.quantity * rentalDays;
});

async function handleCreateRequest() { // <-- Make async
  if (isQuantityInvalid.value) {
    alert('Cannot create request. Quantity exceeds available stock.');
    return;
  }
  if (totalCost.value <= 0) {
    alert('Invalid dates or quantity. Please check your inputs.');
    return;
  }

  // --- API CALL ---
  try {
    const payload = { ...newRequest.value, totalCost: totalCost.value };
    await createRequest(payload);
    
    alert(`New request created!`);
    
    // Reset form
    newRequest.value = {
      borrowerName: '', contactNumber: '', borrowDate: null, returnDate: null,
      purpose: null, notes: '', selectedItem: null, quantity: 1
    };
    
    // Tell the parent to refresh
    emit('request-created'); 
    
  } catch (error) {
    console.error('Failed to create request:', error);
    alert(`Error: ${error.message}`);
  }
  // --- END CALL ---
}
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      Create New Request (Admin)
    </h2>
    <p class="mb-6 text-gray-600">
      Fill out the form below to manually create a new equipment request 
      for a resident.
    </p>
    
    <form @submit.prevent="handleCreateRequest" class="space-y-4">
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Borrower Name</label>
          <input v-model="newRequest.borrowerName" type="text" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Contact Number</label>
          <input v-model="newRequest.contactNumber" type="tel" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
        </div>
         <div>
          <label class="block text-sm font-medium text-gray-700">Borrow Date</label>
          <input v-model="newRequest.borrowDate" type="date" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Return Date</label>
          <input v-model="newRequest.returnDate" type="date" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Item</label>
          <select 
            v-model="newRequest.selectedItem" 
            @change="newRequest.quantity = 1" 
            required 
            class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option disabled :value="null">Select an item</option>
            <option 
              v-for="item in inventory" 
              :key="item.id" 
              :value="item.id" 
              :disabled="item.available <= 0"
            >
              {{ item.name }}
            </option>
          </select>
        </div>
        <div>
          <div class="flex justify-between items-baseline">
            <label class="block text-sm font-medium text-gray-700">Quantity</label>
            <span v-if="selectedItemDetails" class="text-sm" :class="isQuantityInvalid ? 'text-red-600' : 'text-gray-500'">
              Available: {{ selectedItemDetails.available }}
            </span>
          </div>
          <input 
            v-model.number="newRequest.quantity" 
            type="number" 
            min="1"
            :max="selectedItemDetails ? selectedItemDetails.available : 1" 
            :disabled="!selectedItemDetails"
            required 
            class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': isQuantityInvalid }"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Total Fee (₱)</label>
          <input 
            :value="totalCost.toLocaleString()" 
            type="text" 
            disabled 
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100" 
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Purpose of Borrowing</label>
          <select v-model="newRequest.purpose" required class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
            <option disabled :value="null">Select a purpose</option>
            <option v-for="option in purposeOptions" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-3">
          <label class="block text-sm font-medium text-gray-700">Notes (Optional)</label>
          <textarea v-model="newRequest.notes" rows="2" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"></textarea>
        </div>
        
        <div class="w-full flex flex-col">
          <label class="block text-sm font-medium text-transparent select-none">Create</label>
          <button 
            type="submit" 
            :disabled="isQuantityInvalid || totalCost <= 0"
            class="w-full h-full px-6 py-2 bg-[#0957FF] text-white font-semibold rounded-md shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                   disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            Create Request
          </button>
        </div>
      </div>

    </form>
  </div>
</template>