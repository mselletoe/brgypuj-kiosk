<script setup>
import { ref, h, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { NDropdown } from "naive-ui";
import {
  UserCircleIcon,
  BookOpenIcon,
  BellIcon,
  ArrowLeftOnRectangleIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
} from "@heroicons/vue/24/solid";
import { useAdminAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notification";
import GlobalSearch from "@/components/global-search/Index.vue";
import { getAdminProfile, getAdminPhotoUrl } from "@/api/accountSettingsService";

const router       = useRouter();
const adminAuth    = useAdminAuthStore();
const notifStore   = useNotificationStore();
const adminName     = ref('')
const adminPosition = ref('')
const photoUrl      = ref(null)
let   photoBlobUrl  = null
const REPORT_EVENTS = new Set(['new_lost_card_report'])

onMounted(async () => {
  try {
    const data = await getAdminProfile()

    const { first_name } = data.resident
    adminName.value     = [first_name].filter(Boolean).join(' ')
    adminPosition.value = data.position || data.system_role || 'Administrator'

    if (data.has_photo) {
      photoBlobUrl   = await getAdminPhotoUrl()
      photoUrl.value = photoBlobUrl
    }
  } catch {
    adminName.value     = adminAuth.admin?.username || 'Admin'
    adminPosition.value = 'Administrator'
  }
})

onUnmounted(() => {
  if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
})

const initial = computed(() => adminName.value?.charAt(0)?.toUpperCase() || '?')

const showNotifications = ref(false);

// Show only the 5 most recent in the dropdown preview
const recentNotifications = computed(() => 
  notifStore.notifications.slice(0, 5)
)

const unreadCount = computed(() => 
  notifStore.notifications.filter(n => n.unread).length
)

function markAllRead() { 
  const unreadIds = notifStore.notifications
    .filter(n => n.unread)
    .map(n => n.id)
  if (unreadIds.length) notifStore.markAllRead(unreadIds)
}

function handleNotifClick(notif) {
  notifStore.markRead(notif.id)
  showNotifications.value = false

  switch (notif.type) {
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
      if (REPORT_EVENTS.has(notif.event)) {
        router.push('/feedback-and-reports/reports')
      } else {
        router.push('/document-requests')
      }
      break
  }
}

const renderIcon = (icon) => () => h(icon, { class: "h-5 w-5" });

const dropdownOptions = [
  {
    label: "Account Settings",
    key: "profile",
    icon: renderIcon(UserCircleIcon),
  },
  { type: "divider" },
  {
    label: "Log Out",
    key: "logout",
    icon: renderIcon(ArrowLeftOnRectangleIcon),
  },
];

const handleSelect = (key) => {
  if (key === "profile") router.push("/account-settings");
  if (key === "logout") {
    adminAuth.logout();
    router.replace("/auth");
  }
};
</script>

<template>
  <header class="pb-4 flex items-center justify-between w-full relative z-50">
    <div class="flex-1"></div>

    <div class="flex items-center gap-1.5">
      <!-- Global Search -->
      <div class="relative group inline-block">
        <GlobalSearch />
        <div
          class="absolute -bottom-6 left-1/2 -translate-x-1/2
                 opacity-0 invisible group-hover:opacity-100 group-hover:visible
                 transition-all duration-300 ease-in-out
                 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                 whitespace-nowrap shadow-md z-50"
        >
          Search
        </div>
      </div>

      <!-- Help -->
      <div class="relative group inline-block">
        <button
          @click="router.push('/system-guide')"
          class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
        >
          <BookOpenIcon class="h-6 w-6" />
        </button>
        <div class="absolute -bottom-6 left-1/2 -translate-x-1/2
                    opacity-0 invisible group-hover:opacity-100 group-hover:visible
                    transition-all duration-300 ease-in-out
                    bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                    whitespace-nowrap shadow-md z-50">
          System Guide
        </div>
      </div>

      <!-- SMS Announcements -->
      <div class="relative group inline-block">
        <button
          @click="router.push('/sms-announcements')"
          class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
        >
          <ChatBubbleLeftRightIcon class="h-6 w-6" />
        </button>
        <div class="absolute -bottom-6 left-1/2 -translate-x-1/2
                    opacity-0 invisible group-hover:opacity-100 group-hover:visible
                    transition-all duration-300 ease-in-out
                    bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                    whitespace-nowrap shadow-md z-50">
          SMS Announcements
        </div>
      </div>

      <!-- Notifications -->
      <div class="relative">
        <div
          v-if="showNotifications"
          @click="showNotifications = false"
          class="fixed inset-0 z-40"
        ></div>

        <div class="relative group inline-block">
          <button
            @click="showNotifications = !showNotifications"
            class="w-11 h-11 flex items-center justify-center text-gray-500 rounded-full hover:text-blue-600 hover:bg-blue-50 transition-all relative"
          >
            <BellIcon class="h-6 w-6" />
            <span
              v-if="unreadCount > 0"
              class="absolute top-1.5 right-1.5 bg-red-500 text-white text-[9px] font-bold rounded-full border-2 border-[#F4F7FB] min-w-[18px] h-[18px] flex items-center justify-center"
            >
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </button>
          <div class="absolute -bottom-6 left-1/2 -translate-x-1/2
                      opacity-0 invisible group-hover:opacity-100 group-hover:visible
                      transition-all duration-300 ease-in-out
                      bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                      whitespace-nowrap shadow-md z-50">
            Notifications
          </div>
        </div>

        <div
          v-if="showNotifications"
          class="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50"
        >
          <!-- Header -->
          <div class="px-5 py-4 border-b border-gray-50 font-bold text-gray-800 flex justify-between items-center">
            <span>Notifications</span>
            <span
              @click="markAllRead"
              class="text-xs font-semibold text-blue-600 cursor-pointer hover:underline"
            >
              Mark all read
            </span>
          </div>

          <!-- List -->
          <div class="max-h-[320px] overflow-y-auto">
            <div
              v-if="recentNotifications.length === 0"
              class="px-5 py-8 text-center text-gray-400 text-xs"
            >
              No notifications yet
            </div>
            <div
              v-for="notif in recentNotifications"
              :key="notif.id"
              @click="handleNotifClick(notif)"
              class="px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 cursor-pointer flex justify-between items-center transition-colors"
            >
              <div class="flex flex-col pr-4">
                <span class="text-sm leading-tight font-medium text-gray-900">{{ notif.msg }}</span>
                <span class="text-xs text-gray-400 mt-1">{{ notif.date }} · {{ notif.time }}</span>
              </div>
              <div v-if="notif.unread" class="w-2.5 h-2.5 rounded-full bg-blue-600 flex-shrink-0"></div>
            </div>
          </div>

          <!-- Footer -->
          <div
            @click="router.push('/notifications'); showNotifications = false"
            class="py-3.5 text-center text-blue-600 text-xs hover:bg-blue-50 cursor-pointer bg-white font-bold transition-colors"
          >
            View All Notifications
          </div>
        </div>
      </div>

      <!-- System Settings -->
      <div class="relative group inline-block">
        <button
          @click="router.push('/system-settings')"
          class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
        >
          <Cog6ToothIcon class="h-6 w-6" />
        </button>
        <div
          class="absolute -bottom-6 left-1/2 -translate-x-1/2
                 opacity-0 invisible group-hover:opacity-100 group-hover:visible
                 transition-all duration-300 ease-in-out
                 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded
                 whitespace-nowrap shadow-md z-50"
        >
          System Settings
        </div>
      </div>

      <div class="w-px h-8 bg-gray-200 mx-2"></div>

      <!-- Admin Avatar + Dropdown -->
      <n-dropdown
        trigger="click"
        :options="dropdownOptions"
        @select="handleSelect"
        placement="bottom-end"
      >
        <button
          class="pl-2 pr-4 py-1.5 rounded-xl hover:bg-white border border-transparent hover:border-gray-200 hover:shadow-sm transition-all flex gap-3 items-center group"
        >
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center overflow-hidden border border-blue-200 group-hover:border-blue-300 transition-colors"
            :class="photoUrl ? '' : 'bg-indigo-100'"
          >
            <img
              v-if="photoUrl"
              :src="photoUrl"
              alt="Admin Avatar"
              class="w-full h-full object-cover"
            />
            <span
              v-else
              class="text-indigo-600 font-bold text-sm"
            >
              {{ initial }}
            </span>
          </div>

          <div class="flex flex-col text-left">
            <span class="text-sm font-bold text-gray-800 leading-none">{{ adminName }}</span>
            <span class="text-[11px] font-semibold text-gray-500 mt-0.5 leading-none">{{ adminPosition }}</span>
          </div>
        </button>
      </n-dropdown>
    </div>
  </header>
</template>