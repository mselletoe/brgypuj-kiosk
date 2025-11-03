<script setup>
import { ref, computed } from 'vue';
import {
  MagnifyingGlassIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  CheckIcon,
  CurrencyDollarIcon,
} from '@heroicons/vue/24/outline'; 

const currentTab = ref('Pending'); // The "sub-tab"
const searchQuery = ref('');

const allRequests = ref([
  // --- 6 Pending Samples ---
  {
    id: 'EQ-001',
    status: 'Pending',
    paid: false, 
    refunded: false,
    borrowerName: 'Juan Dela Cruz',
    contactNumber: '09171234567',
    requestedVia: { type: 'RFID', id: '123456789' },
    requestDate: 'October 30, 2025',
    borrowDate: 'November 1, 2025',
    returnDate: 'November 3, 2025',
    items: [{ id: 1, name: 'Event Tent', quantity: 1, rate: 500 }, { id: 2, name: 'Monobloc Chairs', quantity: 50, rate: 10 }],
    totalCost: 3000,
    purpose: 'Birthday party',
    notes: 'Need assistance for setup.',
  },
  {
    id: 'EQ-002',
    status: 'Pending',
    paid: false, 
    refunded: false,
    borrowerName: 'Maria Santos',
    contactNumber: '09209876543',
    requestedVia: { type: 'Guest User' },
    requestDate: 'October 29, 2025',
    borrowDate: 'November 5, 2025',
    returnDate: 'November 5, 2025',
    items: [{ id: 4, name: 'Sound System', quantity: 1, rate: 300 }],
    totalCost: 300,
    purpose: 'Community event',
    notes: null,
  },
  {
    id: 'EQ-003',
    status: 'Pending',
    paid: true, 
    refunded: false,
    borrowerName: 'Pedro Reyes',
    contactNumber: '09351112222',
    requestedVia: { type: 'RFID', id: '987654321' },
    requestDate: 'October 28, 2025',
    borrowDate: 'November 10, 2025',
    returnDate: 'November 11, 2025',
    items: [{ id: 3, name: 'Folding Tables', quantity: 3, rate: 1500 }],
    totalCost: 9000,
    purpose: 'Presentation',
    notes: 'Will pick up in the afternoon.',
  },
  {
    id: 'EQ-004',
    status: 'Pending',
    paid: false, 
    refunded: false,
    borrowerName: 'Anna Lim',
    contactNumber: '09001230000',
    requestedVia: { type: 'Guest User' },
    requestDate: 'October 28, 2025',
    borrowDate: 'November 12, 2025',
    returnDate: 'November 12, 2025',
    items: [{ id: 2, name: 'Monobloc Chairs', quantity: 100, rate: 10 }],
    totalCost: 1000,
    purpose: 'Personal Event',
    notes: null,
  },
    {
    id: 'EQ-005',
    status: 'Pending',
    paid: false, 
    refunded: false,
    borrowerName: 'Mark Lee',
    contactNumber: '09123456789',
    requestedVia: { type: 'RFID', id: '112233445' },
    requestDate: 'October 27, 2025',
    borrowDate: 'November 15, 2025',
    returnDate: 'November 16, 2025',
    items: [{ id: 4, name: 'Sound System', quantity: 2, rate: 300 }],
    totalCost: 1200,
    purpose: 'Barangay Event',
    notes: null,
  },
  {
    id: 'EQ-006',
    status: 'Pending',
    paid: false, 
    refunded: false,
    borrowerName: 'Jose Rizal',
    contactNumber: '09112223333',
    requestedVia: { type: 'RFID', id: '18611896' },
    requestDate: 'October 26, 2025',
    borrowDate: 'November 20, 2025',
    returnDate: 'November 22, 2025',
    items: [{ id: 1, name: 'Event Tent', quantity: 2, rate: 500 }],
    totalCost: 3000,
    purpose: 'Emergency Use',
    notes: 'Urgent',
  },

  // --- Other Statuses ---
  { 
    id: 'EQ-007', 
    status: 'Approved', 
    paid: true, 
    refunded: false,
    borrowerName: 'Clara Kim', 
    contactNumber: '09223334444',
    requestedVia: { type: 'Guest User' },
    items: [ { id: 4, name: 'Sound System', quantity: 1, rate: 300 } ], 
    totalCost: 600,
    purpose: 'Community Meeting',
    notes: null,
  },
  { 
    id: 'EQ-008', 
    status: 'Approved', 
    paid: true, 
    refunded: false,
    borrowerName: 'Ben Ten',
    contactNumber: '09334445555',
    requestedVia: { type: 'RFID', id: '10101010' },
    items: [ { id: 2, name: 'Monobloc Chairs', quantity: 50, rate: 10 } ],
    totalCost: 1000,
    purpose: 'Barangay Event',
    notes: null,
  },
  { 
    id: 'EQ-009', 
    status: 'Picked-Up', 
    paid: true, 
    refunded: false,
    borrowerName: 'Son Goku',
    contactNumber: '09445556666',
    requestedVia: { type: 'RFID', id: '90009000' },
    items: [ { id: 1, name: 'Event Tent', quantity: 2, rate: 500 } ],
    totalCost: 3000,
    purpose: 'Personal Event',
    notes: null,
  },
  { 
    id: 'EQ-010', 
    status: 'Returned', 
    paid: true, 
    refunded: false,
    borrowerName: 'Jane Doe',
    contactNumber: '09556667777',
    requestedVia: { type: 'Guest User' },
    items: [ { id: 3, name: 'Folding Tables', quantity: 4, rate: 1500 } ],
    totalCost: 18000,
    purpose: 'Community Meeting',
    notes: 'One table has a scratch.',
  },
  { 
    id: 'EQ-011', 
    status: 'Rejected', 
    paid: true,
    refunded: false,
    borrowerName: 'V. Putin',
    contactNumber: '09667778888',
    requestedVia: { type: 'RFID', id: '00000001' },
    items: [ { id: 1, name: 'Event Tent', quantity: 10, rate: 500 } ],
    totalCost: 10000,
    purpose: 'Personal Event',
    notes: 'Rejected due to lack of available stock.',
  },
  { 
    id: 'EQ-012', 
    status: 'Rejected', 
    paid: true,
    refunded: true,
    borrowerName: 'S. Smith',
    contactNumber: '09778889999',
    requestedVia: { type: 'Guest User' },
    items: [ { id: 3, name: 'Folding Tables', quantity: 2, rate: 1500 } ],
    totalCost: 3000,
    purpose: 'Personal Event',
    notes: 'Refund processed.',
  },
]);

const filteredRequests = computed(() => {
  let requests = allRequests.value.filter(req => req.status === currentTab.value);

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    requests = requests.filter(req =>
      req.id.toLowerCase().includes(query) ||
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

// --- Action Handlers ---
const handleMarkAsPaid = (request) => {
  console.log('API call to mark paid', request.id);
  request.paid = true;
};
const handleApprove = (request) => { 
  console.log('API call to approve', request.id);
  request.status = 'Approved'; 
};
const handleReject = (request) => { 
  console.log('API call to reject', request.id);
  request.status = 'Rejected'; 
};
const handlePickedUp = (request) => { 
  console.log('API call to mark picked-up', request.id);
  request.status = 'Picked-Up'; 
};
const handleReturned = (request) => { 
  console.log('API call to mark returned', request.id);
  request.status = 'Returned'; 
};
const handleRefund = (request) => { 
  console.log('API call to process refund for', request.id);
  request.refunded = true; 
};
const handleViewDetails = (request) => { 
  const via = request.requestedVia.type === 'RFID' 
    ? `RFID (${request.requestedVia.id})` 
    : 'Guest User';

  const details = [
    `--- Request Details (ID: ${request.id}) ---`,
    ``,
    `Borrower: ${request.borrowerName}`,
    `Contact Number: ${request.contactNumber || 'N/A'}`,
    `Requested Via: ${via}`,
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

    <div class="space-y-4">
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
            
            <span v-if="request.requestedVia.type === 'RFID'" class="inline-flex items-center space-x-2">
              <span class="font-semibold text-gray-700">RFID</span>
              <span class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-500 text-white">
                {{ request.requestedVia.id }}
              </span>
            </span>
            
            <span v-else-if="request.requestedVia.type === 'Guest User'" class="font-semibold text-amber-600">
              Guest User
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