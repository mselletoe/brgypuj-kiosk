/**
 * @file router/index.js
 * @description Centralized routing configuration with Navigation Guards.
 */

import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import UserLayout from "@/layouts/UserLayout.vue";

// Views
import Display from "@/views/idle/Display.vue";
import Idle from "@/views/idle/Idle.vue";
import Announcements from "@/views/idle/Announcements.vue";
import Login from "@/views/auth/Login.vue";
import ScanRFID from "@/views/auth/ScanRFID.vue";
import AuthPIN from "@/views/auth/AuthPIN.vue";
import Register from "@/views/auth/Register.vue";
import KioskHome from "@/views/home/KioskHome.vue";
import DocumentServices from "@/views/document-services/DocumentServices.vue";
import DocumentFormWrapper from "@/views/document-services/DocumentFormWrapper.vue";
import EquipmentBorrowing from "@/views/equipment-borrowing/EquipmentBorrowing.vue";
import HelpAndSupport from "@/views/help-and-support/HelpAndSupport.vue";
import Feedback from "@/views/feedback/Feedback.vue";
import Rating from "@/views/feedback/Rating.vue";
import Comments from "@/views/feedback/Comments.vue";
import ComponentShowcase from "../components/ComponentShowcase.vue";
import InAnnouncements from "../views/announcements/Announcement.vue";
import TransactionHistory from "../views/transactions/TransactionHistory.vue";

// ID Services Views
import IDServices from "../views/id-services/IDServices.vue";
import RequestReplacement from "../views/id-services/RequestReplacement.vue";
import ChangePasscode from "../views/id-services/ChangePasscode.vue";
import ReportLost from "../views/id-services/ReportLost.vue";
import ApplyID from "../views/id-services/ApplyID.vue"; // <--- NEW IMPORT

const routes = [
  // Root Redirect: Kiosk starts at the Idle/Welcome screen
  { path: "/", redirect: "/idle" },

  /**
   * PUBLIC ROUTES
   */
  { path: "/display", name: "Display", component: Display },
  { path: "/idle", name: "Idle", component: Idle },
  { path: "/announcements", name: "Announcements", component: Announcements },
  { path: "/login", name: "LoginSelection", component: Login },
  { path: "/login-rfid", name: "ScanRFID", component: ScanRFID },
  { path: "/auth-pin", name: "VerifyPIN", component: AuthPIN },
  {
    path: "/inannouncements",
    name: "InAnnouncements",
    component: InAnnouncements,
  },

  /**
   * PROTECTED ROUTES (UserLayout)
   */
  {
    path: "/",
    component: UserLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "home", name: "Home", component: KioskHome },

      // Document Services
      {
        path: "document-services",
        name: "DocumentServices",
        component: DocumentServices,
        children: [{ path: ":docType", component: DocumentFormWrapper }],
      },

      // ID Services
      { path: "id-services", name: "IDServices", component: IDServices },
      {
        path: "id-services/replacement",
        name: "RequestReplacement",
        component: RequestReplacement,
      },
      {
        path: "id-services/change-pin",
        name: "ChangePasscode",
        component: ChangePasscode,
      },
      {
        path: "id-services/report-lost",
        name: "ReportLost",
        component: ReportLost,
      },
      {
        path: "id-services/apply", // <--- NEW ROUTE
        name: "ApplyID",
        component: ApplyID,
      },

      // Other Services
      {
        path: "equipment-borrowing",
        name: "EquipmentBorrowing",
        component: EquipmentBorrowing,
      },
      { path: "help-and-support", name: "Support", component: HelpAndSupport },
      { path: "feedback", name: "Feedback", component: Feedback },
      { path: "rating", name: "Rating", component: Rating },
      { path: "comments", name: "Comments", component: Comments },
      { path: "register", name: "Register", component: Register },
      {
        path: "component-showcase",
        name: "DevShowcase",
        component: ComponentShowcase,
      },
      {
        path: "transaction-history",
        name: "TransactionHistory",
        component: TransactionHistory,
      },
    ],
  },

  // Catch-all
  { path: "/:pathMatch(.*)*", redirect: "/idle" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard with DEV BYPASS
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) authStore.restore();

  // 🚧 DEV BYPASS
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log("⚠️ DEV MODE: Bypassing RFID Check");
    authStore.setRFID(
      { id: "2023-0042", first_name: "Keanno", last_name: "Macatangay" },
      "FAKE-RFID-TAG-888",
    );
    next();
    return;
  }
  // 🚧 END BYPASS

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
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
