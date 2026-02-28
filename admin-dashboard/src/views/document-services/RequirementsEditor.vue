<script setup>
import { ref, watch } from 'vue'
import { NModal, NButton, NSelect, NInput, useMessage } from 'naive-ui'
import { XMarkIcon, PlusIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  requirementsData: {
    type: Array,
    default: () => []
  },
  serviceId: {
    type: Number,
    default: null
  }
})

const message = useMessage()
const emit = defineEmits(['close', 'saved'])

const editingRequirements = ref([])

const systemCheckOptions = [
  { label: 'Clean Blotter Record', value: 'clean_blotter' },
  { label: 'Minimum Years of Residency', value: 'min_residency' }
]

// Sync local copy when modal opens
watch(() => props.show, (val) => {
  if (val) {
    editingRequirements.value = JSON.parse(JSON.stringify(props.requirementsData || []))
  }
})

function addRequirement(type) {
  if (type === 'document') {
    editingRequirements.value.push({
      id: `doc_${Date.now()}`,
      label: '',
      type: 'document',
      params: null
    })
  } else {
    editingRequirements.value.push({
      id: '',
      label: '',
      type: 'system_check',
      params: {}
    })
  }
}

function removeRequirement(index) {
  editingRequirements.value.splice(index, 1)
}

function onSystemCheckSelect(index, value) {
  const req = editingRequirements.value[index]
  req.id = value
  if (value === 'clean_blotter') {
    req.label = req.label || 'Clean Blotter Record'
    req.params = null
  } else if (value === 'min_residency') {
    req.label = req.label || 'Minimum Residency'
    req.params = { years: 0, months: 6 }
    updateResidencyLabel(index)
  }
}

function updateResidencyLabel(index) {
  const req = editingRequirements.value[index]
  if (req.id !== 'min_residency') return
  const y = req.params?.years ?? 0
  const m = req.params?.months ?? 0
  const parts = []
  if (y > 0) parts.push(`${y} year${y !== 1 ? 's' : ''}`)
  if (m > 0) parts.push(`${m} month${m !== 1 ? 's' : ''}`)
  req.label = `Minimum ${parts.join(' and ') || '0 months'} of Residency`
}

function handleSave() {
  for (const req of editingRequirements.value) {
    if (req.type === 'system_check' && !req.id) {
      message.warning('Please select a check type for all system requirements.')
      return
    }
    if (req.type === 'document' && !req.label.trim()) {
      message.warning('Please enter a label for all document requirements.')
      return
    }
  }
  emit('saved', [...editingRequirements.value], props.serviceId)
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <NModal :show="show" @update:show="handleClose" :mask-closable="false">
    <div class="w-[640px] max-h-[80vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
        <div>
          <h2 class="text-base font-semibold text-gray-800">Edit Requirements</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            Define what residents must meet or submit to request this document.
          </p>
        </div>
        <button @click="handleClose" class="p-1 rounded hover:bg-gray-200 transition">
          <XMarkIcon class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-4 overflow-y-auto space-y-3 flex-1">

        <!-- Empty state -->
        <p v-if="editingRequirements.length === 0" class="text-sm text-gray-400 text-center py-6">
          No requirements set. Add one below.
        </p>

        <!-- Requirement rows -->
        <div
          v-for="(req, index) in editingRequirements"
          :key="index"
          class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
        >
          <!-- Type badge -->
          <div class="pt-1">
            <span
              class="text-xs font-semibold px-2 py-0.5 rounded-full"
              :class="req.type === 'system_check' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'"
            >
              {{ req.type === 'system_check' ? 'System' : 'Document' }}
            </span>
          </div>

          <!-- Fields -->
          <div class="flex-1 space-y-2">
            <!-- System check: select which check -->
            <NSelect
              v-if="req.type === 'system_check'"
              :value="req.id"
              :options="systemCheckOptions"
              placeholder="Select check type..."
              @update:value="(v) => onSystemCheckSelect(index, v)"
            />

            <!-- Label -->
            <n-input
              v-model:value="req.label"
              :placeholder="req.type === 'document' ? 'e.g. Valid Government-Issued ID' : 'Display label (auto-filled)'"
              size="small"
            />

            <!-- min_residency params: years + months -->
            <div v-if="req.id === 'min_residency'" class="flex items-center gap-3 flex-wrap">
              <div class="flex items-center gap-1.5">
                <span class="text-xs text-gray-500">Years:</span>
                <n-input
                  :value="String(req.params?.years ?? 0)"
                  type="number"
                  size="small"
                  style="width: 72px"
                  @update:value="(v) => { req.params = { ...req.params, years: Math.max(0, Number(v)) }; updateResidencyLabel(index) }"
                />
              </div>
              <div class="flex items-center gap-1.5">
                <span class="text-xs text-gray-500">Months:</span>
                <n-input
                  :value="String(req.params?.months ?? 0)"
                  type="number"
                  size="small"
                  style="width: 72px"
                  @update:value="(v) => { req.params = { ...req.params, months: Math.min(11, Math.max(0, Number(v))) }; updateResidencyLabel(index) }"
                />
              </div>
              <span class="text-xs text-gray-400 italic">
                ({{ (req.params?.years ?? 0) * 12 + (req.params?.months ?? 0) }} months total)
              </span>
            </div>
          </div>

          <!-- Remove -->
          <button @click="removeRequirement(index)" class="pt-1 text-red-400 hover:text-red-600 transition">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>

        <!-- Add buttons -->
        <div class="flex gap-2 pt-2">
          <button
            @click="addRequirement('system_check')"
            class="flex items-center gap-1.5 text-sm text-blue-600 border border-blue-300 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition"
          >
            <PlusIcon class="w-4 h-4" />
            System Check
          </button>
          <button
            @click="addRequirement('document')"
            class="flex items-center gap-1.5 text-sm text-amber-600 border border-amber-300 hover:bg-amber-50 px-3 py-1.5 rounded-lg transition"
          >
            <PlusIcon class="w-4 h-4" />
            Document
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-3 px-6 py-4 border-t">
        <NButton @click="handleClose">Cancel</NButton>
        <NButton type="primary" @click="handleSave">Save Requirements</NButton>
      </div>

    </div>
  </NModal>
</template>