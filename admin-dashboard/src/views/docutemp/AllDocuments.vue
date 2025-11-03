<script setup>
import { ref } from 'vue';
import { PencilIcon, ArchiveBoxIcon, TrashIcon } from '@heroicons/vue/24/outline';

// Dummy data for the list
const documents = ref([
  {
    id: 1,
    name: 'Barangay Clearance',
    created: 'May 2, 2023',
    modified: '19 hours ago',
    status: 'Available',
    statusColor: 'bg-green-500' // <-- This controls the bar color
  },
  {
    id: 2,
    name: 'Cedula (Community Tax Certificate)',
    created: 'November 19, 2020',
    modified: 'December 13, 2020',
    status: 'Out of Stock',
    statusColor: 'bg-red-500' // <-- This controls the bar color
  },
  {
    id: 3,
    name: 'Business Permit',
    created: 'January 5, 2024',
    modified: '3 days ago',
    status: 'Available',
    statusColor: 'bg-green-500' // <-- This controls the bar color
  },
]);

// --- Action Handlers ---
function handleEdit(doc) {
  console.log('Editing:', doc.name);
  alert(`Editing "${doc.name}"...`);
}

function handleArchive(doc) {
  console.log('Archiving:', doc.name);
  alert(`Archiving "${doc.name}"...`);
  documents.value = documents.value.filter(d => d.id !== doc.id);
}

function handleDelete(doc) {
  console.log('Deleting:', doc.name);
  if (confirm(`Are you sure you want to delete "${doc.name}"?`)) {
    documents.value = documents.value.filter(d => d.id !== doc.id);
  }
}
</script>

<template>
  <div class="flow-root">
    <div class="border-b border-gray-200">
      <div class="hidden md:grid grid-cols-12 gap-4 px-4 py-2 text-sm font-medium text-gray-500">
        <div class="col-span-4">Document Name</div>
        <div class="col-span-2">Created On</div>
        <div class="col-span-2">Last Modified</div>
        <div class="col-span-1">Status</div>
        <div class="col-span-3 text-right">Actions</div>
      </div>
    </div>

    <div class="divide-y divide-gray-200">
      <div 
        v-for="doc in documents" 
        :key="doc.id" 
        class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center px-4 py-3"
      >
        
        <div class="md:col-span-4 flex items-center gap-3">
          <div 
            class="w-1.5 h-8 rounded-full" 
            :class="doc.statusColor"
          ></div>
          <span class="text-base font-bold text-gray-900">{{ doc.name }}</span>
        </div>
        
        <div class="md:col-span-2 text-sm text-gray-600">
          <span class="md:hidden font-medium">Created: </span>
          {{ doc.created }}
        </div>
        
        <div class="md:col-span-2 text-sm text-gray-600">
          <span class="md:hidden font-medium">Modified: </span>
          {{ doc.modified }}
        </div>
        
        <div class="md:col-span-1 text-sm">
          <span 
            class="px-2 py-1 rounded-full text-xs font-medium"
            :class="doc.status === 'Available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
          >
            {{ doc.status }}
          </span>
        </div>
        
        <div class="md:col-span-3 flex justify-end gap-2 mt-2 md:mt-0">
          <button 
            @click="handleArchive(doc)"
            class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-white border rounded-md shadow-sm transition-colors border-yellow-500 text-yellow-600 hover:bg-yellow-50"
          >
            <ArchiveBoxIcon class="w-4 h-4" />
            Archive
          </button>
          <button 
            @click="handleEdit(doc)"
            class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-white border rounded-md shadow-sm transition-colors border-green-500 text-green-600 hover:bg-green-50"
          >
            <PencilIcon class="w-4 h-4" />
            Edit
          </button>
          <button 
            @click="handleDelete(doc)"
            class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-white border rounded-md shadow-sm transition-colors border-red-500 text-red-600 hover:bg-red-50"
          >
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>