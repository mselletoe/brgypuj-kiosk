<script setup>
import { ref, onMounted, watch } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'
import { getAnnouncements, createAnnouncement, deleteAnnouncement as deleteAnnouncementApi } from '@/api/announcements.js'


// Load announcements from localStorage (or start with empty array)
const announcements = ref([])

onMounted(() => {
  const saved = localStorage.getItem('announcements')
  if (saved) {
    announcements.value = JSON.parse(saved)
  }
})

onMounted(async () => {
  try {
    const data = await getAnnouncements()
    if (data && data.length) {
      announcements.value = data.map(a => ({
        id: a.id,
        title: a.title,
        date: a.event_date,
        start: a.event_time, // or start/end if you split time
        end: a.event_time,
        location: a.location,
        image: a.image ? `data:image/jpeg;base64,${arrayBufferToBase64(a.image.data)}` : ''
      }))
    }
  } catch (err) {
    console.error('Error fetching announcements:', err)
  }
})

// helper: converts backend binary to base64 image
const arrayBufferToBase64 = (buffer) => {
  if (!buffer) return ''
  let binary = ''
  const bytes = new Uint8Array(buffer)
  const len = bytes.byteLength
  for (let i = 0; i < len; i++) binary += String.fromCharCode(bytes[i])
  return window.btoa(binary)
}

// Automatically save announcements to localStorage whenever they change
watch(announcements, (newVal) => {
  localStorage.setItem('announcements', JSON.stringify(newVal))
}, { deep: true })

const showModal = ref(false)
const editMode = ref(false)
const editId = ref(null)
const newAnnouncement = ref({
  title: '',
  date: '',
  start: '',
  end: '',
  location: '',
  image: ''
})
const imagePreview = ref(null)

const timeOptions = [
  '07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM',
  '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM',
  '01:00 PM', '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM',
  '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM', '06:00 PM', '06:30 PM',
  '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM'
]

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    newAnnouncement.value.image = URL.createObjectURL(file)
    imagePreview.value = newAnnouncement.value.image
  }
}

const openAddModal = () => {
  editMode.value = false
  showModal.value = true
  newAnnouncement.value = { title: '', date: '', start: '', end: '', location: '', image: '' }
  imagePreview.value = null
}

const addAnnouncement = async () => {
  if (!newAnnouncement.value.title || !newAnnouncement.value.image) {
    alert('Please fill out all required fields.')
    return
  }

  if (editMode.value) {
    const index = announcements.value.findIndex(a => a.id === editId.value)
    if (index !== -1) {
      announcements.value[index] = {
        ...announcements.value[index],
        ...newAnnouncement.value
      }
    }
  } else {
    announcements.value.push({
      id: Date.now(),
      ...newAnnouncement.value
    })
  }

  // Also send to backend
try {
  const formData = new FormData()
  formData.append('title', newAnnouncement.value.title)
  formData.append('event_date', newAnnouncement.value.date)
  formData.append('event_day', new Date(newAnnouncement.value.date).toLocaleDateString(undefined, { weekday: 'long' }))
  formData.append('event_time', `${newAnnouncement.value.start} - ${newAnnouncement.value.end}`)
  formData.append('location', newAnnouncement.value.location)

  // If the image is from a file input, convert URL back to File
  const inputEl = document.querySelector('input[type="file"]')
  if (inputEl && inputEl.files[0]) {
    formData.append('image', inputEl.files[0])
  }

  await createAnnouncement(formData)
  console.log('Announcement synced to backend.')
} catch (error) {
  console.error('Failed to sync with backend:', error)
}

  showModal.value = false
  editMode.value = false
  newAnnouncement.value = { title: '', date: '', start: '', end: '', location: '', image: '' }
  imagePreview.value = null
}

const openEditModal = (announcement) => {
  editMode.value = true
  editId.value = announcement.id
  newAnnouncement.value = { ...announcement }
  imagePreview.value = announcement.image
  showModal.value = true
}

const deleteAnnouncement = async (id) => {
  announcements.value = announcements.value.filter(a => a.id !== id)
  try {
    await deleteAnnouncementApi(id)
    console.log('Deleted from backend.')
  } catch (err) {
    console.error('Failed to delete from backend:', err)
  }
}
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5">
    <div class="flex justify-between items-center">
      <PageTitle title="Announcements" />
      <button
        @click="openAddModal"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center gap-1"
      >
        <span>➕</span> Add Announcement
      </button>
    </div>

    <!-- Announcements Grid -->
    <div v-if="announcements.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-7">
      <div
        v-for="item in announcements"
        :key="item.id"
        class="rounded-2xl bg-[#F3F3F3] overflow-hidden flex flex-col"
      >
        <img
          :src="item.image"
          alt="announcement"
          class="h-[80px] w-full object-cover"
        />
        <div class="p-6 flex flex-col justify-between flex-1">
          <div>
            <h3 class="text-xl font-bold text-[#4B4B4B]">{{ item.title }}</h3>

            <div class="mt-4 space-y-3 text-sm text-gray-700">
              <!-- Date & Time side by side -->
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <p class="font-medium text-[#808080]">Date</p>
                  <p class="font-semibold text-[#535353] mt-1">
                    {{
                      new Date(item.date).toLocaleDateString(undefined, {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                      })
                    }}, {{
                      new Date(item.date).toLocaleDateString(undefined, { weekday: 'long' })
                    }}
                  </p>
                </div>
                <div>
                  <p class="font-medium text-[#808080]">Time</p>
                  <p class="font-semibold text-[#535353] mt-1">{{ item.start }} - {{ item.end }}</p>
                </div>
              </div>

              <!-- Location below -->
              <div>
                <p class="mt-6 font-medium text-[#808080]">Location</p>
                <p class="font-semibold text-[#535353] mt-1">{{ item.location }}</p>
              </div>
            </div>
          </div>

          <div class="flex justify-between items-center mt-6">
            <button
              @click="openEditModal(item)"
              class="bg-[#BAF9B2] hover:bg-[#216917] text-[#216917] hover:text-white px-10 py-3 rounded-lg font-semibold text-sm"
            >
              Edit
            </button>
            <button
              @click="deleteAnnouncement(item.id)"
              class="bg-red-100 hover:bg-[#FFBABB] text-[#5D0E07] px-6 py-3 rounded-lg font-medium text-sm"
            >
              <span class="text-lg">🗑</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center text-gray-500 py-10">
      No announcements yet. Click <strong>"Add Announcement"</strong> to create one.
    </div>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-2xl w-full max-w-2xl p-6 shadow-xl">
        <!-- Upload Image Section -->
        <div
          class="bg-[#D0D0D0] border-2rounded-lg flex flex-col items-center justify-center h-40 mb-6 relative cursor-pointer"
        >
          <input
            type="file"
            accept="image/*"
            class="absolute inset-0 opacity-0 cursor-pointer"
            @change="handleImageUpload"
          />
          <template v-if="!imagePreview">
            <div class="flex flex-col items-center justify-center text-gray-500">
              <span class="text-3xl mb-1 text-white">+</span>
              <p class="text-sm font-medium text-white">Upload Image</p>
            </div>
          </template>
          <template v-else>
            <img
              :src="imagePreview"
              class="h-full w-full object-cover rounded-md"
            />
          </template>
        </div>

        <!-- Form Inputs -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold mb-1">Title of the Announcement</label>
            <input
              v-model="newAnnouncement.title"
              type="text"
              class="w-full border bg-[#D0D0D0] rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 "
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-semibold mb-1">Date</label>
              <input
                v-model="newAnnouncement.date"
                type="date"
                class="w-full border bg-[#D0D0D0] rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 "
              />
            </div>

            <div>
              <label class="block text-sm font-semibold mb-1">Start</label>
              <select
                v-model="newAnnouncement.start"
                class="w-full border bg-[#D0D0D0] rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option disabled value="">Select start time</option>
                <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold mb-1">End</label>
              <select
                v-model="newAnnouncement.end"
                class="w-full border bg-[#D0D0D0] rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 "
              >
                <option disabled value="">Select end time</option>
                <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold mb-1">Location</label>
            <input
              v-model="newAnnouncement.location"
              type="text"
              class="w-full border bg-[#D0D0D0] rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex justify-between items-center mt-6">
          <button
            @click="showModal = false"
            class="px-5 py-2 border border-blue-500 text-blue-600 rounded-md text-sm hover:bg-blue-50"
          >
            Cancel
          </button>
          <button
            @click="addAnnouncement"
            class="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            <span>{{ editMode ? 'Save Changes' : 'Upload' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
