<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { TrashIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import KioskAnnouncementCard from '@/views/announcements/KioskAnnouncementCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getAllAnnouncements,
  getAnnouncementById,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement as deleteAnnouncementApi,
  bulkDeleteAnnouncements,
  toggleAnnouncementStatus
} from '@/api/announcementService'

const message = useMessage()

/* -------------------- STATE -------------------- */
const announcements = ref([])
const editingId = ref(null)
const creatingNew = ref(false)
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)
const loading = ref(false)
const selectedAnnouncements = ref(new Set())
const searchQuery = ref('')

/* -------------------- COMPUTED -------------------- */
const selectedCount = computed(() => selectedAnnouncements.value.size)
const totalCount = computed(() => announcements.value.length)

const selectionState = computed(() => {
  const count = selectedCount.value
  const total = totalCount.value
  
  if (count === 0) return 'none'
  if (count > 0 && count < total) return 'partial'
  return 'all'
})

/* -------------------- LOAD DATA -------------------- */
const loadAnnouncements = async () => {
  loading.value = true
  try {
    // First get the list of announcements
    const data = await getAllAnnouncements()
    
    // Then fetch full details (including images) for each announcement
    const detailedAnnouncements = await Promise.all(
      data.map(announcement => getAnnouncementById(announcement.id))
    )
    
    announcements.value = detailedAnnouncements
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    message.error('Failed to load announcements. Please try again.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnnouncements()
})

/* -------------------- SELECTION ACTIONS -------------------- */
const handleMainSelectToggle = () => {
  if (selectionState.value === 'all' || selectionState.value === 'partial') {
    deselectAll()
  } else {
    selectAll()
  }
}

const selectAll = () => {
  selectedAnnouncements.value = new Set(announcements.value.map(a => a.id))
}

const deselectAll = () => {
  selectedAnnouncements.value.clear()
}

const handleSelectionUpdate = (announcementId, isSelected) => {
  if (isSelected) {
    selectedAnnouncements.value.add(announcementId)
  } else {
    selectedAnnouncements.value.delete(announcementId)
  }
}

/* -------------------- BULK DELETE -------------------- */
const bulkDelete = () => {
  if (selectedAnnouncements.value.size === 0) return

  deleteTargetId.value = 'bulk'
  showDeleteModal.value = true
}

const confirmBulkDelete = async () => {
  loading.value = true
  
  try {
    await bulkDeleteAnnouncements(Array.from(selectedAnnouncements.value))
    await loadAnnouncements()
    selectedAnnouncements.value.clear()
    showDeleteModal.value = false
    deleteTargetId.value = null
    message.success(`${selectedCount.value} announcement(s) deleted successfully`)
  } catch (err) {
    console.error('Bulk delete failed:', err)
    message.error('Failed to delete announcements. Please try again.')
  } finally {
    loading.value = false
  }
}

/* -------------------- CRUD ACTIONS -------------------- */
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
    message.warning('Title is required')
    return
  }
  if (!formData.event_date) {
    message.warning('Event date is required')
    return
  }
  if (!formData.location?.trim()) {
    message.warning('Location is required')
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
      message.success('Announcement created successfully')
    } else {
      // Update existing announcement
      await updateAnnouncement(editingId.value, announcementData, imageFile, false)
      message.success('Announcement updated successfully')
    }

    // Reload announcements
    await loadAnnouncements()
    cancelEdit()
  } catch (err) {
    console.error('Save failed:', err)
    message.error(err.response?.data?.detail || 'Failed to save announcement. Please try again.')
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (announcement) => {
  try {
    await toggleAnnouncementStatus(announcement.id)
    // Reload to get updated data
    await loadAnnouncements()
    message.success(`Announcement ${announcement.is_active ? 'deactivated' : 'activated'} successfully`)
  } catch (err) {
    console.error('Toggle status failed:', err)
    message.error('Failed to toggle announcement status')
  }
}

const requestDelete = (id) => {
  deleteTargetId.value = id
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (deleteTargetId.value === 'bulk') {
    await confirmBulkDelete()
    return
  }

  const id = deleteTargetId.value
  loading.value = true
  
  try {
    await deleteAnnouncementApi(id)
    await loadAnnouncements()
    showDeleteModal.value = false
    deleteTargetId.value = null
    message.success('Announcement deleted successfully')
  } catch (err) {
    console.error('Delete failed:', err)
    message.error('Failed to delete announcement. Please try again.')
  } finally {
    loading.value = false
  }
}

const cancelDelete = () => {
  showDeleteModal.value = false
  deleteTargetId.value = null
}

const deleteModalTitle = computed(() => {
  if (deleteTargetId.value === 'bulk') {
    return `Delete ${selectedCount.value} announcement(s)?`
  }
  return 'Delete this announcement?'
})

const deleteModalMessage = computed(() => {
  if (deleteTargetId.value === 'bulk') {
    return `This action cannot be undone. ${selectedCount.value} announcement(s) will be permanently removed from the system.`
  }
  return 'This action cannot be undone. The announcement will be permanently removed from the system.'
})
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Kiosk Announcements" />
        <p class="text-sm text-gray-500 mt-1">
          Create and schedule public notices for the community information kiosks.
        </p>
      </div>
      
      <div class="flex items-center space-x-2">
        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search announcements..."
          class="block px-4 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-all"
        />

        <!-- Delete Button -->
        <button 
          @click="bulkDelete"
          :disabled="selectionState === 'none'"
          :class="[selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50']"
          class="p-2 border border-red-700 rounded-lg transition-colors"
        >
          <TrashIcon class="w-5 h-5 text-red-700" />
        </button>

        <!-- Select Checkbox -->
        <div class="flex items-center border rounded-lg overflow-hidden"
          :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
        >
          <button 
            @click="handleMainSelectToggle"
            class="p-2 hover:bg-gray-50 flex items-center"
          >
            <div class="w-5 h-5 border rounded flex items-center justify-center" 
                 :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'">
              <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
              <svg v-if="selectionState === 'all'" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </button>
        </div>

        <!-- Add Button -->
        <button
          @click="startCreate"
          :disabled="loading || creatingNew"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !announcements.length" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-gray-500 mt-2">Loading announcements...</p>
      </div>
    </div>

    <!-- Grid -->
    <div v-else class="flex-1 overflow-y-auto pr-2 pt-2">
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
          :is-selected="selectedAnnouncements.has(item.id)"
          @edit="startEdit"
          @save="saveAnnouncement"
          @cancel="cancelEdit"
          @delete="requestDelete"
          @toggle-status="handleToggleStatus"
          @update:selected="(value) => handleSelectionUpdate(item.id, value)"
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
    :title="deleteModalTitle"
    :message="deleteModalMessage"
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />
</template>