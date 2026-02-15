<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageTitle from '@/components/shared/PageTitle.vue'

const router = useRouter()

// --- MOCK DATA (Replace with API calls) ---
const stats = ref({
  totalRequests: 342,
  pendingRequests: 28,
  readyForPickup: 12,
  completedToday: 45,
  equipmentRequests: 18,
  equipmentAvailable: 8,
  totalResidents: 237,
  activeRFIDCards: 189,
  recentFeedback: 15,
  unreadFeedback: 7
})

const systemHealth = ref({
  raspberryPi: { status: 'healthy', uptime: '15 days 4h', cpu: 45, memory: 62, temp: 52 },
  rfidReader: { status: 'healthy', lastScan: '2 minutes ago', totalScans: 1247 },
  sim800L: { status: 'warning', signal: 78, lastSMS: '5 minutes ago', messagesSent: 89, messagesQueued: 3 },
  network: { status: 'healthy', latency: 24, uptime: 99.8 }
})

const recentActivity = ref([
  { id: 1, type: 'document', user: 'Juan dela Cruz', action: 'Requested Barangay Clearance', time: '2 min ago', status: 'pending' },
  { id: 2, type: 'equipment', user: 'Maria Santos', action: 'Requested Basketball', time: '8 min ago', status: 'approved' },
  { id: 3, type: 'rfid', user: 'Pedro Reyes', action: 'RFID Scan - Document Pickup', time: '15 min ago', status: 'completed' },
  { id: 4, type: 'document', user: 'Ana Garcia', action: 'Requested Certificate of Residency', time: '23 min ago', status: 'pending' },
  { id: 5, type: 'sms', user: 'System', action: 'SMS Announcement sent to 237 residents', time: '1 hour ago', status: 'completed' }
])

const topDocuments = ref([
  { name: 'Barangay Clearance', requests: 89, percentage: 85 },
  { name: 'Certificate of Residency', requests: 67, percentage: 64 },
  { name: 'Business Permit', requests: 45, percentage: 43 },
  { name: 'Barangay ID', requests: 38, percentage: 36 },
  { name: 'Indigency Certificate', requests: 22, percentage: 21 }
])

const topEquipment = ref([
  { name: 'Basketball', requests: 34, available: 2 },
  { name: 'Folding Chairs (Set of 10)', requests: 28, available: 3 },
  { name: 'Sound System', requests: 15, available: 1 },
  { name: 'Folding Tables (Set of 5)', requests: 12, available: 2 }
])

// --- COMPUTED ---
const requestCompletionRate = computed(() => {
  const total = stats.value.totalRequests
  const completed = total - stats.value.pendingRequests
  return total > 0 ? Math.round((completed / total) * 100) : 0
})

const rfidAdoptionRate = computed(() => {
  const total = stats.value.totalResidents
  const active = stats.value.activeRFIDCards
  return total > 0 ? Math.round((active / total) * 100) : 0
})

// --- METHODS ---
const getStatusColor = (status) => {
  const colors = {
    healthy: 'text-green-600 bg-green-100',
    warning: 'text-yellow-600 bg-yellow-100',
    error: 'text-red-600 bg-red-100'
  }
  return colors[status] || colors.healthy
}

const getActivityIcon = (type) => {
  const icons = {
    document: '📄',
    equipment: '🏀',
    rfid: '💳',
    sms: '📱',
    feedback: '💬'
  }
  return icons[type] || '📋'
}

const navigateTo = (path) => {
  router.push(path)
}

// --- LIFECYCLE ---
onMounted(() => {
  // Fetch real data from API
  // await fetchDashboardStats()
  // await fetchSystemHealth()
  // await fetchRecentActivity()
})
</script>

<template>
  <div class="min-h-screen space-y-6">

    <!-- Key Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <!-- Total Requests -->
      <div 
        @click="navigateTo('/requests')"
        class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-5 shadow-md cursor-pointer transition-all"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-blue-100 text-sm font-medium">Total Requests</p>
            <p class="text-white text-3xl font-bold mt-2">{{ stats.totalRequests }}</p>
            <p class="text-blue-100 text-xs mt-2">{{ requestCompletionRate }}% completion rate</p>
          </div>
          <div class="bg-white bg-opacity-20 rounded-lg p-2">
            <span class="text-2xl">📋</span>
          </div>
        </div>
      </div>

      <!-- Pending Requests -->
      <div 
        @click="navigateTo('/requests')"
        class="bg-white rounded-xl p-5 shadow-md border border-gray-200 cursor-pointer transition-all"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-gray-600 text-sm font-medium">Pending Requests</p>
            <p class="text-gray-900 text-3xl font-bold mt-2">{{ stats.pendingRequests }}</p>
            <p class="text-orange-600 text-xs mt-2 font-semibold">⏱️ Needs attention</p>
          </div>
          <div class="bg-orange-100 rounded-lg p-2">
            <span class="text-2xl">⏳</span>
          </div>
        </div>
      </div>

      <!-- Ready for Pickup -->
      <div 
        @click="navigateTo('/requests')"
        class="bg-white rounded-xl p-5 shadow-md border border-gray-200 cursor-pointer transition-all"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-gray-600 text-sm font-medium">Ready for Pickup</p>
            <p class="text-gray-900 text-3xl font-bold mt-2">{{ stats.readyForPickup }}</p>
            <p class="text-green-600 text-xs mt-2 font-semibold">✅ Awaiting collection</p>
          </div>
          <div class="bg-green-100 rounded-lg p-2">
            <span class="text-2xl">📦</span>
          </div>
        </div>
      </div>

      <!-- Equipment Requests -->
      <div 
        @click="navigateTo('/equipment-management')"
        class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 shadow-md cursor-pointer transition-all"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-purple-100 text-sm font-medium">Equipment Requests</p>
            <p class="text-white text-3xl font-bold mt-2">{{ stats.equipmentRequests }}</p>
            <p class="text-purple-100 text-xs mt-2">{{ stats.equipmentAvailable }} items available</p>
          </div>
          <div class="bg-white bg-opacity-20 rounded-lg p-2">
            <span class="text-2xl">🏀</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Left Column - Analytics (2/3) -->
      <div class="lg:col-span-2 space-y-6">
        
        <!-- Top Requested Documents -->
        <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-bold text-gray-800">📊 Top Requested Documents</h3>
            <button 
              @click="navigateTo('/document-services')"
              class="text-xs text-blue-600 hover:text-blue-700 font-semibold"
            >
              View All →
            </button>
          </div>
          
          <div class="space-y-4">
            <div 
              v-for="doc in topDocuments" 
              :key="doc.name"
              class="flex items-center gap-4"
            >
              <div class="flex-1">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-semibold text-gray-700">{{ doc.name }}</span>
                  <span class="text-sm font-bold text-gray-900">{{ doc.requests }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-blue-600 h-2.5 rounded-full transition-all" 
                    :style="{ width: doc.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Requested Equipment -->
        <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-bold text-gray-800">🏀 Top Requested Equipment</h3>
            <button 
              @click="navigateTo('/equipment-management')"
              class="text-xs text-blue-600 hover:text-blue-700 font-semibold"
            >
              Manage →
            </button>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="item in topEquipment" 
              :key="item.name"
              class="p-4 bg-gray-50 rounded-lg border border-gray-200"
            >
              <p class="text-sm font-bold text-gray-800 mb-2">{{ item.name }}</p>
              <div class="flex items-center justify-between text-xs">
                <span class="text-gray-600">
                  <span class="font-semibold text-purple-600">{{ item.requests }}</span> requests
                </span>
                <span class="font-semibold" :class="item.available > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ item.available }} available
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 class="text-lg font-bold text-gray-800 mb-5">⚡ Recent Activity</h3>
          
          <div class="space-y-3">
            <div 
              v-for="activity in recentActivity" 
              :key="activity.id"
              class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
            >
              <div class="text-2xl">{{ getActivityIcon(activity.type) }}</div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-800 truncate">{{ activity.user }}</p>
                <p class="text-xs text-gray-600 mt-0.5">{{ activity.action }}</p>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-xs text-gray-400">{{ activity.time }}</p>
                <span 
                  class="text-xs font-semibold px-2 py-0.5 rounded-full mt-1 inline-block"
                  :class="{
                    'bg-green-100 text-green-700': activity.status === 'completed',
                    'bg-blue-100 text-blue-700': activity.status === 'approved',
                    'bg-yellow-100 text-yellow-700': activity.status === 'pending'
                  }"
                >
                  {{ activity.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - System Health & Quick Stats (1/3) -->
      <div class="space-y-6">
        
        <!-- System Health -->
        <div class="bg-white rounded-xl p-5 shadow-md border border-gray-200">
          <h3 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>💚</span> System Health
          </h3>
          
          <div class="space-y-3">
            <!-- Raspberry Pi -->
            <div class="p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">🖥️ Raspberry Pi</span>
                <span 
                  class="text-xs font-bold px-2 py-0.5 rounded-full"
                  :class="getStatusColor(systemHealth.raspberryPi.status)"
                >
                  {{ systemHealth.raspberryPi.status }}
                </span>
              </div>
              <div class="text-xs text-gray-600 space-y-1">
                <div class="flex justify-between">
                  <span>Uptime:</span>
                  <span class="font-semibold">{{ systemHealth.raspberryPi.uptime }}</span>
                </div>
                <div class="flex justify-between">
                  <span>CPU:</span>
                  <span class="font-semibold">{{ systemHealth.raspberryPi.cpu }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>Memory:</span>
                  <span class="font-semibold">{{ systemHealth.raspberryPi.memory }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>Temp:</span>
                  <span class="font-semibold">{{ systemHealth.raspberryPi.temp }}°C</span>
                </div>
              </div>
            </div>

            <!-- RFID Reader -->
            <div class="p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">💳 RFID Reader</span>
                <span 
                  class="text-xs font-bold px-2 py-0.5 rounded-full"
                  :class="getStatusColor(systemHealth.rfidReader.status)"
                >
                  {{ systemHealth.rfidReader.status }}
                </span>
              </div>
              <div class="text-xs text-gray-600 space-y-1">
                <div class="flex justify-between">
                  <span>Last Scan:</span>
                  <span class="font-semibold">{{ systemHealth.rfidReader.lastScan }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Total Scans:</span>
                  <span class="font-semibold">{{ systemHealth.rfidReader.totalScans }}</span>
                </div>
              </div>
            </div>

            <!-- SIM800L -->
            <div class="p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">📱 SIM800L</span>
                <span 
                  class="text-xs font-bold px-2 py-0.5 rounded-full"
                  :class="getStatusColor(systemHealth.sim800L.status)"
                >
                  {{ systemHealth.sim800L.status }}
                </span>
              </div>
              <div class="text-xs text-gray-600 space-y-1">
                <div class="flex justify-between">
                  <span>Signal:</span>
                  <span class="font-semibold">{{ systemHealth.sim800L.signal }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>Last SMS:</span>
                  <span class="font-semibold">{{ systemHealth.sim800L.lastSMS }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Sent Today:</span>
                  <span class="font-semibold">{{ systemHealth.sim800L.messagesSent }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Queued:</span>
                  <span class="font-semibold text-yellow-600">{{ systemHealth.sim800L.messagesQueued }}</span>
                </div>
              </div>
            </div>

            <!-- Network -->
            <div class="p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">🌐 Network</span>
                <span 
                  class="text-xs font-bold px-2 py-0.5 rounded-full"
                  :class="getStatusColor(systemHealth.network.status)"
                >
                  {{ systemHealth.network.status }}
                </span>
              </div>
              <div class="text-xs text-gray-600 space-y-1">
                <div class="flex justify-between">
                  <span>Latency:</span>
                  <span class="font-semibold">{{ systemHealth.network.latency }}ms</span>
                </div>
                <div class="flex justify-between">
                  <span>Uptime:</span>
                  <span class="font-semibold">{{ systemHealth.network.uptime }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-5 shadow-md border border-blue-200">
          <h3 class="text-sm font-bold text-gray-800 mb-4">📈 Quick Stats</h3>
          
          <div class="space-y-4">
            <div>
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs text-gray-600">RFID Adoption</span>
                <span class="text-xs font-bold text-indigo-700">{{ rfidAdoptionRate }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-indigo-600 h-2 rounded-full" 
                  :style="{ width: rfidAdoptionRate + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ stats.activeRFIDCards }} of {{ stats.totalResidents }} residents</p>
            </div>

            <div class="pt-3 border-t border-blue-200">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Completed Today</span>
                <span class="text-2xl font-bold text-green-600">{{ stats.completedToday }}</span>
              </div>
            </div>

            <div class="pt-3 border-t border-blue-200">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Community Feedback</span>
                <div class="text-right">
                  <p class="text-lg font-bold text-gray-800">{{ stats.recentFeedback }}</p>
                  <p class="text-xs text-orange-600 font-semibold">{{ stats.unreadFeedback }} unread</p>
                </div>
              </div>
            </div>

            <button 
              @click="navigateTo('/community-feedback')"
              class="w-full mt-4 px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition"
            >
              View Feedback →
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-xl p-5 shadow-md border border-gray-200">
          <h3 class="text-sm font-bold text-gray-800 mb-4">⚡ Quick Actions</h3>
          
          <div class="space-y-2">
            <button 
              @click="navigateTo('/requests')"
              class="w-full px-4 py-2.5 bg-blue-50 text-blue-700 text-xs font-semibold rounded-lg hover:bg-blue-100 transition text-left"
            >
              📄 Process Requests
            </button>
            <button 
              @click="navigateTo('/sms-announcements')"
              class="w-full px-4 py-2.5 bg-green-50 text-green-700 text-xs font-semibold rounded-lg hover:bg-green-100 transition text-left"
            >
              📱 Send SMS Announcement
            </button>
            <button 
              @click="navigateTo('/residents')"
              class="w-full px-4 py-2.5 bg-purple-50 text-purple-700 text-xs font-semibold rounded-lg hover:bg-purple-100 transition text-left"
            >
              👥 Manage Residents
            </button>
            <button 
              @click="navigateTo('/document-services')"
              class="w-full px-4 py-2.5 bg-orange-50 text-orange-700 text-xs font-semibold rounded-lg hover:bg-orange-100 transition text-left"
            >
              📋 Configure Services
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>