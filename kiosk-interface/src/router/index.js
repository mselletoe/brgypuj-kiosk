import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import UserLayout from "@/layouts/UserLayout.vue";

// Only eagerly import the most critical first-render routes
import Idle from "@/views/idle/Idle.vue";
import Login from "@/views/auth/Login.vue";

const routes = [
  { path: "/", redirect: "/idle" },
  { path: "/display", name: "Display", component: () => import("@/views/idle/Display.vue") },
  { path: "/idle", name: "Idle", component: Idle },
  { path: "/announcements", name: "Announcements", component: () => import("@/views/idle/Announcements.vue") },
  { path: "/login", name: "LoginSelection", component: Login },
  { path: "/login-rfid", name: "ScanRFID", component: () => import("@/views/auth/ScanRFID.vue") },
  { path: "/auth-pin", name: "VerifyPIN", component: () => import("@/views/auth/AuthPIN.vue") },
  { path: "/inannouncements", name: "InAnnouncements", component: () => import("@/views/announcements/Announcement.vue") },

  {
    path: "/",
    component: UserLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "home", name: "Home", component: () => import("@/views/home/KioskHome.vue") },
      {
        path: "document-services",
        name: "DocumentServices",
        component: () => import("@/views/document-services/DocumentServices.vue"),
        children: [{ path: ":docType", component: () => import("@/views/document-services/DocumentFormWrapper.vue") }],
      },
      { path: "id-services", name: "IDServices", component: () => import("@/views/id-services/IDServices.vue") },
      { path: "id-services/change-pin", name: "ChangePasscode", component: () => import("@/views/id-services/ChangePasscode.vue") },
      { path: "id-services/report-lost", name: "ReportLost", component: () => import("@/views/id-services/ReportLost.vue") },
      { path: "id-services/apply", name: "ApplyID", component: () => import("@/views/id-services/applyid/ApplyID.vue"), meta: { noBottomPadding: true } },
      { path: "equipment-borrowing", name: "EquipmentBorrowing", component: () => import("@/views/equipment-borrowing/EquipmentBorrowing.vue") },
      { path: "help-and-support", name: "Support", component: () => import("@/views/help-and-support/HelpAndSupport.vue") },
      { path: "feedback", name: "Feedback", component: () => import("@/views/feedback/Feedback.vue") },
      { path: "rating", name: "Rating", component: () => import("@/views/feedback/Rating.vue") },
      { path: "comments", name: "Comments", component: () => import("@/views/feedback/Comments.vue") },
      { path: "register", name: "Register", component: () => import("@/views/auth/Register.vue"), meta: { guestAllowed: true } },
      { path: "component-showcase", name: "DevShowcase", component: () => import("@/components/ComponentShowcase.vue") },
      { path: "transaction-history", name: "TransactionHistory", component: () => import("@/views/transactions/TransactionHistory.vue") },
    ],
  },

  { path: "/:pathMatch(.*)*", redirect: "/idle" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (!authStore.isAuthenticated) authStore.restore();

  if (to.meta.guestAllowed) {
    next();
  } else if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
  } else if (
    (to.path === "/login" || to.path === "/login-rfid") &&
    authStore.isAuthenticated
  ) {
    next("/home");
  } else {
    next();
  }
});

export default router;