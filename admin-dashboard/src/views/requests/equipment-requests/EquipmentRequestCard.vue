<script setup>
import { computed } from 'vue';
import { TrashIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/solid';

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
  }
});

const emit = defineEmits(['button-click', 'update:isPaid', 'update:selected']);

const isPastDue = computed(() => {
  if (!props.borrowingPeriod?.to) return false;
  const dueDate = new Date(props.borrowingPeriod.to);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dueDate < today;
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
    <div class="flex flex-col items-center justify-center space-y-1">
      <div class="flex justify-center bg-[#F0F5FF] border border-[#D4DFF6] rounded px-4 py-1 min-w-[90px]">
        <div class="text-lg font-bold text-slate-700 leading-tight">{{ transactionNo }}</div>        
      </div>
      <div class="text-[9px] text-gray-400 font-medium">Transaction No.</div>
    </div>

    <div class="flex-1 flex flex-col gap-3">
      <h3 class="text-xl font-bold text-slate-800 leading-none">
        {{ requestType }}
      </h3>
      
      <div class="flex gap-16">
        <div class="flex flex-col">
          <span class="text-[11px] text-gray-400 font-medium">Request from</span>
          <span class="text-sm text-slate-700 font-bold">
            {{ requester.firstName }} {{ requester.middleName }} {{ requester.lastName }}
          </span>
        </div>

        <div class="flex flex-col">
          <span class="text-[11px] text-gray-400 font-medium">RFID No.</span>
          <span class="text-sm font-bold text-blue-600">
            {{ rfidNo }}
          </span>
        </div>
      </div>

      <div class="flex gap-16">
        <div class="flex flex-col">
          <span class="text-[11px] text-gray-400 font-medium">Requested on</span>
          <span class="text-sm text-slate-700 font-bold">{{ requestedOn }}</span>
        </div>

        <div class="flex flex-col">
          <span class="text-[11px] text-gray-400 font-medium">Borrowing Period</span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-slate-700 font-bold">
              {{ borrowingPeriod.from }} - {{ borrowingPeriod.to }}
            </span>
            <span 
              v-if="isPastDue" 
              class="px-2 py-0.5 bg-red-100 text-red-600 rounded text-[10px] font-bold uppercase"
            >
              Past Due
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-col items-end gap-4 min-w-fit">
      <div class="flex items-center gap-3">
        <input 
          type="checkbox" 
          :checked="isSelected"
          @change="$emit('update:selected', $event.target.checked)"
          class="w-4 h-4 border-gray-300 rounded accent-[#0957FF] cursor-pointer"
        />
      </div>

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

      <div class="flex items-center gap-2">
        <button
          v-for="btn in visibleButtons"
          :key="btn.id"
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
      </div>
    </div>
  </div>
</template>