<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import PageTitle from '@/components/shared/PageTitle.vue'
import {
  fetchPuroks,
  fetchSMSHistory,
  previewRecipients,
  sendSMSAnnouncement,
  RESIDENT_GROUPS,
} from '@/api/smsService'

// ── State ────────────────────────────────────────────────
const message       = ref('')
const isSending     = ref(false)
const sentSuccess   = ref(false)
const errorMessage  = ref('')
const recipientMode = ref('groups')

const groups = ref(RESIDENT_GROUPS.map(g => ({ ...g, count: '—' })))
const selectedGroups = ref([])

const puroks         = ref([])
const selectedPuroks = ref([])

const specificNumbers = ref('')
const history         = ref([])

const recipientCount   = ref(0)
const isResolvingCount = ref(false)

// ── Send progress (SSE) ───────────────────────────────────
const sendProgress     = ref(0)   // 0–100
const sendCurrent      = ref(0)
const sendTotal        = ref(0)
const sendResults      = ref([])  // { number, ok }[]

const templates = [
  { label: 'Assembly',           accent: 'blue',   text: 'Mahal na mga Residente, may barangay assembly sa [DATE] ng [TIME] sa [LUGAR]. Pakiusap ay dumalo.' },
  { label: 'Water Interruption', accent: 'cyan',   text: 'Abiso: Magkakaroon ng water interruption sa [DATE] mula [TIME] hanggang [TIME]. Mangyaring maghanda.' },
  { label: 'Emergency Alert',    accent: 'rose',   text: 'ALERTO: [DETALYE]. Mangyaring sumunod sa mga tagubilin ng mga awtoridad. Manatiling ligtas.' },
  { label: 'Health Program',     accent: 'green',  text: 'Libreng [PROGRAMA] sa [LUGAR] sa [DATE], [TIME]. Para sa lahat ng [GRUPO]. Magdala ng valid ID.' },
  { label: 'Document Pickup',    accent: 'amber',  text: 'Ang inyong hiniling na dokumento ay handa na. Pumunta sa barangay hall sa oras ng opisina.' },
  { label: 'Event Notice',       accent: 'purple', text: 'Imbitasyon: [EVENT] sa [DATE] sa [LUGAR]. [DETALYE]. Lahat ay malugod na tinatanggap.' },
]

// ── Color maps ───────────────────────────────────────────
const groupColorMap = {
  cyan:   { strip: 'bg-gradient-to-r from-white to-[#CBFCFF]', check: 'bg-[#06B6D4] border-[#06B6D4]', border: 'border-cyan-400',   bg: 'bg-cyan-50',   dot: '#06B6D4' },
  purple: { strip: 'bg-gradient-to-r from-white to-[#F5D6FF]', check: 'bg-[#8B5CF6] border-[#8B5CF6]', border: 'border-purple-400', bg: 'bg-purple-50', dot: '#8B5CF6' },
  blue:   { strip: 'bg-gradient-to-r from-white to-[#DBEAFE]', check: 'bg-[#3B82F6] border-[#3B82F6]', border: 'border-blue-400',   bg: 'bg-blue-50',   dot: '#3B82F6' },
  green:  { strip: 'bg-gradient-to-r from-white to-[#B6FFC2]', check: 'bg-[#10B981] border-[#10B981]', border: 'border-green-400',  bg: 'bg-green-50',  dot: '#10B981' },
  amber:  { strip: 'bg-gradient-to-r from-white to-[#FFF5D3]', check: 'bg-[#F59E0B] border-[#F59E0B]', border: 'border-amber-400',  bg: 'bg-amber-50',  dot: '#F59E0B' },
  rose:   { strip: 'bg-gradient-to-r from-white to-[#FFD6E0]', check: 'bg-[#F43F5E] border-[#F43F5E]', border: 'border-rose-400',   bg: 'bg-rose-50',   dot: '#F43F5E' },
}

// Purok color palette — cycles through if there are more puroks than entries
const purokColorList = [
  { strip: 'bg-gradient-to-r from-white to-[#CBFCFF]', check: 'bg-[#06B6D4] border-[#06B6D4]', border: 'border-cyan-400',   bg: 'bg-cyan-50',   dot: '#06B6D4' },
  { strip: 'bg-gradient-to-r from-white to-[#F5D6FF]', check: 'bg-[#8B5CF6] border-[#8B5CF6]', border: 'border-purple-400', bg: 'bg-purple-50', dot: '#8B5CF6' },
  { strip: 'bg-gradient-to-r from-white to-[#B6FFC2]', check: 'bg-[#10B981] border-[#10B981]', border: 'border-green-400',  bg: 'bg-green-50',  dot: '#10B981' },
  { strip: 'bg-gradient-to-r from-white to-[#FFF5D3]', check: 'bg-[#F59E0B] border-[#F59E0B]', border: 'border-amber-400',  bg: 'bg-amber-50',  dot: '#F59E0B' },
  { strip: 'bg-gradient-to-r from-white to-[#FFD6E0]', check: 'bg-[#F43F5E] border-[#F43F5E]', border: 'border-rose-400',   bg: 'bg-rose-50',   dot: '#F43F5E' },
  { strip: 'bg-gradient-to-r from-white to-[#DBEAFE]', check: 'bg-[#3B82F6] border-[#3B82F6]', border: 'border-blue-400',   bg: 'bg-blue-50',   dot: '#3B82F6' },
]

const templateAccentMap = {
  blue:   'hover:border-blue-300   hover:bg-blue-50   group-hover:text-blue-600',
  cyan:   'hover:border-cyan-300   hover:bg-cyan-50   group-hover:text-cyan-600',
  rose:   'hover:border-rose-300   hover:bg-rose-50   group-hover:text-rose-600',
  green:  'hover:border-green-300  hover:bg-green-50  group-hover:text-green-600',
  amber:  'hover:border-amber-300  hover:bg-amber-50  group-hover:text-amber-600',
  purple: 'hover:border-purple-300 hover:bg-purple-50 group-hover:text-purple-600',
}
const templateLabelMap = {
  blue:   'text-blue-600',
  cyan:   'text-cyan-600',
  rose:   'text-rose-600',
  green:  'text-green-600',
  amber:  'text-amber-600',
  purple: 'text-purple-600',
}

const charCount = computed(() => message.value.length)
const smsPages  = computed(() => Math.ceil(charCount.value / 160) || 1)

const canSend = computed(() => {
  if (!message.value.trim()) return false
  if (recipientMode.value === 'groups'   && !selectedGroups.value.length)  return false
  if (recipientMode.value === 'puroks'   && !selectedPuroks.value.length)  return false
  if (recipientMode.value === 'specific' && !specificNumbers.value.trim()) return false
  return true
})

// ── Live recipient count ──────────────────────────────────
let previewTimer = null

const resolveRecipientCount = async () => {
  const hasSelection =
    (recipientMode.value === 'groups'   && selectedGroups.value.length)  ||
    (recipientMode.value === 'puroks'   && selectedPuroks.value.length)  ||
    (recipientMode.value === 'specific' && specificNumbers.value.trim())

  if (!hasSelection) { recipientCount.value = 0; return }

  isResolvingCount.value = true
  try {
    const res = await previewRecipients(
      recipientMode.value,
      {
        groups:       selectedGroups.value,
        purokIds:     selectedPuroks.value,
        phoneNumbers: specificNumbers.value,
      }
    )
    recipientCount.value = res.count ?? 0
  } catch {
    // silently keep last count on transient failure
  } finally {
    isResolvingCount.value = false
  }
}

const schedulePreview = () => {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(resolveRecipientCount, 400)
}

watch([selectedGroups, selectedPuroks, specificNumbers, recipientMode], schedulePreview, { deep: true })

// ── Per-card population counts ────────────────────────────
const resolveGroupCounts = async () => {
  await Promise.allSettled(
    groups.value.map(async (g, idx) => {
      try {
        const res = await previewRecipients('groups', { groups: [g.id] })
        groups.value[idx] = { ...groups.value[idx], count: res.count }
      } catch {
        groups.value[idx] = { ...groups.value[idx], count: '?' }
      }
    })
  )
}

const resolvePurokCounts = async () => {
  await Promise.allSettled(
    puroks.value.map(async (p, idx) => {
      try {
        const res = await previewRecipients('puroks', { purokIds: [p.id] })
        puroks.value[idx] = { ...puroks.value[idx], count: res.count }
      } catch {
        puroks.value[idx] = { ...puroks.value[idx], count: '?' }
      }
    })
  )
}

// ── Methods ──────────────────────────────────────────────
const toggleGroup = (id) => {
  const i = selectedGroups.value.indexOf(id)
  i > -1 ? selectedGroups.value.splice(i, 1) : selectedGroups.value.push(id)
}
const togglePurok = (id) => {
  const i = selectedPuroks.value.indexOf(id)
  i > -1 ? selectedPuroks.value.splice(i, 1) : selectedPuroks.value.push(id)
}
const switchMode    = (mode) => { recipientMode.value = mode; selectedGroups.value = []; selectedPuroks.value = [] }
const applyTemplate = (text) => { message.value = text }

const handleSend = () => {
  if (!canSend.value || isSending.value) return

  isSending.value    = true
  errorMessage.value = ''
  sendProgress.value = 0
  sendCurrent.value  = 0
  sendTotal.value    = 0
  sendResults.value  = []

  // Capture message/selection before they reset on success
  const frozenMessage = message.value
  const frozenMode    = recipientMode.value
  const frozenGroups  = [...selectedGroups.value]
  const frozenPuroks  = [...selectedPuroks.value]

  const baseURL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`

  const payload = JSON.stringify({
    message:        frozenMessage,
    recipient_mode: frozenMode,
    groups:         frozenMode === 'groups'   ? frozenGroups  : undefined,
    purok_ids:      frozenMode === 'puroks'   ? frozenPuroks  : undefined,
    phone_numbers:  frozenMode === 'specific'
      ? specificNumbers.value.split(',').map(n => n.trim()).filter(Boolean)
      : undefined,
  })

  // Use fetch + ReadableStream to POST with SSE response
  fetch(`${baseURL}/admin/sms/send-stream`, {
    method:  'POST',
    headers: {
      'Content-Type':  'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') ?? ''}`,
    },
    body: payload,
  })
    .then(res => {
      if (!res.ok) return res.json().then(e => { throw e })
      const reader  = res.body.getReader()
      const decoder = new TextDecoder()
      let   buffer  = ''

      const pump = () => reader.read().then(({ done, value }) => {
        if (done) { isSending.value = false; return }

        buffer += decoder.decode(value, { stream: true })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() // keep incomplete frame

        for (const frame of frames) {
          const eventMatch = frame.match(/^event: (\w+)/m)
          const dataMatch  = frame.match(/^data: (.+)/m)
          if (!eventMatch || !dataMatch) continue

          const event = eventMatch[1]
          const data  = JSON.parse(dataMatch[1])

          if (event === 'start') {
            sendTotal.value = data.total
          }

          else if (event === 'progress') {
            sendCurrent.value  = data.current
            sendTotal.value    = data.total
            sendProgress.value = Math.round((data.current / data.total) * 100)
            sendResults.value.push({ number: data.number, ok: data.ok })
          }

          else if (event === 'done') {
            sendProgress.value = 100

            const modeLabel =
              frozenMode === 'groups'
                ? frozenGroups.map(id => groups.value.find(g => g.id === id)?.label).join(', ')
                : frozenMode === 'puroks'
                  ? frozenPuroks.map(id => puroks.value.find(p => p.id === id)?.purok_name).join(', ')
                  : 'Specific Numbers'

            const dotColors = ['#3B82F6', '#06B6D4', '#8B5CF6', '#10B981', '#F59E0B', '#F43F5E']
            history.value.unshift({
              id:         data.queued_at ?? Date.now(),
              preview:    frozenMessage.substring(0, 60) + (frozenMessage.length > 60 ? '...' : ''),
              recipients: data.sent,
              mode:       modeLabel,
              time:       'Just now',
              dot:        dotColors[history.value.length % dotColors.length],
            })

            sentSuccess.value     = true
            message.value         = ''
            selectedGroups.value  = []
            selectedPuroks.value  = []
            specificNumbers.value = ''
            recipientCount.value  = 0
            isSending.value       = false
            setTimeout(() => {
              sentSuccess.value  = false
              sendProgress.value = 0
              sendResults.value  = []
            }, 4000)
          }

          else if (event === 'error') {
            errorMessage.value = data.detail || 'SMS gateway error.'
            isSending.value    = false
          }
        }

        pump()
      })

      pump()
    })
    .catch(err => {
      errorMessage.value = err?.detail || 'Failed to send SMS. Please try again.'
      isSending.value    = false
    })
}

// ── Bootstrap ────────────────────────────────────────────
onMounted(async () => {
  try {
    const [purokList, historyList] = await Promise.all([
      fetchPuroks(),
      fetchSMSHistory(20),
    ])

    // Assign a color entry from purokColorList by index
    puroks.value = purokList.map((p, i) => ({
      ...p,
      name:  p.purok_name,
      count: '—',
      color: i % purokColorList.length,
    }))

    const histDots = ['#3B82F6', '#06B6D4', '#8B5CF6', '#10B981', '#F59E0B', '#F43F5E']
    history.value = historyList.map((h, i) => ({
      id:         h.id,
      preview:    h.message.substring(0, 60) + (h.message.length > 60 ? '...' : ''),
      recipients: h.recipients,
      mode:       h.mode,
      time:       formatRelativeTime(h.sent_at),
      dot:        histDots[i % histDots.length],
    }))
  } catch (err) {
    console.error('Failed to load SMS page data:', err)
  }

  resolveGroupCounts()
  resolvePurokCounts()
})

// ── Helpers ──────────────────────────────────────────────
function formatRelativeTime(isoString) {
  if (!isoString) return ''
  const diff = (Date.now() - new Date(isoString).getTime()) / 1000
  if (diff < 60)    return 'Just now'
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}
</script>

<template>
  <div class="flex flex-col p-3 sm:p-4 lg:p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- Header -->
    <div class="flex items-start justify-between mb-4 sm:mb-6 flex-shrink-0">
      <div>
        <PageTitle title="SMS Announcements" />
        <p class="text-sm text-gray-500 mt-1">Send targeted messages to specific resident groups</p>
      </div>
    </div>

    <!-- Success Banner -->
    <transition name="banner-slide">
      <div v-if="sentSuccess"
        class="mb-4 flex-shrink-0 bg-green-50 border-l-4 border-green-500 px-4 sm:px-5 py-3 rounded-r-xl shadow-sm flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
        </svg>
        <div>
          <p class="text-sm font-bold text-green-800">SMS Sent Successfully!</p>
          <p class="text-xs text-green-600 mt-0.5">Your message has been queued for delivery.</p>
        </div>
      </div>
    </transition>

    <!-- Error Banner -->
    <transition name="banner-slide">
      <div v-if="errorMessage"
        class="mb-4 flex-shrink-0 bg-red-50 border-l-4 border-red-500 px-4 sm:px-5 py-3 rounded-r-xl shadow-sm flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
          <p class="text-sm font-bold text-red-800">{{ errorMessage }}</p>
        </div>
        <button @click="errorMessage = ''" class="text-red-400 hover:text-red-600 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </transition>

    <!-- Body: stacks vertically on mobile/tablet, side-by-side on desktop -->
    <div class="flex flex-col lg:flex-row gap-4 sm:gap-6 flex-1 min-h-0 overflow-y-auto lg:overflow-hidden">

      <!-- LEFT column -->
      <div class="flex flex-col gap-4 sm:gap-6 flex-1 min-w-0 lg:overflow-y-auto lg:pr-1">

        <!-- Recipients Card -->
        <div class="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-sm border border-gray-200 flex-shrink-0">
          <div class="mb-4 sm:mb-6 flex items-start justify-between gap-2">
            <div>
              <h2 class="text-lg sm:text-xl font-bold text-gray-800 tracking-tight">Recipients</h2>
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">Select who receives this message</p>
            </div>
            <div :class="[
              'flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg border text-[11px] font-bold uppercase tracking-widest transition-all shrink-0',
              recipientCount > 0 ? 'bg-blue-50 border-blue-200 text-blue-600' : 'bg-gray-50 border-gray-200 text-gray-400'
            ]">
              <svg v-if="isResolvingCount" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              {{ recipientCount }} selected
            </div>
          </div>

          <!-- Mode tabs: wrap on mobile -->
          <div class="flex gap-1.5 sm:gap-2 mb-4 sm:mb-6">
            <button
              v-for="tab in [
                { id: 'groups',   label: 'Groups'           },
                { id: 'puroks',   label: 'By Purok'         },
                { id: 'specific', label: 'Specific Numbers' },
              ]"
              :key="tab.id"
              @click="switchMode(tab.id)"
              :class="[
                'flex-1 py-1.5 px-1.5 sm:px-3 rounded-lg text-[10px] sm:text-[11px] font-bold uppercase tracking-widest border transition-all',
                recipientMode === tab.id
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'text-gray-500 border-gray-200 bg-gray-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-700'
              ]"
            >{{ tab.label }}</button>
          </div>

          <!-- Groups grid: 1 col on mobile, 2 col on sm+ -->
          <div v-if="recipientMode === 'groups'">
            <div class="flex items-center justify-between mb-3 h-5">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest">Resident Groups</p>
              <button v-if="selectedGroups.length" @click="selectedGroups = []"
                class="text-[11px] font-bold text-blue-600 uppercase tracking-widest hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-lg transition-colors">
                Clear
              </button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                v-for="g in groups" :key="g.id"
                @click="toggleGroup(g.id)"
                :class="[
                  'relative overflow-hidden flex items-center justify-between p-3 sm:p-4 rounded-xl border-2 text-left transition-all group',
                  selectedGroups.includes(g.id)
                    ? groupColorMap[g.color].border + ' ' + groupColorMap[g.color].bg
                    : 'border-gray-100 bg-white hover:bg-gray-50'
                ]"
              >
                <div :class="['absolute right-0 top-0 h-full w-[10px] z-0 transition-all duration-500', groupColorMap[g.color].strip, selectedGroups.includes(g.id) ? 'w-full opacity-30' : '']"></div>
                <div class="relative z-10">
                  <p class="text-sm font-bold text-gray-700">{{ g.label }}</p>
                  <p class="text-xs text-gray-400 mt-0.5 italic">{{ g.count }} residents</p>
                </div>
                <div :class="[
                  'relative z-10 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all',
                  selectedGroups.includes(g.id) ? groupColorMap[g.color].check : 'border-gray-300 bg-white'
                ]">
                  <svg v-if="selectedGroups.includes(g.id)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
              </button>
            </div>
          </div>

          <!-- Puroks grid: 1 col on mobile, 2 col on sm+ -->
          <div v-if="recipientMode === 'puroks'">
            <div class="flex items-center justify-between mb-3 h-5">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest">Select Puroks</p>
              <button v-if="selectedPuroks.length" @click="selectedPuroks = []"
                class="text-[11px] font-bold text-blue-600 uppercase tracking-widest hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-lg transition-colors">
                Clear
              </button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                v-for="p in puroks" :key="p.id"
                @click="togglePurok(p.id)"
                :class="[
                  'relative overflow-hidden flex items-center justify-between p-3 sm:p-4 rounded-xl border-2 text-left transition-all group',
                  selectedPuroks.includes(p.id)
                    ? purokColorList[p.color].border + ' ' + purokColorList[p.color].bg
                    : 'border-gray-100 bg-white hover:border-gray-200'
                ]"
              >
                <div :class="['absolute right-0 top-0 h-full w-[10px] z-0 transition-all duration-500', purokColorList[p.color].strip, selectedPuroks.includes(p.id) ? 'w-full opacity-30' : '']"></div>
                <div class="relative z-10">
                  <p class="text-sm font-bold text-gray-700">{{ p.name }}</p>
                  <p class="text-xs text-gray-400 mt-0.5 italic">{{ p.count }} residents</p>
                </div>
                <div :class="[
                  'relative z-10 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all',
                  selectedPuroks.includes(p.id) ? purokColorList[p.color].check : 'border-gray-300 bg-white'
                ]">
                  <svg v-if="selectedPuroks.includes(p.id)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
              </button>
            </div>
          </div>

          <!-- Specific Numbers -->
          <div v-if="recipientMode === 'specific'">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 h-5">Phone Numbers</p>
            <textarea
              v-model="specificNumbers"
              placeholder="+639123456789, +639987654321, ..."
              rows="4"
              class="w-full border border-gray-200 rounded-xl p-3 text-sm text-gray-700 resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400 bg-gray-50"
            ></textarea>
            <div class="flex items-center justify-between mt-2">
              <p class="text-xs text-gray-400">Separate numbers with commas</p>
              <p v-if="specificNumbers.trim()" class="text-xs font-bold text-blue-600">
                {{ specificNumbers.split(',').filter(n => n.trim()).length }} number(s)
              </p>
            </div>
          </div>
        </div>

        <!-- Compose Card -->
        <div class="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-sm border border-gray-200 flex-shrink-0">
          <div class="mb-4 sm:mb-6 flex items-start justify-between gap-2">
            <div>
              <h2 class="text-lg sm:text-xl font-bold text-gray-800 tracking-tight">Compose Message</h2>
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">Write your announcement</p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span :class="['text-[11px] font-bold uppercase tracking-widest', charCount > 480 ? 'text-red-500' : 'text-gray-400']">
                {{ charCount }}/500
              </span>
              <span class="text-[11px] font-bold text-gray-500 uppercase tracking-widest bg-gray-50 border border-gray-200 rounded-lg px-2 sm:px-3 py-1.5">
                {{ smsPages }} SMS page{{ smsPages > 1 ? 's' : '' }}
              </span>
            </div>
          </div>

          <textarea
            v-model="message"
            placeholder="Type your announcement message here..."
            rows="7"
            maxlength="500"
            class="w-full border border-gray-200 rounded-xl p-3 sm:p-4 text-sm text-gray-700 resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400 bg-gray-50 leading-relaxed"
          ></textarea>

          <div class="mt-3 h-1 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300"
              :class="charCount > 480 ? 'bg-red-400' : charCount > 320 ? 'bg-yellow-400' : 'bg-blue-600'"
              :style="{ width: `${(charCount / 500) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Send Button + Progress -->
        <div class="flex flex-col gap-3 flex-shrink-0">

          <!-- Progress panel (visible while sending) -->
          <transition name="banner-slide">
            <div v-if="isSending" class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 sm:p-5 flex flex-col gap-3">

              <!-- Header row -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  <span class="text-sm font-bold text-gray-700">
                    Sending SMS...
                  </span>
                </div>
                <span class="text-xs font-bold text-blue-600 tabular-nums">
                  {{ sendCurrent }} / {{ sendTotal }}
                </span>
              </div>

              <!-- Progress bar -->
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-700 ease-out"
                  :class="sendProgress === 100 ? 'bg-green-500' : 'bg-blue-600'"
                  :style="{ width: sendProgress + '%' }"
                ></div>
              </div>

              <!-- Per-number result pills -->
              <div v-if="sendResults.length" class="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto">
                <span
                  v-for="(r, i) in sendResults" :key="i"
                  :class="[
                    'inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full',
                    r.ok
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  ]"
                >
                  <span>{{ r.ok ? '✓' : '✗' }}</span>
                  <span class="tabular-nums">{{ r.number }}</span>
                </span>
              </div>

            </div>
          </transition>

          <!-- Send button -->
          <button
            @click="handleSend"
            :disabled="!canSend || isSending"
            :class="[
              'w-full py-4 rounded-[20px] font-bold text-sm transition-all flex items-center justify-center gap-2',
              canSend && !isSending
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            ]"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"/>
            </svg>
            <span v-if="isSending">Sending {{ sendProgress }}%...</span>
            <span v-else>Send to {{ recipientCount }} Recipient{{ recipientCount !== 1 ? 's' : '' }}</span>
          </button>

        </div>

      </div>

      <!-- RIGHT sidebar: full-width on mobile/tablet, fixed-width column on desktop -->
      <div class="w-full lg:w-72 lg:shrink-0 flex flex-col sm:flex-row lg:flex-col gap-4 sm:gap-6 lg:overflow-y-auto">

        <!-- Templates Card -->
        <div class="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-sm border border-gray-200 flex-1 lg:flex-none">
          <div class="mb-4 sm:mb-6">
            <h2 class="text-lg sm:text-xl font-bold text-gray-800 tracking-tight">Templates</h2>
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">Quick message starters</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2">
            <button
              v-for="t in templates" :key="t.label"
              @click="applyTemplate(t.text)"
              :class="['w-full text-left p-3 rounded-xl border border-gray-100 transition-all group cursor-pointer', templateAccentMap[t.accent]]"
            >
              <p :class="['text-xs font-bold uppercase tracking-wide transition-colors', templateLabelMap[t.accent]]">{{ t.label }}</p>
              <p class="text-[13px] text-gray-500 font-medium mt-0.5 leading-relaxed line-clamp-2">{{ t.text }}</p>
            </button>
          </div>
        </div>

        <!-- History Card -->
        <div class="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-sm border border-gray-200 flex-1 lg:flex-none">
          <div class="mb-4 sm:mb-6">
            <h2 class="text-lg sm:text-xl font-bold text-gray-800 tracking-tight">Recent Sends</h2>
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">Send History</p>
          </div>

          <div v-if="!history.length" class="text-sm text-gray-400 text-center mt-4">No messages sent yet.</div>

          <div class="ml-2 border-l-2 border-gray-50 space-y-4">
            <div
              v-for="item in history.slice(0, 5)" :key="item.id"
              class="flex flex-col relative pl-6 py-2 -ml-1 pr-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="absolute -left-[6.5px] top-3 w-3.5 h-3.5 rounded-full border-2 border-white shadow-sm" :style="{ backgroundColor: item.dot }"></div>
              <div class="flex justify-between items-start">
                <span class="text-sm font-bold text-gray-700">{{ item.mode }}</span>
                <span class="text-[10px] font-bold text-gray-400 uppercase">{{ item.time }}</span>
              </div>
              <p class="text-[13px] text-gray-500 font-medium mt-0.5 leading-relaxed">{{ item.preview }}</p>
              <span class="text-xs text-gray-400 mt-1 italic">{{ item.recipients }} recipients</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.banner-slide-enter-active,
.banner-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.banner-slide-enter-from,
.banner-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>