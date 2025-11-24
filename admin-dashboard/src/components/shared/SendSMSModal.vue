<script setup>
import { ref, watch } from 'vue'
import { NModal, NCard, NInput, NButton, NSpace, useMessage } from 'naive-ui'

// --- PROPS ---
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  recipientName: {
    type: String,
    default: ''
  },
  recipientPhone: {
    type: String,
    default: ''
  },
  defaultMessage: {
    type: String,
    default: ''
  }
})

// --- EMITS ---
const emit = defineEmits(['update:show', 'send'])

// --- REFS ---
const message = useMessage()
const phoneNumber = ref('')
const smsMessage = ref('')
const isSending = ref(false)

// --- WATCHERS ---
watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset and populate fields when modal opens
    phoneNumber.value = props.recipientPhone || ''
    smsMessage.value = props.defaultMessage || ''
  }
})

// --- HANDLERS ---
const handleClose = () => {
  emit('update:show', false)
}

const handleSend = async () => {
  // Validation
  if (!phoneNumber.value.trim()) {
    message.warning('Please enter a phone number')
    return
  }
  
  if (!smsMessage.value.trim()) {
    message.warning('Please enter a message')
    return
  }

  isSending.value = true

  try {
    // Emit the send event with the data
    await emit('send', {
      phone: phoneNumber.value,
      message: smsMessage.value,
      recipientName: props.recipientName
    })
    
    message.success('SMS sent successfully!')
    handleClose()
  } catch (error) {
    console.error('Error sending SMS:', error)
    message.error('Failed to send SMS. Please try again.')
  } finally {
    isSending.value = false
  }
}

const characterCount = ref(0)
watch(smsMessage, (newVal) => {
  characterCount.value = newVal.length
})
</script>

<template>
  <NModal
    :show="show"
    @update:show="handleClose"
    preset="card"
    :style="{ maxWidth: '540px' }"
    :bordered="false"
    :segmented="{ content: true }"
  >
    <template #header>
      <div class="text-lg font-semibold text-gray-800">Send SMS</div>
    </template>

    <NSpace vertical :size="16">
      <!-- Recipient Name (if provided) -->
      <div v-if="recipientName">
        <label class="block text-xs font-medium text-gray-500 mb-1.5">Recipient</label>
        <div class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md text-sm font-semibold text-gray-800">
          {{ recipientName }}
        </div>
      </div>

      <!-- Phone Number -->
      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1.5">
          Phone Number <span class="text-red-500">*</span>
        </label>
        <NInput
          v-model:value="phoneNumber"
          placeholder="e.g., +639123456789"
          size="large"
          :disabled="isSending"
        />
      </div>

      <!-- Message -->
      <div>
        <div class="flex items-center justify-between mb-1.5">
          <label class="block text-xs font-medium text-gray-500">
            Message <span class="text-red-500">*</span>
          </label>
          <span class="text-xs text-gray-400">{{ characterCount }} characters</span>
        </div>
        <NInput
          v-model:value="smsMessage"
          type="textarea"
          placeholder="Type your message here..."
          :rows="5"
          :disabled="isSending"
          :maxlength="500"
          show-count
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-end gap-2 pt-2">
        <NButton
          @click="handleClose"
          :disabled="isSending"
          size="large"
        >
          Cancel
        </NButton>
        <NButton
          type="primary"
          @click="handleSend"
          :loading="isSending"
          size="large"
        >
          Send SMS
        </NButton>
      </div>
    </NSpace>
  </NModal>
</template>