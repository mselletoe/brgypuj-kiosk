<script setup>
import { computed } from 'vue';
import { TrashIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true,
    validator: (value) => ['document', 'rfid'].includes(value)
  },
  status: {
    type: String,
    required: true,
    validator: (value) => ['pending', 'approved', 'released', 'rejected'].includes(value)
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

const accentColorClass = computed(() => {
  return props.type === 'rfid' ? 'border-l-[#FF2B3A]' : 'border-l-[#0957FF]';
});

const buttonConfigs = {
  pending: {
    document: [
      { id: 'view', label: 'View File', variant: 'primary' },
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'approve', label: 'Approve', variant: 'green' },
      { id: 'reject', label: 'Reject', variant: 'red' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
    ],
    rfid: [
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'approve', label: 'Approve', variant: 'green' },
      { id: 'reject', label: 'Reject', variant: 'red' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' }
    ]
  },
  approved: {
    document: [
      { id: 'view', label: 'View File', variant: 'primary' },
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'notify', label: 'Notify', variant: 'solidgreen' },
      { id: 'release', label: 'Release', variant: 'green' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ],
    rfid: [
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'notify', label: 'Notify', variant: 'solidgreen' },
      { id: 'release', label: 'Release', variant: 'green' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ]
  },
  released: {
    document: [
      { id: 'view', label: 'View File', variant: 'primary' },
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ],
    rfid: [
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ]
  },
  rejected: {
    document: [
      { id: 'view', label: 'View File', variant: 'primary' },
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ],
    rfid: [
      { id: 'notes', label: 'Notes', variant: 'gray' },
      { id: 'delete', label: '', icon: TrashIcon, variant: 'delete' },
      { id: 'undo', label: '', icon: ArrowUturnLeftIcon, variant: 'gray' }
    ]
  }
};

const visibleButtons = computed(() => {
  return buttonConfigs[props.status][props.type];
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
    primary: 'bg-[#0957FF] text-white hover:bg-white-10',
    gray: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
    green: 'bg-white text-green-600 border border-[#09AA44] hover:bg-green-50',
    solidgreen: 'bg-[#09AA44] text-white hover:bg-green-90',
    red: 'bg-white text-red-600 border border-[#FF2B3A] hover:bg-red-50',
    delete: 'bg-white text-[#B1202A] border border-[#FBBABA] hover:bg-[#FFE6E6]'
  };
  
  return `${baseClasses} ${variantClasses[btn.variant] || variantClasses.secondary}`;
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
    type: props.type,
    status: props.status
  });
};
</script>

<template>
  <div 
    class="bg-white rounded-lg border-l-[6px] border border-[#CCCCCC] p-5 flex items-start gap-4 transition-all relative"
    :class="accentColorClass"
  >
    <div class="flex flex-col items-center justify-center space-y-1">
      <div class="flex justify-center bg-[#F0F5FF] border border-[#D4DFF6] rounded px-4 py-1 min-w-[90px]">
        <div class="text-lg font-bold text-slate-700 leading-tight">{{ id }}</div>        
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
            {{ requester.firstName }} {{ requester.middleName }} {{ requester.surname }}
          </span>
        </div>

        <div class="flex flex-col">
          <span class="text-[11px] text-gray-400 font-medium">Requested on</span>
          <span class="text-sm text-slate-700 font-bold">{{ requestedOn }}</span>
        </div>
      </div>

      <div class="flex flex-col">
        <span class="text-[11px] text-gray-400 font-medium">RFID No.</span>
        <span 
          class="text-sm font-bold" 
          :class="rfidNo === 'Guest Mode' ? 'text-orange-500' : 'text-blue-600'"
        >
          {{ rfidNo }}
        </span>
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

      <div v-if="type === 'document' || amount" class="flex items-center gap-3">
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
            btn.id === 'delete' ? 'w-9 px-0' : 'px-4'
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