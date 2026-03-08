<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const actions = [
  {
    label: "Send SMS",
    description: "Broadcast announcements",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>`,
    color: "text-blue-600",
    iconBg: "bg-blue-100",
    cardBg: "bg-blue-100 hover:bg-blue-200 border-blue-200",
    route: "/sms-announcements",
  },
  {
    label: "Notifications",
    description: "View recent alerts",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>`,
    color: "text-purple-600",
    iconBg: "bg-purple-100",
    cardBg: "bg-purple-100 hover:bg-purple-200 border-purple-200",
    route: "/notifications",
  },
  {
    label: "Account Settings",
    description: "Manage your account",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>`,
    color: "text-pink-600",
    iconBg: "bg-pink-100",
    cardBg: "bg-pink-100 hover:bg-pink-200 border-pink-200",
    route: "/account-settings",
  },
  {
    label: "Backup Data",
    description: "Manage backups",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7h16M4 7l2-3h8l2 3"/>`,
    color: "text-amber-600",
    iconBg: "bg-amber-100",
    cardBg: "bg-amber-100 hover:bg-amber-200 border-amber-200",
    route: "/system-settings",
    query: { tab: "backup" },
  },
  {
    label: "Maintenance",
    description: "Kiosk maintenance mode",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>`,
    color: "text-orange-600",
    iconBg: "bg-orange-100",
    cardBg: "bg-orange-100 hover:bg-orange-200 border-orange-200",
    route: "/system-settings",
    query: { tab: "preferences" },
  },
  {
    label: "Help & Support",
    description: "System reference guide",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>`,
    color: "text-green-600",
    iconBg: "bg-green-100",
    cardBg: "bg-green-100 hover:bg-green-200 border-green-200",
    route: "/help-and-support",
  },
];

const navigate = (action) => {
  router.push({ path: action.route, query: action.query });
};
</script>

<template>
  <div
    class="bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 min-h-[290px]"
  >
    <h3
      class="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-4"
    >
      Quick Actions
    </h3>
    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="(action, i) in actions"
        :key="action.label"
        @click="navigate(action)"
        class="quick-action-btn flex items-center gap-3 p-3 rounded-[14px] border transition-all duration-200 cursor-pointer text-left group h-[60px]"
        :class="action.cardBg"
        :style="{ animationDelay: `${0.05 + i * 0.05}s` }"
      >
        <div
          class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 transition-transform duration-200 group-hover:scale-110"
          :class="[action.iconBg, action.color]"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            v-html="action.icon"
          ></svg>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-[12px] font-bold text-gray-700 leading-tight">{{
            action.label
          }}</span>
          <span
            class="text-[10px] text-gray-400 font-medium leading-tight mt-0.5 truncate"
            >{{ action.description }}</span
          >
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.quick-action-btn {
  opacity: 0;
  animation: actionIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes actionIn {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
