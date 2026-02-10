<script setup>
import { ref, computed } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'

const recipientType = ref('all')
const phoneNumbers = ref('')
const announcementMessage = ref('')
const isSending = ref(false)
const showPreview = ref(false)
const sendHistory = ref([])

const filters = ref({
  puroks: [],            // array of purok IDs
  gender: 'any',         // 'any' | 'male' | 'female'
  residencyYears: null,  // number
  ageFrom: null,         // number
  ageTo: null            // number
})

const puroks = ref([
  { id: 1, name: 'Purok 1' },
  { id: 2, name: 'Purok 2' },
  { id: 3, name: 'Purok 3' }
])

const characterCount = computed(() => announcementMessage.value.length)
const estimatedSMSCount = computed(() => Math.ceil(characterCount.value / 160) || 1)

const recipientCount = computed(() => {
  if (recipientType.value === 'all') return 237 // Total residents (example)
  if (recipientType.value === 'specific') {
    const phones = phoneNumbers.value.split(',').filter(p => p.trim())
    return phones.length
  }
  if (recipientType.value === 'filtered')
  return 0
})

const isFormValid = computed(() => {
  if (!announcementMessage.value.trim()) return false
  if (recipientType.value === 'specific' && !phoneNumbers.value.trim()) return false
  if (recipientType.value === 'filtered') {
    const f = filters.value
    const hasAnyFilter =
      f.puroks.length ||
      f.gender !== 'any' ||
      f.residencyYears !== null ||
      f.ageFrom !== null ||
      f.ageTo !== null

    if (!hasAnyFilter) return false
  }
  return true
})

// --- QUICK MESSAGE TEMPLATES ---
const templates = [
  {
    title: 'Event Reminder',
    message: 'Reminder: Community meeting tomorrow at 6 PM in the clubhouse. Please attend.'
  },
  {
    title: 'Maintenance Notice',
    message: 'Scheduled water interruption on [DATE] from [TIME] to [TIME]. Please prepare accordingly.'
  },
  {
    title: 'Emergency Alert',
    message: 'IMPORTANT: [Emergency details]. Please stay safe and follow instructions.'
  },
  {
    title: 'Payment Reminder',
    message: 'This is a reminder that your HOA dues payment is due on [DATE]. Thank you!'
  }
]

// --- HANDLERS ---
const handleSendSMS = async () => {
  if (!isFormValid.value) return

  isSending.value = true
  
  try {
    // Prepare payload based on recipient type
    let payload = {
      message: announcementMessage.value,
      recipientType: recipientType.value
    }

    if (recipientType.value === 'specific') {
      payload.phoneNumbers = phoneNumbers.value
        .split(',')
        .map(p => p.trim())
        .filter(p => p)
    } else if (recipientType.value === 'filtered') {
      payload.filters = filters.value
    }

    // API call (replace with your actual endpoint)
    // const response = await api.post('/sms/send-announcement', payload)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Add to history
    sendHistory.value.unshift({
      id: Date.now(),
      message: announcementMessage.value.substring(0, 50) + '...',
      recipients: recipientCount.value,
      timestamp: new Date().toLocaleString(),
      status: 'sent'
    })

    // Success feedback
    alert(`SMS announcement sent successfully to ${recipientCount.value} recipient(s)!`)
    
    // Reset form
    announcementMessage.value = ''
    phoneNumbers.value = ''
    selectedGroups.value = []
    showPreview.value = false
    
  } catch (error) {
    console.error('Error sending SMS announcement:', error)
    alert('Failed to send SMS announcement. Please try again.')
  } finally {
    isSending.value = false
  }
}

const applyTemplate = (template) => {
  announcementMessage.value = template.message
}

const toggleGroupSelection = (groupId) => {
  const index = selectedGroups.value.indexOf(groupId)
  if (index > -1) {
    selectedGroups.value.splice(index, 1)
  } else {
    selectedGroups.value.push(groupId)
  }
}
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex flex-col mb-4">
      <PageTitle title="SMS Announcements" />
      <p class="text-sm text-gray-500 mt-1">Send SMS announcements to residents</p>
    </div>

    <div class="overflow-y-auto">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Compose Area (2/3 width) -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Recipient Selection -->
          <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Recipients</h3>
            
            <div class="space-y-4">
              <!-- Radio Options -->
              <label
                class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition"
                :class="{ 'border-blue-500 bg-blue-50': recipientType === 'filtered' }"
              >
                <input type="radio" v-model="recipientType" value="filtered" class="mr-3 w-4 h-4" />
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">Filtered Residents</div>
                  <div class="text-sm text-gray-500">
                    Select residents based on location and demographics
                  </div>
                </div>
              </label>

              <div
                v-if="recipientType === 'filtered'"
                class="ml-7 pl-4 border-l-2 border-gray-200 space-y-5"
              >
                <!-- Purok -->
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-2">📍 Purok</div>
                  <div class="grid grid-cols-2 gap-2">
                    <label
                      v-for="purok in puroks"
                      :key="purok.id"
                      class="flex items-center gap-2 text-sm"
                    >
                      <input type="checkbox" :value="purok.id" v-model="filters.puroks" />
                      {{ purok.name }}
                    </label>
                  </div>
                </div>

                <!-- Gender -->
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-2">👤 Gender</div>
                  <div class="flex gap-4 text-sm">
                    <label><input type="radio" value="any" v-model="filters.gender" /> Any</label>
                    <label><input type="radio" value="male" v-model="filters.gender" /> Male</label>
                    <label><input type="radio" value="female" v-model="filters.gender" /> Female</label>
                  </div>
                </div>

                <!-- Years of Residency -->
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-1">🏠 Years of Residency</div>
                  <div class="flex items-center gap-2 text-sm">
                    <input
                      type="number"
                      min="0"
                      v-model.number="filters.residencyYears"
                      class="w-20 border rounded px-2 py-1"
                    />
                    <span>years or more</span>
                  </div>
                </div>

                <!-- Age -->
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-1">🎂 Age</div>
                  <div class="flex items-center gap-2 text-sm">
                    <span>From</span>
                    <input
                      type="number"
                      min="0"
                      v-model.number="filters.ageFrom"
                      class="w-20 border rounded px-2 py-1"
                    />
                    <span>to</span>
                    <input
                      type="number"
                      min="0"
                      v-model.number="filters.ageTo"
                      class="w-20 border rounded px-2 py-1"
                    />
                  </div>
                </div>
              </div>

              <label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition"
                    :class="{ 'border-blue-500 bg-blue-50': recipientType === 'specific' }">
                <input type="radio" v-model="recipientType" value="specific" class="mr-3 w-4 h-4" />
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">Specific Numbers</div>
                  <div class="text-sm text-gray-500">Enter phone numbers manually</div>
                </div>
              </label>

              <!-- Phone Number Input (shown when 'specific' is selected) -->
              <div v-if="recipientType === 'specific'" class="ml-7 pl-4 border-l-2 border-gray-200">
                <textarea
                  v-model="phoneNumbers"
                  placeholder="Enter phone numbers separated by commas&#10;e.g., +639123456789, +639987654321"
                  rows="3"
                  class="w-full border border-gray-300 bg-gray-50 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                  Separate multiple numbers with commas
                </p>
              </div>
            </div>
          </div>

          <!-- Message Compose -->
          <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-800">Compose Message</h3>
              <div class="text-xs text-gray-500">
                <span class="font-semibold">{{ characterCount }}</span> characters
                <span class="mx-1">•</span>
                <span class="font-semibold">{{ estimatedSMSCount }}</span> SMS
              </div>
            </div>

            <textarea
              v-model="announcementMessage"
              placeholder="Type your announcement message here..."
              rows="8"
              maxlength="500"
              class="w-full border border-gray-300 bg-gray-50 rounded-md p-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            ></textarea>

            <div class="flex items-center justify-between mt-3">
              <div class="text-xs text-gray-400">Maximum 500 characters</div>
              <div class="flex gap-2">
                <button
                  @click="showPreview = !showPreview"
                  class="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 transition"
                >
                  {{ showPreview ? 'Hide' : 'Show' }} Preview
                </button>
              </div>
            </div>

            <!-- Message Preview -->
            <div v-if="showPreview && announcementMessage" class="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div class="text-xs font-semibold text-gray-500 uppercase mb-2">Preview</div>
              <div class="text-sm text-gray-800 whitespace-pre-wrap">{{ announcementMessage }}</div>
            </div>
          </div>

          <!-- Send Button -->
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600">
              <span class="font-semibold text-blue-600">{{ recipientCount }}</span> recipient(s) will receive this message
            </div>
            <button
              @click="handleSendSMS"
              :disabled="!isFormValid || isSending"
              class="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center gap-2"
            >
              <svg v-if="!isSending" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
              <span v-if="isSending">Sending...</span>
              <span v-else>Send SMS Announcement</span>
            </button>
          </div>
        </div>

        <!-- Sidebar (1/3 width) -->
        <div class="flex flex-col gap-6">
          
          <!-- Quick Templates -->
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-5 shadow-sm">
            <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
              </svg>
              Quick Templates
            </h3>
            <div class="space-y-2">
              <button
                v-for="template in templates"
                :key="template.title"
                @click="applyTemplate(template)"
                class="w-full text-left p-3 bg-white border border-blue-200 rounded-md hover:bg-blue-50 hover:border-blue-400 transition text-sm"
              >
                <div class="font-semibold text-gray-800 text-xs">{{ template.title }}</div>
                <div class="text-gray-600 text-xs mt-1 line-clamp-2">{{ template.message }}</div>
              </button>
            </div>
          </div>

          <!-- Send History -->
          <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm overflow-y-auto h-45">
            <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Recent Messages
            </h3>
            
            <div v-if="sendHistory.length === 0" class="text-center text-gray-400 text-xs py-4">
              No messages sent yet
            </div>
            
            <div v-else class="space-y-3 max-h-96 overflow-y-auto">
              <div 
                v-for="item in sendHistory.slice(0, 5)" 
                :key="item.id"
                class="p-3 bg-gray-50 border border-gray-200 rounded-md"
              >
                <div class="text-xs text-gray-700 font-medium line-clamp-2 mb-1">{{ item.message }}</div>
                <div class="flex items-center justify-between text-xs text-gray-500">
                  <span>{{ item.recipients }} recipients</span>
                  <span class="text-green-600 font-semibold">✓ Sent</span>
                </div>
                <div class="text-xs text-gray-400 mt-1">{{ item.timestamp }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>