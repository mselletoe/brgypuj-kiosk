<script setup>
import { ref, computed } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'

// --- REFS ---
const recipientType = ref('all') // 'all', 'specific', 'group'
const phoneNumbers = ref('')
const announcementMessage = ref('')
const isSending = ref(false)
const showPreview = ref(false)
const sendHistory = ref([])

// Predefined groups (you can fetch these from your backend)
const residentGroups = ref([
  { id: 'homeowners', label: 'Homeowners', count: 150 },
  { id: 'tenants', label: 'Tenants', count: 75 },
  { id: 'officers', label: 'HOA Officers', count: 12 },
])
const selectedGroups = ref([])

// --- COMPUTED ---
const characterCount = computed(() => announcementMessage.value.length)
const estimatedSMSCount = computed(() => Math.ceil(characterCount.value / 160) || 1)

const recipientCount = computed(() => {
  if (recipientType.value === 'all') return 237 // Total residents (example)
  if (recipientType.value === 'specific') {
    const phones = phoneNumbers.value.split(',').filter(p => p.trim())
    return phones.length
  }
  if (recipientType.value === 'group') {
    return selectedGroups.value.reduce((total, groupId) => {
      const group = residentGroups.value.find(g => g.id === groupId)
      return total + (group?.count || 0)
    }, 0)
  }
  return 0
})

const isFormValid = computed(() => {
  if (!announcementMessage.value.trim()) return false
  if (recipientType.value === 'specific' && !phoneNumbers.value.trim()) return false
  if (recipientType.value === 'group' && selectedGroups.value.length === 0) return false
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
    } else if (recipientType.value === 'group') {
      payload.groups = selectedGroups.value
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
  <div class="p-6 bg-white rounded-md w-full min-h-screen space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <PageTitle title="Send SMS Announcement" />
      <div class="text-sm text-gray-500">
        Reach residents instantly via SMS
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Compose Area (2/3 width) -->
      <div class="lg:col-span-2 space-y-6">
        
        <!-- Recipient Selection -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Recipients</h3>
          
          <div class="space-y-4">
            <!-- Radio Options -->
            <label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition"
                   :class="{ 'border-blue-500 bg-blue-50': recipientType === 'all' }">
              <input type="radio" v-model="recipientType" value="all" class="mr-3 w-4 h-4" />
              <div class="flex-1">
                <div class="font-semibold text-gray-800">All Residents</div>
                <div class="text-sm text-gray-500">Send to all registered residents (237 contacts)</div>
              </div>
            </label>

            <label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition"
                   :class="{ 'border-blue-500 bg-blue-50': recipientType === 'group' }">
              <input type="radio" v-model="recipientType" value="group" class="mr-3 w-4 h-4" />
              <div class="flex-1">
                <div class="font-semibold text-gray-800">Specific Groups</div>
                <div class="text-sm text-gray-500">Select one or more resident groups</div>
              </div>
            </label>

            <!-- Group Selection (shown when 'group' is selected) -->
            <div v-if="recipientType === 'group'" class="ml-7 pl-4 border-l-2 border-gray-200 space-y-2">
              <label 
                v-for="group in residentGroups" 
                :key="group.id"
                class="flex items-center p-2 rounded hover:bg-gray-50 cursor-pointer"
              >
                <input 
                  type="checkbox" 
                  :checked="selectedGroups.includes(group.id)"
                  @change="toggleGroupSelection(group.id)"
                  class="mr-2 w-4 h-4"
                />
                <span class="text-sm font-medium text-gray-700">{{ group.label }}</span>
                <span class="ml-auto text-xs text-gray-500">({{ group.count }})</span>
              </label>
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
      <div class="space-y-6">
        
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
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            Recent Broadcasts
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

        <!-- Tips -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 shadow-sm">
          <h3 class="text-sm font-semibold text-amber-800 mb-2 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
            </svg>
            SMS Tips
          </h3>
          <ul class="text-xs text-amber-900 space-y-1.5">
            <li>• Keep messages clear and concise</li>
            <li>• Include date/time for events</li>
            <li>• Add contact info for questions</li>
            <li>• Avoid sending late at night</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>