<script setup>
import { ref, computed, onMounted } from 'vue'
import FeedbackReportCard from '@/views/feedback-and-reports/FeedbackReportCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getRFIDReports,
  undoRFIDReport,
  bulkUndoRFIDReports,
  deleteRFIDReport,
  bulkDeleteRFIDReports,
} from '@/api/idService'

const props = defineProps({
  searchQuery: { type: String, default: '' }
})

// ── State ──────────────────────────────────────────────────────
const reports = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedReports = ref(new Set())

const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)

// ── Fetch ──────────────────────────────────────────────────────
const fetchReports = async () => {
  isLoading.value = true
  errorMessage.value = null
  try {
    const { data } = await getRFIDReports()
    reports.value = data.map(r => ({
      id: r.id,
      requester: {
        firstName: r.resident_first_name || '',
        middleName: '',
        surname: r.resident_last_name || ''
      },
      rfidNo: r.rfid_uid || 'Guest Mode',
      createdOn: new Date(r.reported_at).toLocaleDateString('en-US', {
        month: 'long', day: 'numeric', year: 'numeric'
      }),
      isResolved: r.status === 'Resolved',
      raw: r
    }))
  } catch (err) {
    console.error('Failed to load RFID reports:', err)
    errorMessage.value = 'Failed to load reports. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// ── Confirm modal helpers ───────────────────────────────────────
const openConfirmModal = (title, action) => {
  confirmTitle.value = title
  confirmAction.value = action
  showConfirmModal.value = true
}

const handleConfirm = async () => {
  if (confirmAction.value) await confirmAction.value()
  showConfirmModal.value = false
  confirmAction.value = null
}

const handleCancel = () => {
  showConfirmModal.value = false
  confirmAction.value = null
}

// ── Undo (single) — reactivates RFID card ─────────────────────
const handleUndo = async (reportId) => {
  try {
    await undoRFIDReport(reportId)
    const r = reports.value.find(x => x.id === reportId)
    if (r) r.isResolved = true
  } catch (err) {
    console.error('Failed to undo report:', err)
    alert(err?.response?.data?.detail || 'Failed to undo report.')
  }
}

// ── Bulk undo ──────────────────────────────────────────────────
const bulkUndo = () => {
  if (selectedReports.value.size === 0) return
  openConfirmModal(
    `Undo ${selectedReports.value.size} selected reports? This will reactivate the residents' RFID cards.`,
    async () => {
      try {
        await bulkUndoRFIDReports(Array.from(selectedReports.value))
        const ids = new Set(selectedReports.value)
        reports.value.forEach(r => { if (ids.has(r.id)) r.isResolved = true })
        selectedReports.value = new Set()
      } catch (err) {
        console.error('Error during bulk undo:', err)
        alert('Failed to undo some reports. Please try again.')
      }
    }
  )
}

// ── Delete (single) ────────────────────────────────────────────
const handleDelete = (reportId) => {
  openConfirmModal(
    'Delete this report? The RFID card will remain deactivated.',
    async () => {
      try {
        await deleteRFIDReport(reportId)
        reports.value = reports.value.filter(r => r.id !== reportId)
        selectedReports.value.delete(reportId)
      } catch (err) {
        console.error('Failed to delete report:', err)
        alert('Failed to delete report.')
      }
    }
  )
}

// ── Bulk delete ────────────────────────────────────────────────
const bulkDelete = () => {
  if (selectedReports.value.size === 0) return
  openConfirmModal(
    `Delete ${selectedReports.value.size} selected reports?`,
    async () => {
      try {
        await bulkDeleteRFIDReports(Array.from(selectedReports.value))
        const ids = new Set(selectedReports.value)
        reports.value = reports.value.filter(r => !ids.has(r.id))
        selectedReports.value = new Set()
      } catch (err) {
        console.error('Error during bulk delete:', err)
        alert('Failed to delete some reports. Please try again.')
      }
    }
  )
}

// ── Selection ──────────────────────────────────────────────────
const selectAll = () => {
  selectedReports.value = new Set(filteredReports.value.map(r => r.id))
}

const deselectAll = () => {
  selectedReports.value = new Set()
}

const handleSelectionUpdate = (reportId, isSelected) => {
  const next = new Set(selectedReports.value)
  if (isSelected) next.add(reportId)
  else next.delete(reportId)
  selectedReports.value = next
}

// ── Expose to parent toolbar ───────────────────────────────────
defineExpose({
  selectedCount: computed(() => selectedReports.value.size),
  totalCount: computed(() => filteredReports.value.length),
  selectAll,
  deselectAll,
  bulkDelete,
  bulkUndo,
})

// ── Search filter ──────────────────────────────────────────────
const filteredReports = computed(() => {
  if (!props.searchQuery) return reports.value
  const q = props.searchQuery.toLowerCase()
  return reports.value.filter(r =>
    r.requester.firstName.toLowerCase().includes(q) ||
    r.requester.surname.toLowerCase().includes(q) ||
    r.rfidNo.toLowerCase().includes(q) ||
    r.createdOn.toLowerCase().includes(q)
  )
})

onMounted(fetchReports)
</script>

<template>
  <div class="space-y-4">
    <div v-if="isLoading" class="text-center p-10 text-gray-500">
      <p>Loading reports...</p>
    </div>

    <div v-else-if="errorMessage" class="text-center p-10 text-red-500">
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="filteredReports.length === 0" class="text-center p-10 text-gray-500">
      <h3 class="text-lg font-medium text-gray-700">No Reports Found</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No reports match your search.</span>
        <span v-else>There are currently no lost card reports.</span>
      </p>
    </div>

    <FeedbackReportCard
      v-for="report in filteredReports"
      :key="report.id"
      type="report"
      :id="String(report.id)"
      title="Lost Card Report"
      :requester="report.requester"
      :rfid-no="report.rfidNo"
      :created-on="report.createdOn"
      :is-selected="selectedReports.has(report.id)"
      :is-resolved="report.isResolved"
      @undo="handleUndo(report.id)"
      @delete="handleDelete(report.id)"
      @update:selected="(val) => handleSelectionUpdate(report.id, val)"
    />
  </div>

  <ConfirmModal
    :show="showConfirmModal"
    :title="confirmTitle"
    confirm-text="Yes"
    cancel-text="Cancel"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>