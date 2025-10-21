<script setup>
import { NDataTable } from 'naive-ui'

const props = defineProps({
  residents: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const columns = [
  { title: '#', key: 'index', render: (row, index) => index + 1, width: 60, align: 'center' },
  { title: 'Last Name', key: 'last_name' },
  { title: 'First Name', key: 'first_name' },
  { title: 'Middle Name', key: 'middle_name' },
  { title: 'RFID UID', key: 'rfid_uid' },
  { title: 'Unit/Blk/Street', key: 'unit_blk_street' },
  { title: 'Purok', key: 'purok' },
  { title: 'Phone Number', key: 'phone_number' },
]
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="residents"
    :loading="loading"
    :bordered="true"
    size="small"
    class="rounded-lg shadow-sm"
  />
</template>