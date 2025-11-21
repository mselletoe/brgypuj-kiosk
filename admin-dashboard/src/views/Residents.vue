<script setup>
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentsTable from '@/components/ResidentsTable.vue'
import { NInput, NPagination, NSelect, NModal, NCard } from 'naive-ui'
import { ref, onMounted, watch } from 'vue'
import { fetchResidents, fetchPuroks } from '@/api/residents'

// state
const residents = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const limit = 10
const query = ref('')
const searchFilter = ref('all')

const selectedValues = ref([])
const optionsRef = ref([])
const loadingSelect = ref(false)

const showModal = ref(false)
const residentData = ref(null)

const searchOptions = [
  { label: 'All', value: 'all' },
  { label: 'First Name', value: 'first_name' },
  { label: 'Last Name', value: 'last_name' },
  { label: 'Middle Name', value: 'middle_name' },
  { label: 'Phone Number', value: 'phone_number' }
]

// Fetch data from backend
const loadResidents = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      limit,
      query: query.value,
      filter: searchFilter.value,
      purok_ids: selectedValues.value.join(',')
    }

    const data = await fetchResidents(params)
    residents.value = data.residents || []
    total.value = data.total || residents.value.length
  } catch (err) {
    console.error('Failed to load residents:', err)
  } finally {
    loading.value = false
  }
}

const loadPuroks = async () => {
  loadingSelect.value = true
  try {
    const data = await fetchPuroks()
    optionsRef.value = data.map(p => ({
      label: p.purok_name,
      value: p.id
    }))
  } catch (err) {
    console.error('Failed to load puroks:', err)
  } finally {
    loadingSelect.value = false
  }
}

const handleView = (resident) => {
  residentData.value = resident // Store the resident's data
  showModal.value = true       // Show the modal
}

onMounted(() => {
  loadPuroks()
  loadResidents()
})

watch([page, query, searchFilter, selectedValues], loadResidents)
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5">
    <header class="flex items-center justify-between mb-8 space-x-5">
      <PageTitle title="Residents Information" />

      <!-- Search with filter -->
      <NInput
        v-model:value="query"
        placeholder="Search residents..."
        clearable
        style="width: 450px"
      >
        <template #suffix>
          <div>
            <NSelect
              v-model:value="searchFilter"
              :options="searchOptions"
              size="tiny"
              style="width: 120px;"
              clearable
              class="flex items-center h-full"
            />
          </div>
        </template>
      </NInput>

      <!-- Dynamic Purok filter -->
      <NSelect
        v-model:value="selectedValues"
        multiple
        filterable
        placeholder="Filter by Purok"
        :options="optionsRef"
        :loading="loadingSelect"
        remote
        :clear-filter-after-select="false"
        style="width: 150px;"
      />
    </header>

    <!-- Residents Table -->
    <ResidentsTable :residents="residents" :loading="loading" @view="handleView"/>

    <!-- Pagination -->
    <div class="mt-auto flex items-center justify-between text-xs text-gray-600">
      <p>Showing {{ residents.length }} of {{ total }}</p>
      <NPagination
        v-model:page="page"
        :page-count="Math.ceil(total / limit)"
        size="small"
        simple
      />
    </div>

    <NModal v-model:show="showModal" preset="card" style="width: 600px" :title="residentData ? `Viewing Resident: ${residentData.first_name} ${residentData.last_name}` : 'Resident Details'" :bordered="false" :mask-closable="true">
        <div v-if="residentData" class="space-y-3">
            <h3 class="text-lg font-semibold">Personal Information</h3>
            <p><strong>Full Name:</strong> {{ residentData.first_name }} {{ residentData.middle_name }} {{ residentData.last_name }} {{ residentData.suffix }}</p>
            <p><strong>RFID UID:</strong> <NTag :type="residentData.rfid_uid ? 'success' : 'warning'" size="small">{{ residentData.rfid_uid || 'Not Assigned' }}</NTag></p>
            <p><strong>Contact:</strong> {{ residentData.phone_number || 'N/A' }}</p>
            
            <h3 class="text-lg font-semibold pt-2">Address</h3>
            <p><strong>Unit/Blk/Street:</strong> {{ residentData.unit_blk_street || 'N/A' }}</p>
            <p><strong>Purok:</strong> {{ residentData.purok || 'N/A' }}</p>
            <p><strong>City/Barangay:</strong> {{ residentData.barangay || 'N/A' }}, {{ residentData.city || 'N/A' }}</p>
            </div>
        <div v-else>
            <p>No resident data available.</p>
        </div>
    </NModal>
  </div>
</template>