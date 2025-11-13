<script setup>
import { ref, computed, onMounted } from 'vue';
import {
  MagnifyingGlassIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  CheckIcon,
  CurrencyDollarIcon,
} from '@heroicons/vue/24/outline'; 
import { 
  getRequests, 
  markAsPaid, 
  approveRequest, 
  rejectRequest,
  markAsPickedUp,
  markAsReturned,
  issueRefund
} from '@/api/equipmentApi';

const currentTab = ref('Pending');
const searchQuery = ref('');
const allRequests = ref([]);
const isLoading = ref(true);

async function fetchRequests() {
  isLoading.value = true;
  try {
    const data = await getRequests();
    allRequests.value = data.map(req => ({
      id: req.id,
      status: req.status,
      paid: req.paid,
      refunded: req.refunded,
      borrowerName: req.borrower_name,
      contactNumber: req.contact_number,
      requestedVia: req.requested_via, // This will now be "Kiosk" or "Admin"
      requestDate: new Date(req.created_at).toLocaleDateString(),
      borrowDate: new Date(req.borrow_date).toLocaleDateString(),
      returnDate: new Date(req.return_date).toLocaleDateString(),
      items: (req.items || []).map(item => ({
        id: item.item.id,
        name: item.item.name,
        quantity: item.quantity,
        rate: item.item.rate
      })),
      totalCost: req.total_cost,
      purpose: req.purpose,
      notes: req.notes,
    }));
  } catch (error) {
    console.error('Failed to fetch requests:', error);
    alert('Error: Could not load requests from the server.');
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchRequests);

const filteredRequests = computed(() => {
  let requests = allRequests.value.filter(req => req.status === currentTab.value);
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    requests = requests.filter(req =>
      req.id.toString().toLowerCase().includes(query) ||
      req.borrowerName.toLowerCase().includes(query) ||
      (req.items && req.items.some(item => item.name.toLowerCase().includes(query)))
    );
  }
  return requests;
});

const formatItems = (items) => {
  if (!items || items.length === 0) return 'No items';
  return items.map(item => `${item.quantity}x ${item.name}`).join(', ');
};

// --- Action Handlers (no changes needed) ---
async function handleMarkAsPaid(request) {
  try {
    await markAsPaid(request.id);
    request.paid = true;
    alert('Request marked as paid.');
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}
async function handleApprove(request) { 
  try {
    await approveRequest(request.id);
    request.status = 'Approved';
    alert('Request approved.');
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}
async function handleReject(request) { 
  try {
    await rejectRequest(request.id);
    request.status = 'Rejected';
    alert('Request rejected. Stock will be returned.');
    await fetchRequests(); 
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}
async function handlePickedUp(request) { 
  try {
    await markAsPickedUp(request.id);
    request.status = 'Picked-Up';
    alert('Request marked as picked up.');
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}
async function handleReturned(request) { 
  try {
    await markAsReturned(request.id);
    request.status = 'Returned';
    alert('Request marked as returned. Stock updated.');
    await fetchRequests(); 
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}
async function handleRefund(request) { 
  try {
    await issueRefund(request.id);
    request.refunded = true;
    alert('Refund issued.');
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

// MODIFIED: Simplified the handleViewDetails
const handleViewDetails = (request) => { 
  const details = [
    `--- Request Details (ID: ${request.id}) ---`,
    ``,
    `Borrower: ${request.borrowerName}`,
    `Contact Number: ${request.contactNumber || 'N/A'}`,
    `Requested Via: ${request.requestedVia}`, // This will now just say "Kiosk" or "Admin"
    ``,
    `Equipment: ${formatItems(request.items)}`,
    `Borrow Date: ${request.borrowDate}`,
    `Return Date: ${request.returnDate}`,
    ``,
    `Purpose: ${request.purpose}`,
    `Notes: ${request.notes || 'N/A'}`,
    ``,
    `Total Fee: ₱${request.totalCost.toLocaleString()}`,
    ``,
    `Status: ${request.status}`,
    `Paid: ${request.paid ? 'Yes' : 'No'}`,
    `Refunded: ${request.refunded ? 'Yes' : 'No'}`
  ];
  
  alert(details.join('\n'));
};
// --- END MODIFICATION ---

const tabs = ['Pending', 'Approved', 'Picked-Up', 'Returned', 'Rejected'];
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-200 pb-4 mb-6 gap-4">
      <nav class="flex space-x-4 sm:space-x-8 -mb-px overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab"
          @click="currentTab = tab"
          :class="[
            'whitespace-nowrap pb-3 px-1 border-b-2 text-sm font-medium',
            currentTab === tab
              ? 'border-[#0957FF] text-[#0957FF]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab }}
        </button>
      </nav>
      <div class="relative w-full md:w-auto flex-shrink-0">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search requests..."
          class="pl-10 pr-4 py-2 border rounded-md w-full md:w-64 focus:ring-blue-500 focus:border-blue-500"
        />
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-10 text-gray-500">
      <p>Loading requests...</p>
    </div>

    <div v-else class="space-y-4">
      <div v-if="filteredRequests.length === 0" class="text-center py-10 text-gray-500">
        No {{ currentTab }} requests found.
      </div>

      <div
        v-for="(request, index) in filteredRequests"
        :key="request.id"
        class="relative bg-white border border-gray-200 rounded-lg p-5 flex flex-col sm:flex-row items-start justify-between shadow-sm transition-all hover:shadow-md"
      >
        <div class="absolute -left-2 top-1/2 -translate-y-1/2 h-full w-2 rounded-l-md"
             :class="{
               'bg-yellow-500': request.status === 'Pending',
               'bg-blue-500': request.status === 'Approved',
               'bg-indigo-500': request.status === 'Picked-Up',
               'bg-green-500': request.status === 'Returned',
               'bg-red-500': request.status === 'Rejected',
             }">
        </div>
        <div class="text-xs font-semibold text-gray-700 absolute -top-2 -left-1 bg-white px-2 py-1 rounded-full border border-gray-200 shadow-sm">
          {{ index + 1 }}
        </div>

        <div class="flex-grow grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 mb-4 sm:mb-0">
          
          <div class="col-span-2 text-lg font-semibold text-gray-800">
            {{ formatItems(request.items) }}
          </div>
          
          <div class="text-sm text-gray-600">
            <span class="font-medium">Requested by:</span> {{ request.borrowerName }}
          </div>
          
          <div class="text-sm text-gray-600">
            <span class="font-medium">Requested on:</span> {{ request.requestDate }}
          </div>
          
          <div class="text-sm text-gray-600">
             <span class="font-medium">Borrow Dates:</span> {{ request.borrowDate }} - {{ request.returnDate }}
          </div>
          
          <div class="text-sm">
            <span class="font-medium text-gray-600">Requested via: </span>
            
            <span v-if="request.requestedVia === 'Admin'" class="font-semibold text-purple-600">
              Admin
            </span>
            
            <span v-else class="font-semibold text-amber-600">
              Kiosk
            </span>
          </div>
          </div>

        <div class="flex-shrink-0 w-full sm:w-64 sm:ml-4 flex flex-col items-end space-y-2">
          <div class="text-xl font-bold text-green-700">₱{{ request.totalCost.toLocaleString() }}</div>
          <div class="flex flex-wrap gap-2 justify-end">
            
            <button @click="handleViewDetails(request)" class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md border border-gray-300 hover:bg-gray-200 flex items-center gap-1">
              <EyeIcon class="w-4 h-4" /> Details
            </button>

            <template v-if="request.status === 'Pending'">
              
              <button 
                v-if="!request.paid" 
                @click="handleMarkAsPaid(request)" 
                class="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 flex items-center gap-1"
              >
                <CurrencyDollarIcon class="w-4 h-4" /> Mark as Paid
              </button>
              
              <span 
                v-if="request.paid" 
                class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-md flex items-center gap-1"
              >
                <CheckCircleIcon class="w-4 h-4" /> Paid
              </span>
              
              <button 
                @click="handleApprove(request)" 
                :disabled="!request.paid" 
                class="px-3 py-1 text-sm bg-green-500 text-white rounded-md hover:bg-green-600 flex items-center gap-1
                       disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <CheckCircleIcon class="w-4 h-4" /> Approve
              </button>
              
              <button 
                @click="handleReject(request)" 
                class="px-3 py-1 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 flex items-center gap-1"
              >
                <XCircleIcon class="w-4 h-4" /> Reject
              </button>
            </template>

            <template v-else-if="request.status === 'Approved'">
               <button @click="handlePickedUp(request)" class="px-3 py-1 text-sm bg-indigo-500 text-white rounded-md hover:bg-indigo-600 flex items-center gap-1">
                 <CheckIcon class="w-4 h-4" /> Mark as Picked-Up
               </button>
            </template>

            <template v-else-if="request.status === 'Picked-Up'">
              <button @click="handleReturned(request)" class="px-3 py-1 text-sm bg-green-500 text-white rounded-md hover:bg-green-600 flex items-center gap-1">
                <CheckIcon class="w-4 h-4" /> Mark as Returned
              </button>
            </template>

            <template v-else-if="request.status === 'Rejected'">
              <template v-if="request.paid">
                <button 
                  v-if="!request.refunded" 
                  @click="handleRefund(request)" 
                  class="px-3 py-1 text-sm bg-orange-500 text-white rounded-md hover:bg-orange-600 flex items-center gap-1"
                >
                  <CurrencyDollarIcon class="w-4 h-4" /> Issue Refund
                </button>
                <span 
                  v-if="request.refunded" 
                  class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md flex items-center gap-1"
                >
                  <CheckCircleIcon class="w-4 h-4" /> Refunded
                </span>
              </template>
            </template>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>