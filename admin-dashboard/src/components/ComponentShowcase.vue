<script setup>
import { ref } from 'vue'
import ConfirmationModal from '@/components/shared/ConfirmationModal.vue'
import PageTitle from '@/components/shared/PageTitle.vue'
import SendSMSModal from '@/components/shared/SendSMSModal.vue'
import RequestCard from '@/views/requests/document-requests/DocumentRequestCard.vue'
import BorrowingRequestCard from '@/views/requests/equipment-requests/EquipmentRequestCard.vue'
import NotesInput from './shared/NotesInput.vue'
import FeedbackCard from '@/views/feedback-and-reports/FeedbackReportCard.vue'

const noteInputRef = ref(null)

const handleNoteSubmit = (val) => {
  console.log('Note received in showcase:', val)
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Page Title -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-[#013C6D] mb-4">Component Documentation</h1>
        <p class="text-lg text-[#1B5886]">Visual reference for all components</p>
      </div>

      <!-- Components Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Floating Note Popover</h2>
            <p class="text-sm text-gray-600">Triggered by external button, closes on outside click</p>
          </div>
          <div class="flex flex-col items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            
            <button 
              @click="noteInputRef?.toggle()"
              class="px-5 py-2.5 bg-[#013C6D] text-white rounded-xl hover:bg-[#1B5886] transition-colors shadow-md flex items-start gap-2"
            >
              Add Note
            </button>

            <NotesInput 
              ref="noteInputRef" 
              @submit="handleNoteSubmit" 
            />

            <p class="mt-4 text-xs text-gray-400 italic text-center">
              Click the button to open. Click anywhere outside the input box to dismiss it.
            </p>
          </div>
        </div>
        
        <!-- PageTitle -->
        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Page Title</h2>
            <p class="text-sm text-gray-600">Page title component</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <PageTitle title="Sample Page Title" />
          </div>
        </div>

        <!-- ConfirmationModal -->
        <!-- <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Confirmation Modal</h2>
            <p class="text-sm text-gray-600">Confirmation dialog with custom actions</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <ConfirmationModal 
              :show="true" 
              title="Are you sure you want to delete this?"
              confirmText="Delete"
              cancelText="Cancel"
            />
          </div>
        </div> -->

        <!-- SendSMSModal -->
        <!-- <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Send SMS Modal</h2>
            <p class="text-sm text-gray-600">SMS sending modal with recipient info</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <SendSMSModal 
              :show="true"
              recipientName="Juan Dela Cruz"
              recipientPhone="+639123456789"
              defaultMessage="Hello! Your request has been approved."
            />
          </div>
        </div> -->

        <!-- RequestCard (Document Type) - Uncomment when ready -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Request Card - Document</h2>
            <p class="text-sm text-gray-600">Document request card with actions</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <RequestCard
              id="DR-001"
              type="document"
              status="pending"
              requestType="Certificate of Grades"
              :requester="{ firstName: 'Juan', middleName: 'D.', surname: 'Cruz' }"
              rfidNo="RFID-12345"
              requestedOn="01/05/26"
              amount="150"
              :isPaid="false"
              :isSelected="false"
            />
          </div>
        </div>

        <!-- RequestCard (RFID Type) - Uncomment when ready -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Request Card - RFID</h2>
            <p class="text-sm text-gray-600">RFID request card with actions</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <RequestCard
              id="DR-001"
              type="rfid"
              status="approved"
              requestType="RFID Replacement"
              :requester="{ firstName: 'Maria', middleName: 'S.', surname: 'Santos' }"
              rfidNo="Guest Mode"
              requestedOn="01/03/26"
              :isPaid="true"
              :isSelected="false"
            />
          </div>
        </div>

        <!-- BorrowingRequestCard - Uncomment when ready -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Borrowing Request Card</h2>
            <p class="text-sm text-gray-600">Borrowing request with period tracking</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <BorrowingRequestCard
              id="EB-001"
              status="pickedup"
              requestType="Equipment Borrowing"
              :requester="{ firstName: 'Anna', middleName: 'M.', surname: 'Garcia' }"
              rfidNo="RFID-54321"
              requestedOn="01/09/26"
              :borrowingPeriod="{ from: '01/10/26', to: '01/15/26' }"
              amount="500"
              :isPaid="true"
              :isSelected="false"
            />
          </div>
        </div>

        <!-- Feedback Card -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Feedback Card</h2>
            <p class="text-sm text-gray-600">User feedback with rating and comments</p>
          </div>

          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <FeedbackCard
              id="FB-001"
              type="feedback"
              title="Library Service Feedback"
              :requester="{ firstName: 'Juan', middleName: 'D.', surname: 'Cruz' }"
              rfidNo="RFID-98765"
              createdOn="01/12/26"
              :rating="4"
              ratingLabel="Good"
              comment="Staff were helpful and the process was quick."
              :isSelected="false"
            />
          </div>
        </div>

        <!-- Report Card -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Report Card</h2>
            <p class="text-sm text-gray-600">Incident or loss report</p>
          </div>

          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <FeedbackCard
              id="RP-014"
              type="report"
              title="Lost RFID Card"
              :requester="{ firstName: 'Maria', middleName: 'S.', surname: 'Santos' }"
              rfidNo="RFID-11223"
              createdOn="01/11/26"
              comment="RFID card was lost near the main gate."
              :isResolved="false"
            />
          </div>
        </div>

      </div>

      <!-- Instructions -->
      <div class="mt-12 bg-white rounded-2xl shadow-lg p-8 border-2 border-[#1B5886]">
        <h2 class="text-3xl font-bold text-[#013C6D] mb-4">How to Add More Components</h2>
        <ol class="space-y-3 text-gray-700 list-decimal list-inside">
          <li>Import your component at the top: <code class="bg-gray-100 px-2 py-1 rounded">import YourComponent from '@/components/YourComponent.vue'</code></li>
          <li>Copy one of the card divs and paste it in the grid</li>
          <li>Update the title, description, and replace the component tag</li>
          <li>Add <code class="bg-gray-100 px-2 py-1 rounded">lg:col-span-2</code> class if you want it full-width</li>
          <li>Uncomment the request card sections above to see them</li>
        </ol>
      </div>
    </div>
  </div>
</template>