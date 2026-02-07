<script setup>
import { ref, onMounted } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'
import KioskAnnouncementCard from '@/views/announcements/KioskAnnouncementCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getAllAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement as deleteAnnouncementApi,
  toggleAnnouncementStatus
} from '@/api/announcementService'

/* -------------------- STATE -------------------- */
const announcements = ref([])
const editingId = ref(null)
const creatingNew = ref(false)
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)
const loading = ref(false)

/* -------------------- LOAD DATA -------------------- */
const loadAnnouncements = async () => {
  loading.value = true
  try {
    const data = await getAllAnnouncements()
    announcements.value = data
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    alert('Failed to load announcements. Please try again.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnnouncements()
})

/* -------------------- ACTIONS -------------------- */
const startCreate = () => {
  creatingNew.value = true
  editingId.value = null
}

const startEdit = (announcement) => {
  editingId.value = announcement.id
  creatingNew.value = false
}

const cancelEdit = () => {
  editingId.value = null
  creatingNew.value = false
}

const saveAnnouncement = async ({ formData, imageFile }) => {
  // Validation
  if (!formData.title?.trim()) {
    alert('Title is required')
    return
  }
  if (!formData.event_date) {
    alert('Event date is required')
    return
  }
  if (!formData.location?.trim()) {
    alert('Location is required')
    return
  }

  loading.value = true
  try {
    const announcementData = {
      title: formData.title,
      description: formData.description || null,
      event_date: formData.event_date,
      event_time: formData.event_time || null,
      location: formData.location,
      is_active: formData.is_active ?? true
    }

    if (creatingNew.value) {
      // Create new announcement
      await createAnnouncement(announcementData, imageFile)
      alert('Announcement created successfully')
    } else {
      // Update existing announcement
      await updateAnnouncement(editingId.value, announcementData, imageFile, false)
      alert('Announcement updated successfully')
    }

    // Reload announcements
    await loadAnnouncements()
    cancelEdit()
  } catch (err) {
    console.error('Save failed:', err)
    alert(err.response?.data?.detail || 'Failed to save announcement. Please try again.')
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (announcement) => {
  try {
    await toggleAnnouncementStatus(announcement.id)
    // Reload to get updated data
    await loadAnnouncements()
  } catch (err) {
    console.error('Toggle status failed:', err)
    alert('Failed to toggle announcement status')
  }
}

const requestDelete = (id) => {
  deleteTargetId.value = id
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  const id = deleteTargetId.value
  loading.value = true
  
  try {
    await deleteAnnouncementApi(id)
    await loadAnnouncements()
    showDeleteModal.value = false
    deleteTargetId.value = null
  } catch (err) {
    console.error('Delete failed:', err)
    alert('Failed to delete announcement. Please try again.')
  } finally {
    loading.value = false
  }
}

const cancelDelete = () => {
  showDeleteModal.value = false
  deleteTargetId.value = null
}
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Kiosk Announcements" />
        <p class="text-sm text-gray-500 mt-1">
          Create and schedule public notices for the community information kiosks.
        </p>
      </div>
      <button
        @click="startCreate"
        :disabled="loading || creatingNew"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Add Announcement
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !announcements.length" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-gray-500 mt-2">Loading announcements...</p>
      </div>
    </div>

    <!-- Grid -->
    <div v-else class="flex-1 overflow-y-auto pr-2">
      <div
        v-if="announcements.length || creatingNew"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5"
      >
        <!-- New Card -->
        <KioskAnnouncementCard
          v-if="creatingNew"
          is-new
          is-editing
          :announcement="{
            title: '',
            description: '',
            event_date: '',
            event_time: '',
            location: '',
            image_base64: null,
            is_active: true
          }"
          @save="saveAnnouncement"
          @cancel="cancelEdit"
        />

        <!-- Existing Cards -->
        <KioskAnnouncementCard
          v-for="item in announcements"
          :key="item.id"
          :announcement="item"
          :is-editing="editingId === item.id"
          @edit="startEdit"
          @save="saveAnnouncement"
          @cancel="cancelEdit"
          @delete="requestDelete"
          @toggle-status="handleToggleStatus"
        />
      </div>

      <!-- Empty State -->
      <div
        v-else
        class="h-full flex flex-col items-center justify-center text-gray-500"
      >
        <svg 
          class="w-20 h-20 text-gray-300 mb-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"
          />
        </svg>
        <p class="text-lg font-medium mb-2">No announcements yet</p>
        <p class="text-sm mb-4">Create your first announcement to get started</p>
        <button
          @click="startCreate"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          Create Announcement
        </button>
      </div>
    </div>

    <!-- Loading Overlay (for operations) -->
    <div 
      v-if="loading && announcements.length" 
      class="fixed inset-0 bg-black bg-opacity-10 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-4 shadow-xl">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <ConfirmModal
    :show="showDeleteModal"
    title="Delete this announcement?"
    message="This action cannot be undone. The announcement will be permanently removed from the system."
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />
</template>
