<script setup>
import { ref, computed, watch, h, onMounted } from 'vue'
import { NDataTable, NCheckbox, NPopover, NSelect, NButton, useMessage } from 'naive-ui'
import {
  TrashIcon,
  CheckIcon,
  EnvelopeOpenIcon,
  FunnelIcon,
} from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import { useNotificationStore } from '@/stores/notification'

const message = useMessage()
const notifStore = useNotificationStore()

const searchQuery       = ref('')
const showFilterPopover = ref(false)
const selectedIds       = ref([])

// ── Fetch persisted notifications on mount ────────────────────────────────────
onMounted(() => {
  notifStore.fetchNotifications()
})

// ── Filter state ──────────────────────────────────────────────────────────────
const filterState = ref({
  status: null,
  type:   null,
})

const statusOptions = [
  { label: 'All Status', value: null },
  { label: 'Unread',     value: 'unread' },
  { label: 'Read',       value: 'read' },
]

const typeOptions = [
  { label: 'All Types', value: null },
  { label: 'Document',  value: 'Document' },
  { label: 'Payment',   value: 'Payment' },
  { label: 'Equipment', value: 'Equipment' },
  { label: 'Feedback',  value: 'Feedback' },
]

const hasActiveFilters = computed(() =>
  !!(filterState.value.status || filterState.value.type)
)

const handleFilterClear = () => {
  filterState.value = { status: null, type: null }
}

// ── Data — from Pinia store ───────────────────────────────────────────────────
const notifications = computed(() => notifStore.notifications)

// ── Filtering ─────────────────────────────────────────────────────────────────
const filteredNotifications = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return notifications.value.filter((n) => {
    const matchSearch = !q || n.msg.toLowerCase().includes(q) || n.type.toLowerCase().includes(q)
    const matchStatus =
      !filterState.value.status ||
      (filterState.value.status === 'unread' && n.unread) ||
      (filterState.value.status === 'read'   && !n.unread)
    const matchType = !filterState.value.type || n.type === filterState.value.type
    return matchSearch && matchStatus && matchType
  })
})

// ── Selection ─────────────────────────────────────────────────────────────────
const totalCount    = computed(() => filteredNotifications.value.length)
const selectedCount = computed(() => selectedIds.value.length)

const selectionState = computed(() => {
  if (totalCount.value === 0 || selectedCount.value === 0) return 'none'
  if (selectedCount.value < totalCount.value) return 'partial'
  return 'all'
})

function handleMainSelectToggle() {
  if (selectionState.value === 'all' || selectionState.value === 'partial') {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredNotifications.value.map((n) => n.id)
  }
}

watch(searchQuery, () => { selectedIds.value = [] })

// ── Actions ───────────────────────────────────────────────────────────────────
function markSelectedAsRead() {
  if (!selectedIds.value.length) return
  notifStore.markAllRead(selectedIds.value)
  message.success(`${selectedIds.value.length} notification(s) marked as read.`)
  selectedIds.value = []
}

function deleteSelected() {
  if (!selectedIds.value.length) return
  const count = selectedIds.value.length
  notifStore.deleteMany(selectedIds.value)
  selectedIds.value = []
  message.success(`${count} notification(s) deleted.`)
}

function markRowAsRead(row) {
  notifStore.markRead(row.id)
}

// ── Type meta ─────────────────────────────────────────────────────────────────
const typeMeta = {
  Document:  { dot: 'bg-[#D946EF]', badge: 'bg-purple-50 text-purple-700 border-purple-200' },
  Payment:   { dot: 'bg-[#10B981]', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  Equipment: { dot: 'bg-[#F59E0B]', badge: 'bg-amber-50 text-amber-700 border-amber-200' },
  Feedback:  { dot: 'bg-[#3B82F6]', badge: 'bg-blue-50 text-blue-700 border-blue-200' },
}

// ── NDataTable columns ────────────────────────────────────────────────────────
const columns = computed(() => [
  {
    key: 'select',
    width: 48,
    title: '',
    render(row) {
      return h(NCheckbox, {
        checked: selectedIds.value.includes(row.id),
        onUpdateChecked(checked) {
          if (checked) {
            if (!selectedIds.value.includes(row.id)) selectedIds.value.push(row.id)
          } else {
            selectedIds.value = selectedIds.value.filter((id) => id !== row.id)
          }
        },
      })
    },
  },
  {
    key: 'type',
    title: 'Type',
    width: 140,
    render(row) {
      const meta = typeMeta[row.type] || { dot: 'bg-gray-400', badge: 'bg-gray-100 text-gray-600 border-gray-200' }
      return h(
        'span',
        { class: `inline-flex items-center gap-1.5 text-[12px] font-semibold px-2.5 py-1 rounded-full border ${meta.badge}` },
        [
          h('span', { class: `w-1.5 h-1.5 rounded-full flex-shrink-0 ${meta.dot}` }),
          row.type,
        ]
      )
    },
  },
  {
    key: 'msg',
    title: 'Notification',
    render(row) {
      return h('div', { class: 'flex items-center gap-2' }, [
        row.unread ? h('span', { class: 'w-1.5 h-1.5 rounded-full bg-[#0d6efd] flex-shrink-0' }) : null,
        h('span', { class: `text-md ${row.unread ? 'font-semibold text-gray-900' : 'font-normal text-gray-600'}` }, row.msg),
      ].filter(Boolean))
    },
  },
  {
    key: 'datetime',
    title: 'Date & Time',
    width: 180,
    render(row) {
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'text-s text-gray-700 font-medium' }, row.date),
        h('span', { class: 'text-xs text-gray-400 mt-0.5' }, row.time),
      ])
    },
  },
  {
    key: 'action',
    title: '',
    width: 48,
    render(row) {
      return row.unread
        ? h('button', {
            title: 'Mark as read',
            onClick: () => markRowAsRead(row),
            class: 'p-1.5 rounded-md text-[#0d6efd] hover:bg-blue-100 transition-colors',
          }, [h(EnvelopeOpenIcon, { class: 'w-4 h-4' })])
        : null
    },
  },
])
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Notifications" />
        <p class="text-sm text-gray-500 mt-1">Manage all system notifications</p>
      </div>

      <div class="flex items-center gap-3">

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px]
                 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
                 transition-all placeholder:text-gray-400"
        />

        <!-- Filter popover -->
        <n-popover
          v-model:show="showFilterPopover"
          trigger="click"
          placement="bottom-end"
          :show-arrow="false"
          style="padding: 0;"
        >
          <template #trigger>
            <button
              :class="[
                'flex items-center px-4 py-2 border rounded-lg text-sm font-medium transition-colors',
                hasActiveFilters
                  ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
            >
              <FunnelIcon class="w-5 h-5 mr-2" :class="hasActiveFilters ? 'text-white' : 'text-gray-500'" />
              Filter
            </button>
          </template>

          <div class="w-[240px] bg-white rounded-lg overflow-hidden flex flex-col">
            <div class="p-4 border-b border-gray-200">
              <h3 class="text-[16px] font-semibold text-gray-800">Filter Notifications</h3>
            </div>
            <div class="px-4 py-4 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <n-select v-model:value="filterState.status" :options="statusOptions" placeholder="All Status" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
                <n-select v-model:value="filterState.type" :options="typeOptions" placeholder="All Types" />
              </div>
            </div>
            <div class="flex justify-end p-4 border-t border-gray-200">
              <n-button secondary @click="handleFilterClear">Clear</n-button>
            </div>
          </div>
        </n-popover>

        <!-- Mark Selected as Read -->
        <div class="relative group inline-block">
          <button
            @click="markSelectedAsRead"
            :disabled="selectionState === 'none'"
            class="p-2 border border-blue-400 rounded-lg transition-colors"
            :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-50'"
          >
            <EnvelopeOpenIcon class="w-5 h-5 text-[#0d6efd]" />
          </button>
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2
                      opacity-0 invisible group-hover:opacity-100 group-hover:visible
                      transition-all duration-300 ease-in-out
                      bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                      whitespace-nowrap shadow-md z-50">
            Mark Selected as Read
          </div>
        </div>

        <!-- Delete Selected -->
        <div class="relative group inline-block">
          <button
            @click="deleteSelected"
            :disabled="selectionState === 'none'"
            class="p-2 border border-red-400 rounded-lg transition-colors"
            :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'"
          >
            <TrashIcon class="w-5 h-5 text-red-500" />
          </button>
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2
                      opacity-0 invisible group-hover:opacity-100 group-hover:visible
                      transition-all duration-300 ease-in-out
                      bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                      whitespace-nowrap shadow-md z-50">
            Delete Selected
          </div>
        </div>

        <!-- Select All -->
        <div class="relative group inline-block">
          <div
            class="flex items-center border rounded-lg overflow-hidden transition-colors"
            :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
          >
            <button @click="handleMainSelectToggle" class="p-2 hover:bg-gray-50 flex items-center">
              <div
                class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
                :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'"
              >
                <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white" />
                <svg v-if="selectionState === 'all'" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </button>
          </div>
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2
                      opacity-0 invisible group-hover:opacity-100 group-hover:visible
                      transition-all duration-300 ease-in-out
                      bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                      whitespace-nowrap shadow-md z-50">
            Select All
          </div>
        </div>

      </div>
    </div>

    <!-- ── Stats strip ─────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-4 mb-4 justify-end">
      <span class="text-[12px] text-gray-400">
        {{ filteredNotifications.length }} notification{{ filteredNotifications.length !== 1 ? 's' : '' }}
        <template v-if="selectedCount > 0">
          · <span class="text-blue-600 font-medium">{{ selectedCount }} selected</span>
        </template>
      </span>
      <span
        v-if="filteredNotifications.filter(n => n.unread).length > 0"
        class="inline-flex items-center gap-1.5 text-[12px] font-medium text-[#0d6efd]
               bg-blue-50 border border-blue-100 px-2.5 py-0.5 rounded-full"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-[#0d6efd]" />
        {{ filteredNotifications.filter(n => n.unread).length }} unread
      </span>
    </div>

    <!-- ── Table ───────────────────────────────────────────────────────────── -->
    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200 flex-1">
      <n-data-table
        :columns="columns"
        :data="filteredNotifications"
        :bordered="false"
        :row-props="(row) => ({
          class: row.unread ? 'bg-[#f0f7ff] hover:bg-blue-50 cursor-pointer' : 'hover:bg-gray-50 cursor-pointer',
          onClick: () => markRowAsRead(row),
        })"
      />
      <div v-if="filteredNotifications.length === 0" class="py-16 text-center text-gray-400 text-[13px]">
        No notifications match your current filters.
      </div>
    </div>

  </div>
</template>