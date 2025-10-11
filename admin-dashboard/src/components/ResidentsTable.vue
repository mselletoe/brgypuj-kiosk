<script setup>
import { ref, computed, onMounted } from 'vue'

// State
const residents = ref([])
const total = ref(0)
const page = ref(1)
const limit = 10

// Fetch data from API
const fetchResidents = async () => {
  try {
    const res = await fetch(
      `http://localhost:5000/api/residents?page=${page.value}&limit=${limit}`
    )
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const data = await res.json()

    residents.value = data.data
    total.value = data.total
  } catch (err) {
    console.error('Failed to load residents:', err)
  }
}

// Derived data
const totalPages = computed(() => Math.ceil(total.value / limit))
const startIndex = computed(() => (page.value - 1) * limit)
const endIndex = computed(() => Math.min(startIndex.value + residents.value.length, total.value))
const paginatedResidents = computed(() => residents.value)

// Methods
const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    fetchResidents()
  }
}

// Initial load
onMounted(fetchResidents)
</script>

<template>
  <div class="space-y-4">
    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="table table-xs w-full">
        <thead>
          <tr>
            <th>#</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Middle Name</th>
            <th>RFID UID</th>
            <th>Unit/Blk/Street</th>
            <th>Purok</th>
            <th>Phone Number</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(resident, index) in paginatedResidents" :key="resident.id">
            <th>{{ startIndex + index + 1 }}</th>
            <td>{{ resident.first_name }}</td>
            <td>{{ resident.last_name }}</td>
            <td>{{ resident.middle_name }}</td>
            <td>{{ resident.rfid_uid }}</td>
            <td>{{ resident.unit_blk_street }}</td>
            <td>{{ resident.purok }}</td>
            <td>{{ resident.phone_number }}</td>
          </tr>

          <tr v-if="paginatedResidents.length === 0">
            <td colspan="8" class="text-center text-gray-500 py-4">
              No residents found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <p class="text-sm text-gray-600">
        Showing {{ startIndex + 1 }}–{{ endIndex }} of {{ total }}
      </p>

      <div class="join">
        <button
          class="join-item btn btn-sm"
          :disabled="page === 1"
          @click="changePage(page - 1)"
        >
          «
        </button>

        <button class="join-item btn btn-sm btn-active">
          Page {{ page }}
        </button>

        <button
          class="join-item btn btn-sm"
          :disabled="page === totalPages"
          @click="changePage(page + 1)"
        >
          »
        </button>
      </div>
    </div>
  </div>
</template>