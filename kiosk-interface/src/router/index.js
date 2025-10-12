import { createRouter, createWebHistory } from 'vue-router'

// Layouts
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
  {
    path: '/',
    redirect: '/idle',
  },
  {
    path: '/idle',
    component: Idle,
    children: [
      { path: 'announcements', component: Announcements },
      {
        path: 'login',
        component: Login,
        children: [
          // Guest kiosk home (for guest users)
          {
            path: 'guest-kiosk-home',
            component: UserLayout,
            children: [
              { path: '', component: KioskHome, meta: { header: 'Guest' } },
            ],
          },
          {
            path: 'rfid',
            component: UseRFID,
            children: [
              {
                path: 'processing',
                component: ProcessingScreen,
                children: [
                  {
                    path: 'keypad',
                    component: Keypad,
                    children: [
                      {
                        path: 'kiosk-home',
                        component: UserLayout,
                        children: [
                          { path: '', component: KioskHome },

                          // Document Services
                          {
                            path: 'document-services',
                            component: DocumentServices,
                            children: [
                              { path: 'barangay-clearance', component: BarangayClearance },
                              { path: 'barangay-clearance-good-moral', component: BarangayClearanceGoodMoral },
                              { path: 'business-permit', component: BusinessPermit },
                              { path: 'barangay-id', component: BarangayID },
                              { path: 'pwd-id', component: PWDID },
                              { path: 'senior-citizen-id', component: SeniorCitizenID },
                              { path: 'solo-parent-id', component: SoloParentID },
                              { path: 'indigency', component: CertificateOfIndigency },
                              { path: 'residency', component: CertificateOfResidency },
                            ],
                          },

                          // Equipment Borrowing
                          {
                            path: 'equipment-borrowing',
                            component: EquipmentBorrowing,
                            children: [
                              { path: 'select', component: EquipmentSelect },
                              { path: 'select-dates', component: EquipmentSelectDates },
                              { path: 'form', component: EquipmentForm },
                              { path: 'review', component: EquipmentReviewRequest },
                              { path: 'submitted', component: EquipmentRequestSubmitted },
                            ],
                          },

                          // Help and Support
                          {
                            path: 'help-and-support',
                            component: HelpAndSupport,
                            children: [
                              { path: 'faqs', component: FAQs },
                              { path: 'contact', component: Contact },
                            ],
                          },

                          // Feedback
                          {
                            path: 'feedback',
                            component: Feedback,
                            children: [
                              { path: 'service-quality', component: ServiceQualityFeedback },
                              { path: 'interface-design', component: InterfaceDesignFeedback },
                              { path: 'system-speed', component: SystemSpeedFeedback },
                              { path: 'accessibility', component: AccessibilityFeedback },
                              { path: 'general-experience', component: GeneralExperienceFeedback },
                            ],
                          },

                          // Appointments
                          {
                            path: 'appointments',
                            component: Appointments,
                            children: [
                              { path: 'schedule', component: ScheduleAppointment },
                              { path: 'submitted', component: AppointmentSubmitted },
                            ],
                          },
                        ],
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
