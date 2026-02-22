<script setup>
import { ref } from 'vue';

const activeTab = ref('Profile');
const tabs = ['Profile', 'Security', 'Preferences', 'Audit Log'];

const profileData = ref({
  name: 'Jett To Holidays',
  role: 'Barangay Administrator',
  username: 'admin.revivemejett'
});

const securityData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const preferencesData = ref({
  newDocumentRequests: true,
  equipmentOverdue: true,
  defaultLandingPage: 'Overview Dashboard'
});

const auditLogs = ref([
  { date: 'Jan 30, 2026', time: '10:30 AM', action: 'Approved Request', details: 'DOC-002 - Barangay Clearance' },
  { date: 'Jan 30, 2026', time: '9:45 AM', action: 'Login', details: 'Successful login' },
  { date: 'Jan 29, 2026', time: '3:20 PM', action: 'Released Document', details: 'DOC-003 - Business Permit' },
  { date: 'Jan 29, 2026', time: '2:45 PM', action: 'Added Resident', details: 'New resident: Ana Garcia' },
  { date: 'Jan 29, 2026', time: '11:15 AM', action: 'Equipment Returned', details: 'EQP-044 - Tables & Chairs' }
]);
</script>

<template>
  <div class="flex flex-col p-8 bg-[#f8f9fa] w-full h-full overflow-y-auto font-sans">
    
    <div class="mb-6">
      <h1 class="text-[24px] font-bold text-gray-900">Account Settings</h1>
      <p class="text-gray-500 text-[14px] mt-1">Manage your admin account</p>
    </div>
    
    <div class="border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden">
      
      <div class="flex px-4 border-b border-gray-200">
        <button 
          v-for="tab in tabs" 
          :key="tab"
          @click="activeTab = tab"
          :class="['px-6 py-4 text-[14px] font-medium transition-colors outline-none', 
                   activeTab === tab ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-800']"
        >
          {{ tab }}
        </button>
      </div>

      <div v-if="activeTab === 'Profile'" class="p-8 flex flex-col lg:flex-row gap-12 lg:justify-between lg:items-center items-start">
        <div class="flex-1 w-full max-w-2xl space-y-6">
          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Name</label>
            <input 
              type="text" 
              v-model="profileData.name" 
              disabled
              class="border border-gray-200 bg-gray-50 rounded-md px-4 py-2 text-[14px] text-gray-600 w-full cursor-not-allowed outline-none"
            />
          </div>

          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Role/Position</label>
            <input 
              type="text" 
              v-model="profileData.role" 
              class="border border-gray-300 rounded-md px-4 py-2 text-[14px] text-gray-800 w-full focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Username</label>
            <input 
              type="text" 
              v-model="profileData.username" 
              class="border border-gray-300 rounded-md px-4 py-2 text-[14px] text-gray-800 w-full focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="pt-4">
            <button class="bg-[#0d6efd] hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md text-[13px] transition-colors">
              Save Changes
            </button>
          </div>
        </div>

        <div class="w-full lg:w-72 border border-gray-200 rounded-lg p-8 flex flex-col items-center justify-center mt-8 lg:mt-0 lg:mr-16">
          
          <div class="relative w-[150px] h-[150px] rounded-full border-2 border-blue-100 overflow-hidden mb-4 group cursor-pointer transition-all duration-300 hover:border-blue-400 hover:shadow-lg">
            <img 
              src="https://api.dicebear.com/7.x/adventurer/svg?seed=Jett" 
              alt="Profile Photo" 
              class="w-full h-full object-cover bg-blue-50 transition-transform duration-300 group-hover:scale-110"
            />
            
            <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
          </div>
          
          <p class="text-[11px] text-gray-500 mb-6">JPG, PNG. Max 2MB</p>
          <div class="flex gap-2 w-full justify-center">
            <button class="border border-[#0d6efd] text-[#0d6efd] bg-white rounded-md px-3 py-1.5 text-[12px] hover:bg-blue-50 transition-colors">
              Upload photo
            </button>
            <button class="border border-red-500 text-red-500 bg-white rounded-md px-3 py-1.5 text-[12px] hover:bg-red-50 transition-colors">
              Remove Photo
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'Security'" class="p-8 flex flex-col lg:flex-row gap-12 lg:justify-between lg:items-center items-start">
        <div class="flex-1 w-full max-w-2xl space-y-6">
          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Current Password</label>
            <input 
              type="password" 
              v-model="securityData.currentPassword"
              placeholder="Enter current password"
              class="border border-gray-300 rounded-md px-4 py-2 text-[14px] text-gray-800 w-full focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
            />
          </div>

          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">New Password</label>
            <input 
              type="password" 
              v-model="securityData.newPassword"
              placeholder="Enter new password"
              class="border border-gray-300 rounded-md px-4 py-2 text-[14px] text-gray-800 w-full focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
            />
          </div>

          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Confirm New Password</label>
            <input 
              type="password" 
              v-model="securityData.confirmPassword"
              placeholder="Confirm new password"
              class="border border-gray-300 rounded-md px-4 py-2 text-[14px] text-gray-800 w-full focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
            />
          </div>

          <div class="pt-1">
            <div class="flex items-center gap-1 text-[12px] font-bold mb-2">
              <span class="text-gray-800">Password Strength:</span>
              <span class="text-yellow-500">Medium</span>
            </div>
            <div class="w-full bg-gray-200 h-1 rounded-full mb-2">
              <div class="bg-yellow-500 h-1 rounded-full" style="width: 50%;"></div>
            </div>
            <p class="text-[11px] text-gray-400">Password must be at least 8 characters with uppercase, lowercase, and numbers</p>
          </div>

          <div class="pt-4">
            <button class="bg-[#0d6efd] hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md text-[13px] transition-colors">
              Save Changes
            </button>
          </div>
        </div>

        <div class="w-full lg:w-[350px] border border-red-200 bg-[#fff5f5] rounded-lg p-6 flex flex-col mt-8 lg:mt-0 lg:mr-16">
          <h3 class="text-red-600 font-medium text-[14px] mb-2">Delete Account</h3>
          <p class="text-[12px] text-gray-800 mb-6 leading-relaxed">Permanently delete your admin account and all associated data. This action cannot be undone.</p>
          <div class="flex justify-end mt-auto">
            <button class="bg-[#dc3545] hover:bg-red-700 text-white font-medium py-2 px-4 rounded-md text-[13px] transition-colors">
              Delete Account
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'Preferences'" class="p-8 flex flex-col md:flex-row gap-16">
        <div class="flex-1 max-w-md">
          <h3 class="font-bold text-gray-800 mb-6 text-[15px]">Notification Settings</h3>
          
          <div class="space-y-6">
            <div class="flex items-center justify-between border-b border-gray-100 pb-4">
              <div>
                <p class="text-[13px] font-bold text-gray-800">New Document Requests</p>
                <p class="text-[11px] text-gray-500 mt-1">Alert when new document requested</p>
              </div>
              <button 
                @click="preferencesData.newDocumentRequests = !preferencesData.newDocumentRequests"
                :class="['relative inline-flex h-5 w-9 items-center rounded-full transition-colors', preferencesData.newDocumentRequests ? 'bg-[#0d6efd]' : 'bg-gray-300']"
              >
                <span :class="['inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform', preferencesData.newDocumentRequests ? 'translate-x-4.5' : 'translate-x-1']"></span>
              </button>
            </div>

            <div class="flex items-center justify-between border-b border-gray-100 pb-4">
              <div>
                <p class="text-[13px] font-bold text-gray-800">Equipment Overdue</p>
                <p class="text-[11px] text-gray-500 mt-1">Alert when equipment is overdue</p>
              </div>
              <button 
                @click="preferencesData.equipmentOverdue = !preferencesData.equipmentOverdue"
                :class="['relative inline-flex h-5 w-9 items-center rounded-full transition-colors', preferencesData.equipmentOverdue ? 'bg-[#0d6efd]' : 'bg-gray-300']"
              >
                <span :class="['inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform', preferencesData.equipmentOverdue ? 'translate-x-4.5' : 'translate-x-1']"></span>
              </button>
            </div>
          </div>

          <div class="pt-8">
            <button class="bg-[#0d6efd] hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md text-[13px] transition-colors">
              Save Changes
            </button>
          </div>
        </div>

        <div class="flex-1 max-w-md">
          <h3 class="font-bold text-gray-800 mb-6 text-[15px]">Display Preferences</h3>
          
          <div class="flex flex-col">
            <label class="text-[12px] font-bold text-gray-800 mb-2">Default Landing Page</label>
            <div class="relative">
              <select 
                v-model="preferencesData.defaultLandingPage"
                class="appearance-none border border-gray-300 rounded-md px-4 py-2 pr-8 text-[13px] text-gray-800 w-full outline-none focus:border-blue-500 bg-white cursor-pointer"
              >
                <option value="Overview Dashboard">Overview Dashboard</option>
                <option value="Document Request">Document Request</option>
                <option value="Equipment Request">Equipment Request</option>
                <option value="Residents Information">Residents Information</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'Audit Log'" class="p-8">
        <h3 class="font-bold text-gray-800 mb-6 text-[15px]">Recent Actions</h3>
        
        <div class="overflow-x-auto w-full">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]">Date & Time</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]">Action</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[50%]">Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, index) in auditLogs" :key="index" class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors">
                <td class="py-4 px-4 whitespace-nowrap">
                  <div class="text-[13px] text-gray-800">{{ log.date }}</div>
                  <div class="text-[11px] text-gray-400 mt-0.5">{{ log.time }}</div>
                </td>
                <td class="py-4 px-4 text-[13px] text-gray-800">{{ log.action }}</td>
                <td class="py-4 px-4 text-[13px] text-gray-600">{{ log.details }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.translate-x-4\.5 {
  transform: translateX(1.125rem);
}
</style>