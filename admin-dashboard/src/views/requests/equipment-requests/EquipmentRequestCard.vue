<script setup>
import { ref, computed, watch } from 'vue'
import { NPopover, NInput, NButton, NSpin } from 'naive-ui'
import { TrashIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/solid';
import { getNotes, updateNotes } from '@/api/equipmentService'

const notes = ref('')
const showNotesPopover = ref(false)
const showDetailsPopover = ref(false)
const isLoadingNotes = ref(false)
const isSavingNotes = ref(false)
const originalNotes = ref('')

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  transactionNo: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    validator: (value) => ['pending', 'approved', 'pickedup', 'returned', 'rejected'].includes(value)
  },
  requestType: {
    type: String,
    required: true
  },
  requester: {
    type: Object,
    required: true
  },
  rfidNo: {
    type: String,
    required: true
  },
  requestedOn: {
    type: String,
    required: true
  },
  borrowingPeriod: {
    type: Object,
    required: true,
    // { from: 'MM/DD/YY', to: 'MM/DD/YY' }
  },
  amount: {
    type: String,
    default: null
  },
  isPaid: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  contactPerson: {
    type: String,
    default: null
  },
  contactNumber: {
    type: String,
    default: null
  },
  purpose: {
    type: String,
    default: null
  },
});

// Load notes when popover opens
watch(showNotesPopover, async (isOpen) => {
  if (isOpen) {
    await loadNotes()
  }
})

const loadNotes = async () => {
  isLoadingNotes.value = true
  try {
    const { data } = await getNotes(props.id)
    notes.value = data.notes || ''
    originalNotes.value = data.notes || ''
  } catch (error) {
    console.error('Failed to load notes:', error)
    notes.value = ''
    originalNotes.value = ''
  } finally {
    isLoadingNotes.value = false
  }
}

const saveNotes = async () => {
  isSavingNotes.value = true
  try {
    const { data } = await updateNotes(props.id, notes.value)
    originalNotes.value = data.notes || ''
    
    // Emit success event
    emit('notes-updated', {
      requestId: props.id,
      notes: data.notes
    })
    
    showNotesPopover.value = false
  } catch (error) {
    console.error('Failed to save notes:', error)
    // Optionally show error notification here
  } finally {
    isSavingNotes.value = false
  }
}

const hasUnsavedChanges = computed(() => {
  return notes.value !== originalNotes.value
})

const emit = defineEmits(['button-click', 'update:isPaid', 'update:selected', 'notes-updated']);

const dueStatus = computed(() => {
  if (!props.borrowingPeriod?.to) return null;
  
  const dueDate = new Date(props.borrowingPeriod.to);
  const today = new Date();
  
  dueDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  
  if (props.status === 'pickedup') {
    if (dueDate < today) {
      return 'overdue'; // Past due and not yet returned
    } else if (dueDate.getTime() === today.getTime()) {
      return 'duetoday'; // Due today
    }
  }
  
  return null;
});

const buttonConfigs = {
  pending: [
    { id: 'details', label: 'Details', variant: 'primary' },
    { id: 'notes', label: 'Notes', variant: 'gray' },
    { id: 'approve', label: 'Approve', variant: 'green' },
    { id: 'reject', label: 'Reject', variant: 'red' },
    { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
  ],
  approved: [
    { id: 'details', label: 'Details', variant: 'primary' },
    { id: 'notes', label: 'Notes', variant: 'gray' },
    { id: 'notify', label: 'Notify', variant: 'solidgreen' },
    { id: 'release', label: 'Release', variant: 'green' },
    { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'undo' },
    { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
  ],
  pickedup: [
    { id: 'details', label: 'Details', variant: 'primary' },
    { id: 'notes', label: 'Notes', variant: 'gray' },
    { id: 'notify', label: 'Notify', variant: 'solidgreen' },
    { id: 'returned', label: 'Returned', variant: 'green' },
    { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'undo' },
    { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
  ],
  returned: [
    { id: 'details', label: 'Details', variant: 'primary' },
    { id: 'notes', label: 'Notes', variant: 'gray' },
    { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'undo' },
    { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
  ],
  rejected: [
    { id: 'details', label: 'Details', variant: 'primary' },
    { id: 'notes', label: 'Notes', variant: 'gray' },
    { id: 'notify', label: 'Notify', variant: 'solidgreen' },
    { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'undo' },
    { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
  ]
};

const visibleButtons = computed(() => {
  return buttonConfigs[props.status] || buttonConfigs.pending;
});

const isButtonDisabled = (btn) => {
  if (btn.id === 'approve' && props.status === 'pending' && props.amount && !props.isPaid) {
    return true;
  }
  return false;
};

const getButtonClass = (btn) => {
  const baseClasses = btn.label === '' ? 'px-2' : '';
  
  if (isButtonDisabled(btn)) {
    return `${baseClasses} bg-gray-100 text-gray-400 cursor-not-allowed`;
  }
  
  const variantClasses = {
    primary: 'bg-[#0957FF] text-white hover:bg-blue-700',
    gray: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
    green: 'bg-white text-green-600 border border-[#09AA44] hover:bg-green-50',
    solidgreen: 'bg-[#09AA44] text-white hover:bg-green-700',
    red: 'bg-white text-red-600 border border-[#FF2B3A] hover:bg-red-50',
    delete: 'bg-white text-[#B1202A] border border-[#FBBABA] hover:bg-[#FFE6E6]',
    undo: 'bg-white text-orange-500 border border-orange-400 hover:bg-orange-50'
  };
  
  return `${baseClasses} ${variantClasses[btn.variant] || variantClasses.gray}`;
};

const handleButtonClick = (buttonId, btn) => {
  if (buttonId === 'payment') {
    emit('update:isPaid', !props.isPaid);
    return;
  }
  
  if (btn && isButtonDisabled(btn)) {
    return;
  }
  
  emit('button-click', {
    action: buttonId,
    requestId: props.id,
    status: props.status
  });
};
</script>

<template>
  <div 
    class="rounded-lg border-l-[6px] border-l-[#0957FF] border p-5 flex items-start gap-4 transition-all relative"
    :class="[
      isSelected ? 'border-[#0957FF] ring-1 ring-[#0957FF]/10 shadow-sm bg-[#F0F5FF]' : 'border-[#CCCCCC] bg-white'
    ]"
  >
    <!-- Transaction Number -->
    <div class="flex flex-col items-center justify-center space-y-1">
      <div class="flex justify-center bg-[#F0F5FF] border border-[#D4DFF6] rounded px-4 py-1 min-w-[90px]">
        <div class="text-lg font-bold text-slate-700 leading-tight">{{ transactionNo }}</div>        
      </div>
      <div class="text-[9px] text-gray-400 font-medium">Transaction No.</div>
    </div>

    <!-- Details -->
    <div class="flex-1 flex flex-col gap-3">
      <!-- Request Type Name -->
      <h3 class="text-xl font-bold text-slate-800 leading-none">
        {{ requestType }}
      </h3>
      
      <!-- Request Details -->
      <div class="flex gap-16">

        <!-- Column 1 -->
        <div class="flex flex-col gap-3">
          <!-- Full Name -->
          <div class="flex flex-col">
            <span class="text-[11px] text-gray-400 font-medium">Request from</span>
            <span class="text-sm text-slate-700 font-bold">
              {{ requester.firstName }} {{ requester.middleName }} {{ requester.lastName }}
            </span>
          </div>

          <!-- RFID No. -->
          <div class="flex flex-col">
            <span class="text-[11px] text-gray-400 font-medium">RFID No.</span>
            <span class="text-sm font-bold text-blue-600">
              {{ rfidNo }}
            </span>
          </div>
        </div>

        <!-- Column 2 -->
        <div class="flex flex-col gap-3">
          <!-- Requested Date -->
          <div class="flex flex-col">
            <span class="text-[11px] text-gray-400 font-medium">Requested on</span>
            <span class="text-sm text-slate-700 font-bold">{{ requestedOn }}</span>
          </div>

          <!-- Borrowing Period -->
          <div class="flex flex-col">
            <span class="text-[11px] text-gray-400 font-medium">Borrowing Period</span>
            <div class="flex items-center gap-2">
              <span class="text-sm text-slate-700 font-bold">
                {{ borrowingPeriod.from }} - {{ borrowingPeriod.to }}
              </span>
              <span 
                v-if="dueStatus === 'overdue'" 
                class="px-2 py-0.5 bg-red-100 text-red-600 rounded text-[10px] font-bold uppercase"
              >
                Past Due
              </span>
              <span 
                v-else-if="dueStatus === 'duetoday'" 
                class="px-2 py-0.5 bg-green-100 text-green-600 rounded text-[10px] font-bold uppercase"
              >
                Due Today
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Buttons -->
    <div class="flex flex-col items-end gap-4 min-w-fit">

      <!-- Checkbox -->
      <div class="flex items-center gap-3">
        <input 
          type="checkbox" 
          :checked="isSelected"
          @change="$emit('update:selected', $event.target.checked)"
          class="w-4 h-4 border-gray-300 rounded accent-[#0957FF] cursor-pointer"
        />
      </div>

      <!-- Payment Status -->
      <div v-if="amount" class="flex items-center gap-3">
        <button
          v-if="status === 'pending'"
          @click="handleButtonClick('payment')"
          :class="[
            'px-2 py-0.5 rounded text-[10px] font-bold uppercase transition-colors',
            isPaid ? 'bg-green-100 text-[#09AA44]' : 'bg-gray-200 text-gray-500'
          ]"
        >
          {{ isPaid ? 'Paid' : 'Mark as Paid' }}
        </button>
        <div 
          v-else-if="isPaid" 
          class="px-2 py-0.5 bg-green-100 text-[#09AA44] rounded text-[10px] font-bold uppercase"
        >
          Paid
        </div>

        <div class="text-2xl font-black text-[#09AA44] flex items-center">
          <span class="text-lg mr-1">₱</span> {{ amount }}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2">
        <template v-for="btn in visibleButtons" :key="btn.id">
          <!-- Details Button -->
          <n-popover
            v-if="btn.id === 'details'"
            trigger="click"
            placement="bottom-end"
            v-model:show="showDetailsPopover"
            :show-arrow="false"
          >
            <template #trigger>
              <button
                :class="[getButtonClass(btn), 'px-4']"
                class="h-9 rounded-md text-sm font-semibold flex items-center justify-center"
              >
                {{ btn.label }}
              </button>
            </template>

            <div class="w-80 p-3 space-y-3">
              <h3 class="text-sm font-bold text-slate-800 mb-3 pb-2 border-b border-gray-200">
                Request Details
              </h3>
              
              <div class="space-y-3">
                <!-- Contact Person -->
                <div class="flex flex-col">
                  <span class="text-xs text-gray-500 font-medium mb-1">Contact Person</span>
                  <span class="text-sm text-slate-700">
                    {{ contactPerson || 'Not provided' }}
                  </span>
                </div>

                <!-- Contact Number -->
                <div class="flex flex-col">
                  <span class="text-xs text-gray-500 font-medium mb-1">Contact Number</span>
                  <span class="text-sm text-slate-700">
                    {{ contactNumber || 'Not provided' }}
                  </span>
                </div>

                <!-- Purpose -->
                <div class="flex flex-col">
                  <span class="text-xs text-gray-500 font-medium mb-1">Purpose</span>
                  <span class="text-sm text-slate-700">
                    {{ purpose || 'Not provided' }}
                  </span>
                </div>
              </div>
            </div>
          </n-popover>

          <!-- Notes Button -->
          <n-popover
            v-else-if="btn.id === 'notes'"
            trigger="click"
            placement="bottom-end"
            v-model:show="showNotesPopover"
            :show-arrow="false"
          >
            <template #trigger>
              <button
                :class="[getButtonClass(btn), 'px-4']"
                class="h-9 rounded-md text-sm font-semibold flex items-center justify-center"
              >
                {{ btn.label }}
              </button>
            </template>

            <div class="flex w-72 p-1 gap-3 items-center">
              <n-spin :show="isLoadingNotes" size="small" class="flex-1">
                <n-input
                  v-model:value="notes"
                  type="textarea"
                  size="medium"
                  placeholder="Add notes..."
                  class="h-9"
                  :disabled="isLoadingNotes"
                />
              </n-spin>
              <n-button
                size="small"
                type="primary"
                @click="saveNotes"
                :disabled="!hasUnsavedChanges || isSavingNotes"
                :loading="isSavingNotes"
              >
                Save
              </n-button>
            </div>
          </n-popover>

          <!-- Other Buttons -->
          <button
            v-else
            @click="handleButtonClick(btn.id, btn)"
            :disabled="isButtonDisabled(btn)"
            :class="[
              getButtonClass(btn),
              ['delete', 'undo'].includes(btn.id) ? 'w-9 px-0' : 'px-4'
            ]"
            class="h-9 rounded-md text-sm font-semibold transition-all flex items-center justify-center"
          >
            {{ btn.label }}
            <component v-if="!btn.label" :is="btn.icon" class="w-5 h-5" />
          </button>
        </template>
      </div>
    </div>
  </div>
</template>