<script setup>
import { ref, computed, onMounted } from 'vue'
import FeedbackReportCard from '@/views/feedback-and-reports/FeedbackReportCard.vue'
import { getAllFeedbacks, deleteFeedback } from '@/api/feedbackService'

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  selectedItems: {
    type: Set,
    default: () => new Set()
  }
})

const emit = defineEmits(['update:selection'])

// --- REFS ---
const feedbacks = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)

// --- HELPERS ---
const getRatingLabel = (rating) => {
  const labels = {
    1: 'Very Poor',
    2: 'Poor',
    3: 'Average',
    4: 'Good',
    5: 'Excellent'
  }
  return labels[rating] || 'N/A'
}

const formatDate = (isoDate) => {
  if (!isoDate) return "N/A"
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

const getRequesterName = (feedback) => {
  if (!feedback.resident_first_name) {
    return 'Guest'
  }
  const middle = feedback.resident_middle_name ? ` ${feedback.resident_middle_name}` : ''
  return `${feedback.resident_first_name}${middle} ${feedback.resident_last_name}`
}

// --- FETCH FEEDBACKS ---
const fetchFeedbacks = async () => {
  try {
    const response = await getAllFeedbacks()
    feedbacks.value = response.map(fb => ({
      id: fb.id,
      type: 'feedback',
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
      comment: fb.additional_comments || '',
      isSelected: props.selectedItems.has(fb.id)
    }))
  } catch (error) {
    console.error('Error fetching feedbacks:', error)
    errorMessage.value = 'Failed to load feedbacks.'
  } finally {
    isLoading.value = false
  }
}

// --- DELETE FEEDBACK ---
const handleDelete = async (id) => {
  const confirmed = confirm('Are you sure you want to delete this feedback?')
  if (!confirmed) return

  try {
    await deleteFeedback(id)
    feedbacks.value = feedbacks.value.filter(fb => fb.id !== id)
  } catch (error) {
    console.error('Error deleting feedback:', error)
    alert('Failed to delete feedback. Please try again.')
  }
}

// --- HANDLE SELECTION ---
const handleSelectionUpdate = (id, isSelected) => {
  emit('update:selection', id, isSelected)
  // Update local state
  const feedback = feedbacks.value.find(fb => fb.id === id)
  if (feedback) {
    feedback.isSelected = isSelected
  }
}

// --- Load on mount ---
onMounted(fetchFeedbacks)

// --- COMPUTED: Search Filter ---
const filteredFeedbacks = computed(() => {
  if (!props.searchQuery) return feedbacks.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return feedbacks.value.filter(fb =>
    fb.title.toLowerCase().includes(lowerQuery) ||
    fb.requester.firstName.toLowerCase().includes(lowerQuery) ||
    fb.requester.surname.toLowerCase().includes(lowerQuery) ||
    fb.rfidNo.toLowerCase().includes(lowerQuery) ||
    fb.comment.toLowerCase().includes(lowerQuery) ||
    fb.ratingLabel.toLowerCase().includes(lowerQuery)
  )
})
</script>

<template>
  <div class="space-y-4 pt-4">
    <div v-if="isLoading" class="text-center p-10 text-gray-500">
      <p>Loading feedbacks...</p>
    </div>

    <div v-else-if="errorMessage" class="text-center p-10 text-red-500">
      <p>{{ errorMessage }}</p>
    </div>

    <div 
      v-else-if="filteredFeedbacks.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Feedbacks Found</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No feedbacks match your search.</span>
        <span v-else>No feedbacks have been submitted yet.</span>
      </p>
    </div>

    <FeedbackReportCard
      v-for="feedback in filteredFeedbacks"
      :key="feedback.id"
      :id="feedback.id.toString()"
      :type="feedback.type"
      :title="feedback.title"
      :requester="feedback.requester"
      :rfid-no="feedback.rfidNo"
      :created-on="feedback.createdOn"
      :rating="feedback.rating"
      :rating-label="feedback.ratingLabel"
      :comment="feedback.comment"
      :is-selected="feedback.isSelected"
      @delete="handleDelete"
      @update:selected="handleSelectionUpdate(feedback.id, $event)"
    />
  </div>
</template>