import { createRouter, createWebHistory } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'

// Idle Screens
import Idle from '@/views/idle/Idle.vue'
import Announcements from '@/views/announcements/Announcements.vue'
import Login from '@/views/login/Login.vue'

// Login Subpages
import UseRFID from '@/views/login/UseRFID.vue'
import ProcessingScreen from '@/views/login/ProcessingScreen.vue'
import Keypad from '@/views/login/Keypad.vue'

// Kiosk Home & Main Sections
import KioskHome from '@/views/home/KioskHome.vue'
import DocumentServices from '@/views/document-services/DocumentServices.vue'
import EquipmentBorrowing from '@/views/equipment-borrowing/EquipmentBorrowing.vue'
import HelpAndSupport from '@/views/help-and-support/HelpAndSupport.vue'
import Feedback from '@/views/feedback/Feedback.vue'
import Appointments from '@/views/appointments/Appointments.vue'

// Document Services Subpages
import BarangayClearance from '@/views/document-services/BarangayClearance.vue'
import BarangayClearanceGoodMoral from '@/views/document-services/BarangayClearanceGoodMoral.vue'
import BusinessPermit from '@/views/document-services/BusinessPermit.vue'
import BarangayID from '@/views/document-services/BarangayID.vue'
import PWDID from '@/views/document-services/PWDID.vue'
import SeniorCitizenID from '@/views/document-services/SeniorCitizenID.vue'
import SoloParentID from '@/views/document-services/SoloParentID.vue'
import CertificateOfIndigency from '@/views/document-services/CertificateOfIndigency.vue'
import CertificateOfResidency from '@/views/document-services/CertificateOfResidency.vue'

// Equipment Borrowing Subpages
import EquipmentSelect from '@/views/equipment-borrowing/EquipmentSelect.vue'
import EquipmentSelectDates from '@/views/equipment-borrowing/EquipmentSelectDates.vue'
import EquipmentForm from '@/views/equipment-borrowing/EquipmentForm.vue'
import EquipmentReviewRequest from '@/views/equipment-borrowing/EquipmentReviewRequest.vue'
import EquipmentRequestSubmitted from '@/views/equipment-borrowing/EquipmentRequestSubmitted.vue'

// Help and Support Subpages
import FAQs from '@/views/help-and-support/FAQs.vue'
import Contact from '@/views/help-and-support/Contact.vue'

// Feedback Subpages
import ServiceQualityFeedback from '@/views/feedback/ServiceQualityFeedback.vue'
import InterfaceDesignFeedback from '@/views/feedback/InterfaceDesignFeedback.vue'
import SystemSpeedFeedback from '@/views/feedback/SystemSpeedFeedback.vue'
import AccessibilityFeedback from '@/views/feedback/AccessibilityFeedback.vue'
import GeneralExperienceFeedback from '@/views/feedback/GeneralExperienceFeedback.vue'

// Appointments Subpages
import ScheduleAppointment from '@/views/appointments/ScheduleAppointment.vue'
import AppointmentSubmitted from '@/views/appointments/AppointmentSubmitted.vue'

const routes = [
  // Idle
  { path: '/', redirect: '/idle' },
  { path: '/idle', component: Idle },
  { path: '/idle/announcements', component: Announcements },

  // Login + Subpages
  { path: '/idle/login', component: Login },
  { path: '/idle/login/guest-kiosk-home', component: KioskHome, meta: { layout: UserLayout, header: 'Guest' } },
  { path: '/idle/login/rfid', component: UseRFID },
  { path: '/idle/login/rfid/processing', component: ProcessingScreen },
  { path: '/idle/login/rfid/processing/keypad', component: Keypad },

  // Kiosk Home (after login)
  {
    path: '/idle/login/rfid/processing/keypad/kiosk-home',
    component: UserLayout,
    children: [
      { path: '', component: KioskHome },

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

      // Help and Support
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
      { path: 'appointments/submitted', component: AppointmentSubmitted },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
