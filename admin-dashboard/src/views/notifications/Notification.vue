<script setup>
import { ref, computed, watch, h, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
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
const router = useRouter()

const isMobile = ref(window.innerWidth < 640)
const onResize = () => { isMobile.value = window.innerWidth < 640 }
onMounted(() => {
  notifStore.fetchNotifications()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => window.removeEventListener('resize', onResize))

const searchQuery       = ref('')
const showFilterPopover = ref(false)
const selectedIds       = ref([])

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
  { label: 'All Types',    value: null },
  { label: 'Document',     value: 'Document' },
  { label: 'Equipment',    value: 'Equipment' },
  { label: 'Feedback',     value: 'Feedback' },
  { label: 'ID Services',  value: 'ID Services' },
]

const hasActiveFilters = computed(() =>
  !!(filterState.value.status || filterState.value.type)
)

const handleFilterClear = () => {
  filterState.value = { status: null, type: null }
}

const notifications = computed(() => notifStore.notifications)

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

const typeMeta = {
  Document:    { dot: 'bg-blue-500',   badge: 'bg-blue-50 text-blue-700 border-blue-200' },
  Equipment:   { dot: 'bg-orange-500', badge: 'bg-orange-50 text-orange-700 border-orange-200' },
  Feedback:    { dot: 'bg-teal-500',   badge: 'bg-teal-50 text-teal-700 border-teal-200' },
  'ID Services': { dot: 'bg-green-500', badge: 'bg-green-50 text-green-700 border-green-200' },
}

const REPORT_EVENTS = new Set(['new_lost_card_report'])

function navigateToRow(row) {
  switch (row.type) {
    case 'Document':
      router.push('/document-requests')
      break
    case 'Equipment':
      router.push('/equipment-requests')
      break
    case 'Feedback':
      router.push('/feedback-and-reports/feedbacks')
      break
    case 'ID Services':
      if (REPORT_EVENTS.has(row.event)) {
        router.push('/feedback-and-reports/reports')
      } else {
        router.push('/document-requests')
      }
      break
  }
}

const desktopColumns = [
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
    width: 150,
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
    minWidth: 200,
    render(row) {
      return h('div', { class: 'flex items-center gap-2 py-1' }, [
        row.unread ? h('span', { class: 'w-1.5 h-1.5 rounded-full bg-[#0d6efd] flex-shrink-0' }) : null,
        h('span', { class: `text-sm leading-snug ${row.unread ? 'font-semibold text-gray-900' : 'font-normal text-gray-600'}` }, row.msg),
      ].filter(Boolean))
    },
  },
  {
    key: 'datetime',
    title: 'Date & Time',
    width: 160,
    render(row) {
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'text-sm text-gray-700 font-medium' }, row.date),
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
]

const mobileColumns = [
  {
    key: 'select',
    width: 40,
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
    width: 120,
    render(row) {
      const meta = typeMeta[row.type] || { dot: 'bg-gray-400', badge: 'bg-gray-100 text-gray-600 border-gray-200' }
      return h(
        'span',
        { class: `inline-flex items-center gap-1.5 text-[11px] font-semibold px-2 py-1 rounded-full border ${meta.badge}` },
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
      return h('div', { class: 'flex items-start justify-between gap-2 py-1 min-w-0' }, [
        h('div', { class: 'flex items-start gap-2 min-w-0 flex-1' }, [
          row.unread ? h('span', { class: 'w-1.5 h-1.5 rounded-full bg-[#0d6efd] flex-shrink-0 mt-1.5' }) : null,
          h('div', { class: 'flex flex-col min-w-0' }, [
            h('span', {
              class: `text-sm leading-snug ${row.unread ? 'font-semibold text-gray-900' : 'font-normal text-gray-600'}`,
            }, row.msg),
            h('span', { class: 'text-xs text-gray-400 mt-1' }, `${row.date} · ${row.time}`),
          ]),
        ].filter(Boolean)),
        row.unread
          ? h('button', {
              title: 'Mark as read',
              onClick: (e) => { e.stopPropagation(); markRowAsRead(row) },
              class: 'flex-shrink-0 p-1.5 rounded-md text-[#0d6efd] hover:bg-blue-100 transition-colors',
            }, [h(EnvelopeOpenIcon, { class: 'w-4 h-4' })])
          : null,
      ].filter(Boolean))
    },
  },
]

const columns = computed(() => isMobile.value ? mobileColumns : desktopColumns)
</script>

<template>
  <div class="flex flex-col p-4 sm:p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- HEADER -->
    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto] items-center gap-4 mb-4">

      <!-- TITLE -->
      <div class="min-w-0">
        <PageTitle title="Notifications" />
        <p class="text-sm text-gray-500 mt-1">Manage all system notifications</p>
      </div>

      <!-- CONTROLS -->
      <div class="flex flex-nowrap items-center justify-start md:justify-end gap-3 w-full">

        <!-- SEARCH -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 flex-1 md:flex-none md:w-[180px] lg:w-[250px] min-w-0 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- ACTION BUTTONS -->
        <div class="flex items-center gap-2 sm:gap-3">

          <!-- FILTER POPOVER -->
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
                  'flex items-center px-3 py-2 border rounded-lg text-sm font-medium transition-colors',
                  hasActiveFilters
                    ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                ]"
              >
                <FunnelIcon class="w-5 h-5 sm:mr-2" :class="hasActiveFilters ? 'text-white' : 'text-gray-500'" />
                <span class="hidden sm:inline">Filter</span>
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

          <!-- MARK SELECTED AS READ -->
          <div class="relative group inline-block">
            <button
              @click="markSelectedAsRead"
              :disabled="selectionState === 'none'"
              class="p-2 border border-blue-400 rounded-lg transition-colors"
              :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-50'"
            >
              <EnvelopeOpenIcon class="w-5 h-5 text-[#0d6efd]" />
            </button>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Mark Selected as Read
            </div>
          </div>

          <!-- DELETE SELECTED -->
          <div class="relative group inline-block">
            <button
              @click="deleteSelected"
              :disabled="selectionState === 'none'"
              class="p-2 border border-red-400 rounded-lg transition-colors"
              :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'"
            >
              <TrashIcon class="w-5 h-5 text-red-500" />
            </button>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Delete Selected
            </div>
          </div>

          <!-- SELECT ALL -->
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
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Select All
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- STATS STRIP -->
    <div class="flex items-center gap-4 mb-4 h-8 justify-end">
      <span class="text-[12px] text-gray-400">
        {{ filteredNotifications.length }} notification{{ filteredNotifications.length !== 1 ? 's' : '' }}
        <template v-if="selectedCount > 0">
          · <span class="text-blue-600 font-medium">{{ selectedCount }} selected</span>
        </template>
      </span>
      <span
        v-if="filteredNotifications.filter(n => n.unread).length > 0"
        class="inline-flex items-center gap-1.5 text-[12px] font-medium text-[#0d6efd] bg-blue-50 border border-blue-100 px-2.5 py-0.5 rounded-full"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-[#0d6efd]" />
        {{ filteredNotifications.filter(n => n.unread).length }} unread
      </span>
    </div>

    <!-- TABLE -->
    <div class="overflow-auto bg-white rounded-lg border border-gray-200 h-[calc(100vh-320px)] sm:h-[calc(100vh-260px)]">
      <n-data-table
        :columns="columns"
        :data="filteredNotifications"
        :bordered="false"
        :row-props="(row) => ({
          class: row.unread ? 'bg-[#f0f7ff] hover:bg-blue-50 cursor-pointer' : 'hover:bg-gray-50 cursor-pointer',
          onClick: () => { markRowAsRead(row); navigateToRow(row) },
        })"
      />
      <div v-if="filteredNotifications.length === 0" class="py-16 text-center text-gray-400 text-[13px]">
        No notifications match your current filters.
      </div>
    </div>

  </div>
</template>