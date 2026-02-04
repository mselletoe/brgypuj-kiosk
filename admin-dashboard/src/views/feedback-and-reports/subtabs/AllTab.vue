<script setup>
import { ref, computed, onMounted } from 'vue'
import FeedbackReportCard from '@/views/feedback-and-reports/FeedbackReportCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getAllFeedbacks,
  deleteFeedback,
  bulkDeleteFeedbacks
} from '@/api/feedbackService'

/* ---------- PROPS ---------- */
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

/* ---------- STATE ---------- */
const feedbacks = ref([])
const selectedFeedbacks = ref(new Set())
const isLoading = ref(true)
const errorMessage = ref(null)

const showConfirmModal = ref(false)
const confirmTitle = ref('')
const confirmAction = ref(null)

/* ---------- HELPERS ---------- */
const getRatingLabel = (rating) => ({
  1: 'Very Poor',
  2: 'Poor',
  3: 'Average',
  4: 'Good',
  5: 'Excellent'
}[rating] || 'N/A')

const formatDate = (isoDate) => {
  if (!isoDate) return 'N/A'
  return new Date(isoDate).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

/* ---------- FETCH ---------- */
const fetchFeedbacks = async () => {
  isLoading.value = true
  try {
    const response = await getAllFeedbacks()
    feedbacks.value = response.map(fb => ({
      id: fb.id,
      title: fb.category,
      requester: {
        firstName: fb.resident_first_name || 'Guest',
        middleName: fb.resident_middle_name || '',
        surname: fb.resident_last_name || ''
      },
      rfidNo: fb.resident_rfid || 'Guest',
      createdOn: formatDate(fb.created_at),
      rating: fb.rating,
      ratingLabel: getRatingLabel(fb.rating),
      comment: fb.additional_comments || ''
    }))
  } catch (err) {
    console.error(err)
    errorMessage.value = 'Failed to load feedbacks.'
  } finally {
    isLoading.value = false
  }
}

/* ---------- SELECTION ---------- */
const handleSelectionUpdate = (id, isSelected) => {
  if (isSelected) {
    selectedFeedbacks.value.add(id)
  } else {
    selectedFeedbacks.value.delete(id)
  }
}

const selectAll = () => {
  selectedFeedbacks.value = new Set(filteredFeedbacks.value.map(f => f.id))
}

const deselectAll = () => {
  selectedFeedbacks.value.clear()
}

/* ---------- DELETE ---------- */
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

const handleDelete = (id) => {
  openConfirmModal('Delete this feedback?', async () => {
    await deleteFeedback(id)
    feedbacks.value = feedbacks.value.filter(f => f.id !== id)
    selectedFeedbacks.value.delete(id)
  })
}

const bulkDelete = () => {
  if (!selectedFeedbacks.value.size) return

  openConfirmModal(
    `Delete ${selectedFeedbacks.value.size} selected feedbacks?`,
    async () => {
      await bulkDeleteFeedbacks([...selectedFeedbacks.value])
      feedbacks.value = feedbacks.value.filter(
        f => !selectedFeedbacks.value.has(f.id)
      )
      selectedFeedbacks.value.clear()
    }
  )
}

/* ---------- EXPOSE (FOR TOOLBAR) ---------- */
defineExpose({
  selectedCount: computed(() => selectedFeedbacks.value.size),
  totalCount: computed(() => filteredFeedbacks.value.length),
  selectAll,
  deselectAll,
  bulkDelete
})

/* ---------- FILTER ---------- */
const filteredFeedbacks = computed(() => {
  if (!props.searchQuery) return feedbacks.value
  const q = props.searchQuery.toLowerCase()

  return feedbacks.value.filter(f =>
    f.title.toLowerCase().includes(q) ||
    f.requester.firstName.toLowerCase().includes(q) ||
    f.requester.surname.toLowerCase().includes(q) ||
    f.rfidNo.toLowerCase().includes(q) ||
    f.comment.toLowerCase().includes(q) ||
    f.ratingLabel.toLowerCase().includes(q)
  )
})

onMounted(fetchFeedbacks)
</script>

<template>
  <div class="space-y-4 pt-4">
    <FeedbackReportCard
      v-for="feedback in filteredFeedbacks"
      :key="feedback.id"
      :id="feedback.id"
      :title="feedback.title"
      :requester="feedback.requester"
      :rfid-no="feedback.rfidNo"
      :created-on="feedback.createdOn"
      :rating="feedback.rating"
      :rating-label="feedback.ratingLabel"
      :comment="feedback.comment"
      :is-selected="selectedFeedbacks.has(feedback.id)"
      @delete="handleDelete(feedback.id)"
      @update:selected="val => handleSelectionUpdate(feedback.id, val)"
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
