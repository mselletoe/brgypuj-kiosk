<script setup>
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentsTable from '@/components/ResidentsTable.vue'
import { NInput, NPagination } from 'naive-ui'
import { ref, watch, computed } from 'vue'

const residents = ref([])
const total = ref(0)
const page = ref(1)
const limit = 10
const query = ref('')
const loading = ref(false)

const fetchResidents = async () => {
  loading.value = true
  try {
    const res = await fetch(
      `http://localhost:5000/api/residents?page=${page.value}&limit=${limit}&q=${query.value}`
    )
    const data = await res.json()
    residents.value = data.data
    total.value = data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch([query, page], fetchResidents, { immediate: true })

const startIndex = computed(() => (page.value - 1) * limit + 1)
const endIndex = computed(() => Math.min(page.value * limit, total.value))
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-4">

    <header class="flex items-center justify-between space-x-20">
      <PageTitle title="Residents Information" />
      <NInput
        v-model:value="query"
        placeholder="Search residents..."
        clearable
        style="width: 400px;"
      />
    </header>

    <ResidentsTable :residents="residents" :loading="loading" />

    <div class="flex items-center justify-between text-sm text-gray-600">
      <p>
        Showing {{ startIndex }}–{{ endIndex }} of {{ total }}
      </p>

      <NPagination
        v-model:page="page"
        :page-size="limit"
        :item-count="total"
        size="small"
      />
    </div>
  </div>
</template>