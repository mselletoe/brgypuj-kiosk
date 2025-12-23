<script setup>
import { ref, onMounted, watch } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'
import KioskAnnouncementCard from '@/views/announcements/KioskAnnouncementCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

import {
  getAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement as deleteAnnouncementApi
} from '@/api/announcements.js'

/* -------------------- STATE -------------------- */
const announcements = ref([])
const editingId = ref(null)
const creatingNew = ref(false)
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)

/* -------------------- LOAD DATA -------------------- */
onMounted(async () => {
  // local fallback
  const saved = localStorage.getItem('announcements')
  if (saved) announcements.value = JSON.parse(saved)

  // backend
  try {
    const data = await getAnnouncements()
    if (data?.length) {
      announcements.value = data.map(a => ({
        id: a.id,
        title: a.title,
        date: a.date,
        start: a.start,
        end: a.end,
        location: a.location,
        image: a.image
      }))
    }
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
  }
})

/* -------------------- PERSIST -------------------- */
watch(
  announcements,
  val => localStorage.setItem('announcements', JSON.stringify(val)),
  { deep: true }
)

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

const saveAnnouncement = async (form) => {
  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('event_date', form.date)
    formData.append('event_time', `${form.start} - ${form.end}`)
    formData.append('location', form.location)

    if (form.image instanceof File) {
      formData.append('image', form.image)
    }

    if (creatingNew.value) {
      const newItem = { id: Date.now(), ...form }
      announcements.value.unshift(newItem)
      await createAnnouncement(formData)
    } else {
      const index = announcements.value.findIndex(a => a.id === editingId.value)
      if (index !== -1) {
        announcements.value[index] = { ...announcements.value[index], ...form }
        await updateAnnouncement(editingId.value, formData)
      }
    }
  } catch (err) {
    console.error('Save failed:', err)
  }

  cancelEdit()
}

const deleteAnnouncement = async (id) => {
  announcements.value = announcements.value.filter(a => a.id !== id)
  try {
    await deleteAnnouncementApi(id)
  } catch (err) {
    console.error('Delete failed:', err)
  }
}

const requestDelete = (id) => {
  deleteTargetId.value = id
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  const id = deleteTargetId.value
  announcements.value = announcements.value.filter(a => a.id !== id)

  try {
    await deleteAnnouncementApi(id)
  } catch (err) {
    console.error('Delete failed:', err)
  }

  showDeleteModal.value = false
  deleteTargetId.value = null
}

const cancelDelete = () => {
  showDeleteModal.value = false
  deleteTargetId.value = null
}
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Kiosk Announcements" />
        <p class="text-sm text-gray-500 mt-1">Create and schedule public notices for the community information kiosks.</p>
      </div>
      <button
        @click="startCreate"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
      >
        Add Announcement
      </button>
    </div>

    <!-- Grid -->
    <div class="flex-1 overflow-y-auto pr-2">
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
            date: '',
            start: '',
            end: '',
            location: '',
            image: null
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
        />
      </div>

      <!-- Empty State -->
      <div
        v-else
        class="h-full flex items-center justify-center text-gray-500"
      >
        No announcements yet.
      </div>
    </div>
  </div>

  <ConfirmModal
    :show="showDeleteModal"
    title="Delete this announcement?"
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />
</template>
