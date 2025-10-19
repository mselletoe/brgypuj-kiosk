<script setup>
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentsTable from '@/components/ResidentsTable.vue'
import { NInput, NPagination, NSelect } from 'naive-ui'
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
    <ResidentsTable :residents="residents" :loading="loading" />

    <!-- Pagination -->
    <div class="mt-auto flex items-center justify-between text-sm text-gray-600">
      <p>Showing {{ residents.length }} of {{ total }}</p>
      <NPagination
        v-model:page="page"
        :page-count="Math.ceil(total / limit)"
        size="small"
        simple
      />
    </div>
  </div>
</template>