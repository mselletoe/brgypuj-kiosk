<script setup>
import { ref, h, computed } from "vue";
import { useRouter } from "vue-router";
import { NDropdown } from "naive-ui";
import {
  UserCircleIcon,
  QuestionMarkCircleIcon,
  BellIcon,
  ArrowLeftOnRectangleIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
} from "@heroicons/vue/24/solid";
import { useAdminAuthStore } from "@/stores/auth";
import GlobalSearch from "@/components/global-search/index.vue";

const router = useRouter();
const adminAuth = useAdminAuthStore();

// State Management
const showNotifications = ref(false);

// Notifications Mock
const recentNotifications = ref([
  { id: 1, title: "New Document Request", time: "5 minutes ago", unread: true },
  { id: 2, title: "Payment Completed", time: "1 hour ago", unread: true },
  { id: 3, title: "Equipment Overdue", time: "2 hours ago", unread: true },
]);

const unreadCount = computed(
  () => recentNotifications.value.filter((n) => n.unread).length,
);
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

const username = computed(() => adminAuth.admin?.username || "Admin");
const role = computed(() => adminAuth.admin?.role || "Administrator");
</script>

<template>
  <header class="pb-4 flex items-center justify-between w-full relative z-50">
    <div class="flex-1"></div>

    <div class="flex items-center gap-1.5">
      <!-- 🔍 Global Search -->
      <GlobalSearch />

      <button
        @click="router.push('/help-and-support')"
        class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
      >
        <QuestionMarkCircleIcon class="h-6 w-6" />
      </button>

      <button
        @click="router.push('/sms-announcements')"
        class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
      >
        <ChatBubbleLeftRightIcon class="h-6 w-6" />
      </button>

      <div class="relative">
        <div
          v-if="showNotifications"
          @click="showNotifications = false"
          class="fixed inset-0 z-40"
        ></div>
        <button
          @click="showNotifications = !showNotifications"
          class="w-11 h-11 flex items-center justify-center text-gray-500 rounded-full hover:text-blue-600 hover:bg-blue-50 transition-all relative"
        >
          <BellIcon class="h-6 w-6" />
          <span
            v-if="unreadCount > 0"
            class="absolute top-1.5 right-1.5 bg-red-500 text-white text-[9px] font-bold rounded-full border-2 border-[#F4F7FB] min-w-[18px] h-[18px] flex items-center justify-center"
          >
            {{ unreadCount }}
          </span>
        </button>

        <div
          v-if="showNotifications"
          class="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50"
        >
          <div
            class="px-5 py-4 border-b border-gray-50 font-bold text-gray-800 flex justify-between items-center"
          >
            <span>Notifications</span>
            <span
              class="text-xs font-semibold text-blue-600 cursor-pointer hover:underline"
            >
              Mark all read
            </span>
          </div>
          <div class="max-h-[320px] overflow-y-auto">
            <div
              v-for="notif in recentNotifications"
              :key="notif.id"
              class="px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 cursor-pointer flex justify-between items-center transition-colors"
            >
              <div class="flex flex-col pr-4">
                <span class="text-sm leading-tight font-bold text-gray-900">{{
                  notif.title
                }}</span>
                <span class="text-xs text-gray-400 mt-1">{{ notif.time }}</span>
              </div>
              <div
                v-if="notif.unread"
                class="w-2.5 h-2.5 rounded-full bg-blue-600"
              ></div>
            </div>
          </div>
          <div
            @click="router.push('/notifications')"
            class="py-3.5 text-center text-blue-600 text-xs hover:bg-blue-50 cursor-pointer bg-white font-bold transition-colors"
          >
            View All Notifications
          </div>
        </div>
      </div>

      <button
        @click="router.push('/system-settings')"
        class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
      >
        <Cog6ToothIcon class="h-6 w-6" />
      </button>

      <div class="w-px h-8 bg-gray-200 mx-2"></div>

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
            class="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center overflow-hidden border border-blue-200 group-hover:border-blue-300 transition-colors"
          >
            <img
              src="https://api.dicebear.com/7.x/adventurer/svg?seed=Jett"
              alt="Avatar"
              class="w-full h-full object-cover"
            />
          </div>
          <div class="flex flex-col text-left">
            <span class="text-sm font-bold text-gray-800 leading-none">{{
              username
            }}</span>
            <span
              class="text-[11px] font-semibold text-gray-500 mt-0.5 leading-none"
              >{{ role }}</span
            >
          </div>
        </button>
      </n-dropdown>
    </div>
  </header>
</template>
