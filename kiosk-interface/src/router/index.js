import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'

// Top-level pages
import KioskHome from '@/views/home/KioskHome.vue'
import Login from '@/views/login/Login.vue'
import Announcements from '@/views/announcements/Announcements.vue'

// Login subpages
import LoginRFID from '@/views/login/LoginRFID.vue'
import LoginKeypad from '@/views/login/LoginKeypad.vue'

// Document Services
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import BarangayClearance from '@/views/document-services/BarangayClearance.vue'
import BarangayClearanceGoodMoral from '@/views/document-services/BarangayClearanceGoodMoral.vue'
import BusinessPermit from '@/views/document-services/BusinessPermit.vue'
import BarangayID from '@/views/document-services/BarangayID.vue'
import PWDID from '@/views/document-services/PWDID.vue'
import SeniorCitizenID from '@/views/document-services/SeniorCitizenID.vue'
import SoloParentID from '@/views/document-services/SoloParentID.vue'
import CertificateOfIndigency from '@/views/document-services/CertificateOfIndigency.vue'
import CertificateOfResidency from '@/views/document-services/CertificateOfResidency.vue'

// Equipment Borrowing
import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'
import EquipmentSelect from '@/views/equipment-borrowing/EquipmentSelect.vue'
import EquipmentSelectDates from '@/views/equipment-borrowing/EquipmentSelectDates.vue'
import EquipmentForm from '@/views/equipment-borrowing/EquipmentForm.vue'
import EquipmentReviewRequest from '@/views/equipment-borrowing/EquipmentReviewRequest.vue'
import EquipmentRequestSubmitted from '@/views/equipment-borrowing/EquipmentRequestSubmitted.vue'

// Help & Support
import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'
import FAQs from '@/views/help-and-support/FAQs.vue'
import Contact from '@/views/help-and-support/Contact.vue'

// Feedback
import Feedback from '@/views/feedback/Feedback.vue'
import ServiceQualityFeedback from '@/views/feedback/ServiceQualityFeedback.vue'
import InterfaceDesignFeedback from '@/views/feedback/InterfaceDesignFeedback.vue'
import SystemSpeedFeedback from '@/views/feedback/SystemSpeedFeedback.vue'
import AccessibilityFeedback from '@/views/feedback/AccessibilityFeedback.vue'
import GeneralExperienceFeedback from '@/views/feedback/GeneralExperienceFeedback.vue'

// Appointments
import Appointments from '@/views/appointments/Appointments.vue'
import ScheduleAppointment from '@/views/appointments/ScheduleAppointment.vue'
import AppointmentSubmitted from '@/views/appointments/AppointmentSubmitted.vue'

const routes = [
  {
    path: '/',
    component: UserLayout,
    redirect: '/kiosk-home',
    children: [
      { path: 'kiosk-home', component: KioskHome },
      { path: 'announcements', component: Announcements },

      // Document Services
      { path: 'document-services', component: DocumentServices },
      { path: 'document-services/barangay-clearance', component: BarangayClearance },
      { path: 'document-services/barangay-clearance-good-moral', component: BarangayClearanceGoodMoral },
      { path: 'document-services/business-permit', component: BusinessPermit },
      { path: 'document-services/barangay-id', component: BarangayID },
      { path: 'document-services/pwd-id', component: PWDID },
      { path: 'document-services/senior-citizen-id', component: SeniorCitizenID },
      { path: 'document-services/solo-parent-id', component: SoloParentID },
      { path: 'document-services/indigency', component: CertificateOfIndigency },
      { path: 'document-services/residency', component: CertificateOfResidency },

      // Equipment Borrowing
      { path: 'equipment-borrowing', component: EquipmentBorrowing },
      { path: 'equipment-borrowing/select', component: EquipmentSelect },
      { path: 'equipment-borrowing/select-dates', component: EquipmentSelectDates },
      { path: 'equipment-borrowing/form', component: EquipmentForm },
      { path: 'equipment-borrowing/review', component: EquipmentReviewRequest },
      { path: 'equipment-borrowing/submitted', component: EquipmentRequestSubmitted },

      // Help & Support
      { path: 'help-and-support', component: HelpAndSupport },
      { path: 'help-and-support/faqs', component: FAQs },
      { path: 'help-and-support/contact', component: Contact },

      // Feedback
      { path: 'feedback', component: Feedback },
      { path: 'feedback/service-quality', component: ServiceQualityFeedback },
      { path: 'feedback/interface-design', component: InterfaceDesignFeedback },
      { path: 'feedback/system-speed', component: SystemSpeedFeedback },
      { path: 'feedback/accessibility', component: AccessibilityFeedback },
      { path: 'feedback/general-experience', component: GeneralExperienceFeedback },

      // Appointments
      { path: 'appointments', component: Appointments },
      { path: 'appointments/schedule', component: ScheduleAppointment },
      { path: 'appointments/submitted', component: AppointmentSubmitted }
    ]
  },

  // Login routes (no layout)
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/login-rfid',
    name: 'LoginRFID',
    component: LoginRFID
  },
  {
    path: '/login-keypad',
    name: 'LoginKeypad',
    component: LoginKeypad
  },
  // Default redirect to the login page
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
