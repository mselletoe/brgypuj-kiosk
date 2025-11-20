<script setup>
import { h } from 'vue'
import { NDataTable, NButton, NTag, NTooltip } from 'naive-ui'

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

const emit = defineEmits(['view'])

const columns = [
  {
    title: '#',
    key: 'index',
    width: 50,
    align: 'center',
    render: (row, rowIndex) => {
      return rowIndex + 1
    }
  },
  {
    title: 'Last Name',
    key: 'last_name',
    minWidth: 120,
  },
  {
    title: 'First Name',
    key: 'first_name',
    minWidth: 120,
  },
  {
    title: 'Middle Name',
    key: 'middle_name',
    minWidth: 120,
    render: (row) => row.middle_name || h('span', { class: 'text-gray-400' }, '—')
  },
  {
    title: 'Suffix',
    key: 'suffix',
    width: 60,
    render: (row) => row.suffix || h('span', { class: 'text-gray-400' }, '')
  },
  {
    title: 'RFID',
    key: 'rfid_uid',
    width: 120,
    render: (row) => {
      if (!row.rfid_uid) {
        return h(NTag, { size: 'small', type: 'warning' }, { default: () => 'Not Assigned' })
      }
      return h(
        NTooltip,
        {},
        {
          trigger: () => h('code', { class: 'text-xs bg-gray-100 px-2 py-1 rounded' }, row.rfid_uid),
          default: () => row.rfid_uid
        }
      )
    }
  },
  {
    title: 'Address',
    key: 'address',
    minWidth: 220,
    ellipsis: {
      tooltip: true
    },
    render: (row) => {
      const parts = [row.unit_blk_street, row.purok].filter(Boolean)
      return parts.length > 0 ? parts.join(', ') : h('span', { class: 'text-gray-400 italic' }, 'No address')
    }
  },
  {
    title: 'Contact',
    key: 'phone_number',
    width: 130,
    render: (row) => {
      return row.phone_number || h('span', { class: 'text-gray-400' }, '—')
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 100,
    align: 'center',
    fixed: 'right',
    render: (row) => {
      return h(
        NButton,
        {
          size: 'small',
          type: 'info',
          onClick: () => emit('view', row)
        },
        { default: () => 'View' }
      )
    }
  }
]

const rowKey = (row) => row.id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="residents"
    :loading="loading"
    :row-key="rowKey"
    :bordered="true"
    :single-line="false"
    size="small"
    :scroll-x="1100"
    class="rounded-lg shadow-sm"
  />
</template>

<style scoped>
:deep(.n-data-table-th) {
  font-weight: 600;
  background-color: #fafafa;
}

:deep(.n-data-table-td) {
  font-size: 13px;
}

:deep(.n-data-table-wrapper) {
  border-radius: 0.5rem;
}
</style>