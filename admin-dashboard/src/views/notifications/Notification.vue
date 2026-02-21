<script setup>
import { ref, computed } from 'vue';

const searchQuery = ref('');
const statusFilter = ref('All Status');
const typeFilter = ref('All Types');

// Mock data
const notifications = ref([
  { id: 1, type: 'Document', msg: 'New Document Request', date: 'Jan 30, 2026', time: '10:55 AM', unread: true, selected: false },
  { id: 2, type: 'Document', msg: 'New Document Request', date: 'Jan 30, 2026', time: '10:55 AM', unread: true, selected: false },
  { id: 3, type: 'Document', msg: 'New Document Request', date: 'Jan 30, 2026', time: '10:55 AM', unread: true, selected: false },
  { id: 4, type: 'Payment', msg: 'Payment Completed', date: 'Jan 30, 2026', time: '10:55 AM', unread: false, selected: false },
  { id: 5, type: 'Equipment', msg: 'Equipment Overdue', date: 'Jan 30, 2026', time: '10:55 AM', unread: true, selected: false },
  { id: 6, type: 'Feedback', msg: 'New Feedback Received', date: 'Jan 30, 2026', time: '10:55 AM', unread: false, selected: false },
  { id: 7, type: 'Payment', msg: 'Payment Received', date: 'Jan 30, 2026', time: '10:55 AM', unread: true, selected: false },
  { id: 8, type: 'Feedback', msg: 'New Feedback Received', date: 'Jan 30, 2026', time: '10:55 AM', unread: false, selected: false }
]);

// Computed property to handle filtering
const filteredNotifications = computed(() => {
  return notifications.value.filter(n => {
    const searchLower = searchQuery.value.toLowerCase();
    const matchesSearch = searchLower === '' || 
                          n.msg.toLowerCase().includes(searchLower) || 
                          n.type.toLowerCase().includes(searchLower);
    
    const matchesStatus = statusFilter.value === 'All Status' ||
                          (statusFilter.value === 'Unread' && n.unread) ||
                          (statusFilter.value === 'Read' && !n.unread);
                          
    const matchesType = typeFilter.value === 'All Types' || n.type === typeFilter.value;

    return matchesSearch && matchesStatus && matchesType;
  });
});

// Writable Computed Property for Select All (The Magic Fix)
const isAllSelected = computed({
  get() {
    // Returns true if there are items and EVERY item is selected
    return filteredNotifications.value.length > 0 && filteredNotifications.value.every(n => n.selected);
  },
  set(value) {
    // When the header checkbox is clicked, apply the boolean value to all currently filtered items
    filteredNotifications.value.forEach(n => {
      n.selected = value;
    });
  }
});

// Triggered by the toolbar button
const toolbarToggleSelectAll = () => {
  isAllSelected.value = !isAllSelected.value;
};

const markAllAsRead = () => {
  notifications.value.forEach(n => {
    n.unread = false;
    n.selected = false;
  });
};

const markSelectedAsRead = () => {
  filteredNotifications.value.forEach(n => {
    if (n.selected) {
      n.unread = false;
      n.selected = false; // Deselect after marking read
    }
  });
};

const deleteSelected = () => {
  // Keep only the items that are NOT selected
  notifications.value = notifications.value.filter(n => !n.selected);
};
</script>

<template>
  <div class="flex flex-col p-8 bg-[#f8f9fa] w-full h-full overflow-y-auto font-sans">
    
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-8 min-h-[calc(100vh-140px)]">
      
      <div class="flex flex-col xl:flex-row xl:items-center justify-between mb-8 gap-4">
        
        <div>
          <h1 class="text-[22px] font-bold text-gray-900">All Notifications</h1>
          <p class="text-gray-500 text-[14px] mt-1">View and manage all system notifications</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          
          <div class="relative">
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="Search Notifications..." 
              class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 text-[13px] w-56 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400" 
            />
          </div>

          <select 
            v-model="statusFilter"
            class="border border-gray-200 text-gray-600 rounded-md py-2 pl-3 pr-8 text-[13px] focus:outline-none focus:border-blue-500 bg-white cursor-pointer appearance-none relative"
            style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
          >
            <option>All Status</option>
            <option>Unread</option>
            <option>Read</option>
          </select>

          <select 
            v-model="typeFilter"
            class="border border-gray-200 text-gray-600 rounded-md py-2 pl-3 pr-8 text-[13px] focus:outline-none focus:border-blue-500 bg-white cursor-pointer appearance-none"
            style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
          >
            <option>All Types</option>
            <option>Document</option>
            <option>Payment</option>
            <option>Equipment</option>
            <option>Feedback</option>
          </select>

          <button @click="toolbarToggleSelectAll" title="Toggle Select All" class="p-2 border border-gray-200 rounded-md text-gray-500 hover:bg-gray-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <button @click="deleteSelected" title="Delete Selected" class="p-2 border border-gray-200 rounded-md text-red-500 hover:bg-red-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>

          <button @click="markSelectedAsRead" title="Mark Selected as Read" class="p-2 border border-gray-200 rounded-md text-[#0d6efd] hover:bg-blue-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </button>

          <button @click="markAllAsRead" class="bg-[#0d6efd] text-white px-5 py-2 rounded-md text-[13px] font-medium hover:bg-blue-700 transition-colors ml-2">
            Mark All as Read
          </button>
        </div>
      </div>

      <div class="w-full">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="py-4 px-6 w-12 text-center">
                <input 
                  type="checkbox" 
                  v-model="isAllSelected" 
                  class="w-4 h-4 rounded text-[#0d6efd] focus:ring-[#0d6efd] border-gray-300 cursor-pointer" 
                />
              </th>
              <th class="py-4 px-6 text-[11px] font-bold text-gray-800 uppercase tracking-wider w-[20%]">Type</th>
              <th class="py-4 px-6 text-[11px] font-bold text-gray-800 uppercase tracking-wider w-[45%]">Notification</th>
              <th class="py-4 px-6 text-[11px] font-bold text-gray-800 uppercase tracking-wider">Date & Time</th>
              <th class="py-4 px-6 w-12"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredNotifications.length === 0">
              <td colspan="5" class="py-12 text-center text-gray-500 text-[13px]">
                No notifications match your current filters.
              </td>
            </tr>
            <tr 
              v-for="n in filteredNotifications" 
              :key="n.id" 
              @click="n.unread = false"
              class="border-b border-gray-100 last:border-none transition-colors cursor-pointer"
              :class="n.unread ? 'bg-[#f0f7ff] hover:bg-blue-50' : 'hover:bg-gray-50'"
            >
              <td class="py-4 px-6 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  v-model="n.selected" 
                  class="w-4 h-4 rounded text-[#0d6efd] focus:ring-[#0d6efd] border-gray-300 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-6 text-[13px] text-gray-600">{{ n.type }}</td>
              <td class="py-4 px-6 text-[13px] font-medium text-gray-800">{{ n.msg }}</td>
              <td class="py-4 px-6 text-[13px] text-gray-600 flex items-center">
                <span class="w-[100px] inline-block">{{ n.date }}</span> 
                <span>{{ n.time }}</span>
              </td>
              <td class="py-4 px-6 text-center">
                <div v-if="n.unread" class="w-1.5 h-1.5 bg-[#0d6efd] rounded-full mx-auto"></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>