<script setup>
/**
 * @file HelpPage.vue
 * @description Admin Help & Documentation Center
 */
import { ref } from "vue";
import PageTitle from "@/components/shared/PageTitle.vue";
import {
  InformationCircleIcon,
  BookOpenIcon,
  CodeBracketIcon,
  ShieldCheckIcon,
  ChevronDownIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  ServerIcon,
  DocumentTextIcon,
  UserGroupIcon,
  BellAlertIcon,
  WrenchScrewdriverIcon,
  IdentificationIcon,
  ClockIcon,
  LockClosedIcon,
} from "@heroicons/vue/24/outline";
import { useSearchSync } from "@/composables/useSearchSync";

// ======================================
// Active Section State
// ======================================
const activeSection = ref("about");

const sections = [
  { id: "about", label: "About the Project", icon: InformationCircleIcon },
  { id: "guide", label: "Admin User Guide", icon: BookOpenIcon },
  { id: "placeholders", label: "Document Placeholders", icon: CodeBracketIcon },
  { id: "privacy", label: "Privacy & Terms", icon: ShieldCheckIcon },
];

// ======================================
// Placeholder Reference Data
// (sourced from DocumentForm.vue fieldMapping)
// ======================================
const placeholderGroups = [
  {
    group: "Name Fields",
    icon: IdentificationIcon,
    color: "blue",
    placeholders: [
      {
        key: "full_name",
        aliases: ["full_name", "name", "resident_name", "applicant_name"],
        description: "Full legal name of the resident",
      },
      {
        key: "first_name",
        aliases: ["first_name", "fname"],
        description: "First (given) name",
      },
      {
        key: "middle_name",
        aliases: ["middle_name", "mname"],
        description: "Middle name",
      },
      {
        key: "last_name",
        aliases: ["last_name", "lname", "surname"],
        description: "Last name / Surname",
      },
      {
        key: "suffix",
        aliases: ["suffix", "name_suffix"],
        description: "Name suffix (e.g., Jr., Sr., III)",
      },
    ],
  },
  {
    group: "Personal Information",
    icon: UserGroupIcon,
    color: "violet",
    placeholders: [
      {
        key: "gender",
        aliases: ["gender", "sex"],
        description: "Gender or biological sex",
      },
      {
        key: "birthdate",
        aliases: ["birthdate", "date_of_birth", "birth_date", "dob"],
        description: "Date of birth",
      },
      {
        key: "age",
        aliases: ["age"],
        description: "Current age of the resident",
      },
    ],
  },
  {
    group: "Contact Information",
    icon: BellAlertIcon,
    color: "green",
    placeholders: [
      {
        key: "email",
        aliases: ["email", "email_address"],
        description: "Email address",
      },
      {
        key: "phone_number",
        aliases: [
          "phone_number",
          "contact_number",
          "mobile_number",
          "phone",
          "contact",
        ],
        description: "Mobile / contact number",
      },
    ],
  },
  {
    group: "Address Fields",
    icon: ServerIcon,
    color: "orange",
    placeholders: [
      {
        key: "unit_blk_street",
        aliases: ["unit_blk_street", "street", "house_number", "house_no"],
        description: "Unit, block, or street address",
      },
      {
        key: "purok_name",
        aliases: ["purok_name", "purok", "sitio"],
        description: "Purok or sitio name",
      },
      {
        key: "barangay",
        aliases: ["barangay", "brgy"],
        description: "Barangay name",
      },
      {
        key: "municipality",
        aliases: ["municipality", "city"],
        description: "Municipality or city",
      },
      {
        key: "province",
        aliases: ["province", "prov"],
        description: "Province",
      },
      { key: "region", aliases: ["region"], description: "Region" },
      {
        key: "full_address",
        aliases: ["full_address", "address", "complete_address"],
        description: "Complete combined address string",
      },
    ],
  },
  {
    group: "Residency Information",
    icon: ClockIcon,
    color: "teal",
    placeholders: [
      {
        key: "years_residency",
        aliases: [
          "yr_res",
          "years_residency",
          "years_of_residency",
          "residency_years",
          "year_residency",
        ],
        description: "Number of years residing in the barangay",
      },
      {
        key: "residency_start_date",
        aliases: ["residency_start_date", "date_started_residency"],
        description: "Date when residency started",
      },
    ],
  },
  {
    group: "RFID & System Fields",
    icon: LockClosedIcon,
    color: "red",
    placeholders: [
      {
        key: "rfid_uid",
        aliases: ["rfid_uid", "rfid", "card_number", "rfid_number"],
        description: "Resident RFID card unique identifier",
      },
    ],
  },
];

// ======================================
// Expandable Guide Modules
// ======================================
const openGuideItems = ref(new Set());
const toggleGuideItem = (id) => {
  if (openGuideItems.value.has(id)) openGuideItems.value.delete(id);
  else openGuideItems.value.add(id);
};

const guideModules = [
  {
    id: "dashboard",
    icon: ServerIcon,
    title: "Dashboard Overview",
    summary: "Monitor all barangay transactions at a glance.",
    content: `The Dashboard is your central command center. It shows real-time statistics including:

• Total registered residents
• Pending document requests
• Pending equipment borrowing requests
• Active blotter cases
• Recent audit logs showing all system actions

The charts display transaction volume over time and breakdowns by type. Use this page to assess daily workload and spot bottlenecks quickly.`,
  },
  {
    id: "residents",
    icon: UserGroupIcon,
    title: "Residents Management",
    summary: "Add, edit, and manage the barangay resident database.",
    content: `The Residents module is the foundation of the entire system. Every kiosk transaction relies on accurate resident records.

Key functions:
• Add new residents manually or via bulk import
• Edit resident profiles (personal info, address, contact details)
• Assign and link RFID card UIDs to resident records
• Capture ID photos that appear on printed documents
• Search and filter residents by name, purok, or RFID

⚠️ Important: RFID UIDs must be registered here before a resident can use the kiosk. When a resident taps their card, the system looks up their profile by UID to auto-fill request forms.`,
  },
  {
    id: "document-services",
    icon: DocumentTextIcon,
    title: "Document Services Configuration",
    summary:
      "Create and configure document types with custom form fields and templates.",
    content: `This is one of the most critical admin functions. You define what document types residents can request at the kiosk.

For each document type you can configure:
• Name, description, and service fee
• Availability toggle (enable / disable from kiosk)
• Custom form fields — see the Document Placeholders tab for valid field names
• Document requirements checklist
• A .docx template file for auto-generation

Template Upload:
Create your Word document and insert placeholders using double curly braces, e.g. {{full_name}}, {{barangay}}. When a resident submits a request, the system replaces those placeholders with their actual profile data automatically.

Field types available: text, email, tel, number, date, textarea, select`,
  },
  {
    id: "document-requests",
    icon: DocumentTextIcon,
    title: "Document Requests",
    summary: "Process, approve, and track resident document requests.",
    content: `View all incoming document requests submitted via the kiosk or admin portal.

Workflow:
1. Request arrives with status: Pending
2. Admin reviews the form data and attached requirements
3. Admin updates status to: Processing → Ready for Pickup → Completed
4. The system automatically sends an SMS to the resident at each status change

Actions available:
• View full request details and submitted form data
• Download or print the auto-generated document
• Update request status and add internal notes
• Reject requests with a reason (resident is notified via SMS)

Tip: Use the filter and search to quickly find requests by document type, status, or resident name.`,
  },
  {
    id: "equipment",
    icon: WrenchScrewdriverIcon,
    title: "Equipment & Inventory",
    summary: "Manage borrowable barangay equipment and track requests.",
    content: `The Equipment module handles barangay-owned items available for resident borrowing (e.g., tents, monobloc chairs, sound systems).

Equipment Management:
• Add items with quantity, description, and borrowing conditions
• Set items as available or unavailable
• Track current stock vs. reserved quantities

Equipment Requests:
• Residents submit borrowing requests via kiosk specifying the dates needed
• Admin approves or rejects based on availability
• The system checks for date conflicts automatically
• Approved reservations reduce available stock for that period`,
  },
  {
    id: "announcements",
    icon: BellAlertIcon,
    title: "Announcements & SMS",
    summary:
      "Broadcast announcements and send targeted SMS messages to residents.",
    content: `Two announcement channels are available:

Kiosk Announcements:
• Displayed on the kiosk idle/home screen
• Useful for notices, advisories, and office hour changes
• Can include images and priority flags

SMS Announcements:
• Sends text messages to all or selected residents
• Uses the GSM module connected to the Raspberry Pi
• Supports targeted sending by purok, age group, or individual
• All sent SMS messages are logged for accountability

⚠️ Note: SMS is sent sequentially through a single GSM module. Large blasts to hundreds of residents may take time. Schedule mass announcements during off-peak hours.`,
  },
  {
    id: "blotter",
    icon: ExclamationTriangleIcon,
    title: "Blotter & KP Logs",
    summary: "Record and manage barangay incident and peace-and-order reports.",
    content: `The Blotter module logs barangay incidents and Katarungang Pambarangay (KP) cases.

Features:
• Log new incidents with complainant, respondent, and narrative details
• Track case status: Active → Under Mediation → Resolved / Closed
• Attach supporting documents or photos
• KP case scheduling and hearing logs
• Export blotter reports for LGU submission

Access Control: Only authorized barangay officials should have full edit access to blotter records.`,
  },
  {
    id: "faqs",
    icon: InformationCircleIcon,
    title: "FAQ Management",
    summary: "Manage the FAQ content displayed on the kiosk help screen.",
    content: `Residents at the kiosk can access a help/FAQ screen. You manage its content here.

• Add, edit, or remove FAQ items
• Organize by category
• Enable or disable individual entries
• Changes reflect on the kiosk in real-time (no reboot needed)

Use this to answer common resident questions like required documents, office hours, or processing times.`,
  },
  {
    id: "notifications",
    icon: BellAlertIcon,
    title: "Notification Logs",
    summary:
      "View the complete history of all SMS notifications sent by the system.",
    content: `The Notifications log keeps a full history of all SMS messages sent to residents.

You can:
• View message content, recipient, and timestamp
• Check delivery status (sent / failed)
• Retry failed messages
• Filter by date range, recipient, or message type

Triggered SMS events include: request status updates, appointment reminders, disaster/emergency alerts, and custom admin broadcasts.`,
  },
];

// ======================================
// Copy to Clipboard
// ======================================
const copiedKey = ref(null);
const copyToClipboard = (text) => {
  navigator.clipboard.writeText(`{{${text}}}`);
  copiedKey.value = text;
  setTimeout(() => {
    copiedKey.value = null;
  }, 2000);
};

// ======================================
// Color variant maps
// ======================================
const colorMap = {
  blue: {
    header: "bg-blue-50 border-b border-blue-100",
    icon: "text-blue-600",
    primary: "bg-blue-100 text-blue-700 border border-blue-200",
    alias: "bg-blue-50 text-blue-600 border border-blue-100",
  },
  violet: {
    header: "bg-violet-50 border-b border-violet-100",
    icon: "text-violet-600",
    primary: "bg-violet-100 text-violet-700 border border-violet-200",
    alias: "bg-violet-50 text-violet-600 border border-violet-100",
  },
  green: {
    header: "bg-green-50 border-b border-green-100",
    icon: "text-green-600",
    primary: "bg-green-100 text-green-700 border border-green-200",
    alias: "bg-green-50 text-green-600 border border-green-100",
  },
  orange: {
    header: "bg-orange-50 border-b border-orange-100",
    icon: "text-orange-600",
    primary: "bg-orange-100 text-orange-700 border border-orange-200",
    alias: "bg-orange-50 text-orange-600 border border-orange-100",
  },
  teal: {
    header: "bg-teal-50 border-b border-teal-100",
    icon: "text-teal-600",
    primary: "bg-teal-100 text-teal-700 border border-teal-200",
    alias: "bg-teal-50 text-teal-600 border border-teal-100",
  },
  red: {
    header: "bg-red-50 border-b border-red-100",
    icon: "text-red-600",
    primary: "bg-red-100 text-red-700 border border-red-200",
    alias: "bg-red-50 text-red-600 border border-red-100",
  },
};
</script>

<template>
  <div
    class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden"
  >
    <!-- Page Header -->
    <div class="flex-shrink-0 mb-5">
      <PageTitle title="Admin Help & Support" />
      <p class="text-sm text-gray-500 mt-1">
        System reference guide for the Barangay Kiosk Admin Dashboard.
      </p>
    </div>

    <!-- Tab Navigation -->
    <div class="flex-shrink-0 flex gap-1 border-b border-gray-200 mb-5">
      <button
        v-for="section in sections"
        :key="section.id"
        @click="activeSection = section.id"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors',
          activeSection === section.id
            ? 'border-blue-600 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
        ]"
      >
        <component :is="section.icon" class="w-4 h-4" />
        {{ section.label }}
      </button>
    </div>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto">
      <div
        class="max-w-4xl mx-auto space-y-4 animate-fade-in"
        :key="activeSection"
      >
        <!-- ==================
             ABOUT
        =================== -->
        <template v-if="activeSection === 'about'">
          <!-- Hero banner -->
          <div
            class="relative bg-blue-600 rounded-xl p-6 text-white overflow-hidden"
          >
            <div class="absolute inset-0 opacity-10 pointer-events-none">
              <svg
                viewBox="0 0 400 200"
                class="w-full h-full"
                preserveAspectRatio="xMaxYMid slice"
              >
                <circle
                  cx="380"
                  cy="10"
                  r="130"
                  stroke="white"
                  stroke-width="1.5"
                  fill="none"
                />
                <circle
                  cx="380"
                  cy="10"
                  r="85"
                  stroke="white"
                  stroke-width="1.5"
                  fill="none"
                />
                <circle cx="380" cy="10" r="40" fill="white" />
              </svg>
            </div>
            <div class="relative">
              <div class="flex flex-wrap gap-2 mb-3">
                <span
                  class="bg-white/20 text-white text-xs font-bold px-2.5 py-1 rounded-full"
                  >PUP Thesis Project</span
                >
                <span
                  class="bg-white/20 text-white text-xs font-bold px-2.5 py-1 rounded-full"
                  >November 2025</span
                >
              </div>
              <h2 class="text-xl font-bold leading-snug mb-2">
                RFID-Enabled Barangay Transaction Kiosk<br />with SMS
                Notification System
              </h2>
              <p class="text-blue-100 text-sm leading-relaxed max-w-xl">
                A self-service platform for Poblacion I, Amadeo, Cavite —
                designed to modernize barangay transactions through RFID
                authentication, automated form handling, and GSM-based SMS
                notifications.
              </p>
              <div class="mt-4 flex flex-wrap gap-2">
                <span
                  v-for="tag in [
                    'Vue.js',
                    'Node.js',
                    'Raspberry Pi 5',
                    'RFID Reader',
                    'GSM Module',
                    'Offline-First',
                    'Local LAN',
                  ]"
                  :key="tag"
                  class="bg-white/15 border border-white/25 text-white text-xs px-2.5 py-0.5 rounded-md font-medium"
                  >{{ tag }}</span
                >
              </div>
            </div>
          </div>

          <!-- Two-col info cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3
                class="font-bold text-gray-800 text-sm mb-3 flex items-center gap-2"
              >
                <InformationCircleIcon class="w-4 h-4 text-blue-600" /> Project
                Background
              </h3>
              <p class="text-sm text-gray-600 leading-relaxed">
                Barangay service delivery has long relied on manual processes —
                paper forms, manual encoding, and verbal announcements. This
                system addresses those inefficiencies with a centralized,
                offline-capable digital platform covering document requests,
                equipment borrowing, resident management, and community
                communication.
              </p>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3
                class="font-bold text-gray-800 text-sm mb-3 flex items-center gap-2"
              >
                <LightBulbIcon class="w-4 h-4 text-blue-600" /> Key Features
              </h3>
              <ul class="text-sm text-gray-600 space-y-1.5">
                <li
                  v-for="f in [
                    'RFID-based resident authentication with auto-fill forms',
                    'Document requests with .docx template auto-generation',
                    'Equipment borrowing with availability tracking',
                    'GSM-based SMS notifications — no internet required',
                    'Bilingual kiosk UI (English / Filipino)',
                    'Staff admin dashboard with full audit logs',
                    'Fully offline — no cloud dependency',
                  ]"
                  :key="f"
                  class="flex items-start gap-2"
                >
                  <span class="text-blue-600 font-bold mt-0.5 leading-none"
                    >•</span
                  >{{ f }}
                </li>
              </ul>
            </div>
          </div>

          <!-- System components -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3
              class="font-bold text-gray-800 text-sm mb-4 flex items-center gap-2"
            >
              <ServerIcon class="w-4 h-4 text-blue-600" /> System Components
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div
                v-for="c in [
                  { name: 'Kiosk Unit', sub: 'Raspberry Pi 5 + Touchscreen' },
                  { name: 'RFID Reader', sub: '13.56MHz / 125KHz Contactless' },
                  { name: 'GSM Module', sub: 'SIM800L — SMS dispatch' },
                  {
                    name: 'Admin Dashboard',
                    sub: 'This interface · LAN-connected',
                  },
                ]"
                :key="c.name"
                class="rounded-lg border border-blue-100 bg-blue-50 p-3 text-center"
              >
                <div class="font-bold text-xs text-blue-700 mb-1">
                  {{ c.name }}
                </div>
                <div class="text-xs text-blue-500">{{ c.sub }}</div>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-3 leading-relaxed">
              The kiosk communicates with this dashboard over a local wireless
              LAN. No internet connection is required for any core operation.
              The GSM module handles outbound SMS independently through the
              cellular network.
            </p>
          </div>

          <!-- Research team -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3
              class="font-bold text-gray-800 text-sm mb-3 flex items-center gap-2"
            >
              <UserGroupIcon class="w-4 h-4 text-blue-600" /> Research Team
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div
                v-for="name in [
                  'Alleah Marie G. Bayas',
                  'Justine Mae L. Convicto',
                  'Eloissa S. Francisco',
                  'Keanno Brennel A. Macatangay',
                ]"
                :key="name"
                class="text-center bg-gray-50 rounded-lg p-3 border border-gray-100"
              >
                <div
                  class="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold mx-auto mb-2"
                >
                  {{ name.charAt(0) }}{{ name.split(" ").at(-1).charAt(0) }}
                </div>
                <div class="text-xs font-semibold text-gray-700 leading-tight">
                  {{ name }}
                </div>
              </div>
            </div>
            <p class="text-xs text-gray-400 text-center mt-3">
              BS Computer Engineering · Polytechnic University of the
              Philippines · 2025
            </p>
          </div>
        </template>

        <!-- ==================
             ADMIN GUIDE
        =================== -->
        <template v-if="activeSection === 'guide'">
          <div
            class="flex gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4"
          >
            <ExclamationTriangleIcon
              class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5"
            />
            <div>
              <p class="text-sm font-semibold text-amber-800">
                Admin Dashboard Documentation Only
              </p>
              <p class="text-xs text-amber-700 mt-0.5 leading-relaxed">
                This guide covers this admin dashboard only. For hardware setup,
                kiosk physical installation, and network configuration, refer to
                the separate
                <strong>Hardware & Deployment Manual</strong> provided with the
                project deliverables.
              </p>
            </div>
          </div>

          <div
            v-for="mod in guideModules"
            :key="mod.id"
            class="bg-white rounded-xl border border-gray-200 overflow-hidden"
          >
            <button
              @click="toggleGuideItem(mod.id)"
              class="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left gap-4"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0"
                >
                  <component :is="mod.icon" class="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <div class="font-semibold text-sm text-gray-800">
                    {{ mod.title }}
                  </div>
                  <div class="text-xs text-gray-400 mt-0.5">
                    {{ mod.summary }}
                  </div>
                </div>
              </div>
              <ChevronDownIcon
                class="w-4 h-4 text-gray-400 flex-shrink-0 transition-transform duration-200"
                :class="openGuideItems.has(mod.id) ? 'rotate-180' : ''"
              />
            </button>
            <div v-if="openGuideItems.has(mod.id)" class="px-5 pb-5">
              <div
                class="border-t border-gray-100 pt-4 text-sm text-gray-600 leading-relaxed whitespace-pre-line"
              >
                {{ mod.content }}
              </div>
            </div>
          </div>

          <!-- Quick tips -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3
              class="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2"
            >
              <LightBulbIcon class="w-4 h-4 text-blue-600" /> Quick Tips & Best
              Practices
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="tip in [
                  {
                    title: 'Backup Regularly',
                    text: 'Export resident data and transaction logs weekly. The system has no automatic cloud backup.',
                  },
                  {
                    title: 'Test SMS Before Events',
                    text: 'Send a test SMS before mass announcements. Verify the SIM card has sufficient balance.',
                  },
                  {
                    title: 'Keep Templates Updated',
                    text: 'Re-upload document templates whenever official formats change. Old templates stay linked until replaced.',
                  },
                  {
                    title: 'RFID Registration First',
                    text: 'Always register the RFID UID in the resident profile before issuing a card. Unregistered cards are rejected.',
                  },
                  {
                    title: 'Monitor Audit Logs',
                    text: 'Review the audit logs on the Overview page daily to catch unauthorized actions or issues early.',
                  },
                  {
                    title: 'Placeholder Spelling',
                    text: 'Field names in document templates must exactly match valid placeholders — they are case-sensitive.',
                  },
                ]"
                :key="tip.title"
                class="bg-gray-50 rounded-lg p-3 border border-gray-100"
              >
                <div class="font-semibold text-xs text-blue-600 mb-1">
                  {{ tip.title }}
                </div>
                <div class="text-xs text-gray-500 leading-relaxed">
                  {{ tip.text }}
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ==================
             PLACEHOLDERS
        =================== -->
        <template v-if="activeSection === 'placeholders'">
          <div class="bg-blue-600 rounded-xl p-5 text-white">
            <div class="flex items-start gap-3">
              <CodeBracketIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div>
                <h3 class="font-bold text-sm mb-1">
                  Document Template Placeholder Reference
                </h3>
                <p class="text-blue-100 text-xs leading-relaxed">
                  When uploading a <strong>.docx document template</strong>,
                  insert placeholders using double curly braces — e.g.
                  <code class="bg-white/20 px-1.5 py-0.5 rounded font-mono"
                    >&#123;&#123;full_name&#125;&#125;</code
                  >. The system replaces them with the resident's actual profile
                  data when a request is submitted.
                </p>
                <p class="text-blue-200 text-xs mt-2">
                  Any <strong>alias</strong> listed for a field works
                  identically. Click any tag below to copy it as a
                  ready-to-paste placeholder.
                </p>
              </div>
            </div>
          </div>

          <!-- How-to steps -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              v-for="(step, i) in [
                {
                  title: 'Create a .docx Template',
                  text: 'Open Microsoft Word and design your document (e.g., Barangay Clearance) as normal.',
                },
                {
                  title: 'Insert Placeholders',
                  text: 'Where resident data should appear, type the placeholder in double curly braces: e.g. {{full_name}}.',
                },
                {
                  title: 'Upload in Document Services',
                  text: 'Go to Document Services, open the document type, and upload the .docx file.',
                },
              ]"
              :key="step.title"
              class="bg-white rounded-xl border border-gray-200 p-4"
            >
              <div
                class="font-semibold text-xs text-gray-700 mb-1.5 flex items-center gap-2"
              >
                <span
                  class="w-5 h-5 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center font-bold flex-shrink-0"
                  >{{ i + 1 }}</span
                >
                {{ step.title }}
              </div>
              <p class="text-xs text-gray-500 leading-relaxed">
                {{ step.text }}
              </p>
            </div>
          </div>

          <!-- Placeholder groups -->
          <div
            v-for="group in placeholderGroups"
            :key="group.group"
            class="bg-white rounded-xl border border-gray-200 overflow-hidden"
          >
            <div
              class="px-5 py-3 flex items-center gap-2"
              :class="colorMap[group.color].header"
            >
              <component
                :is="group.icon"
                class="w-4 h-4"
                :class="colorMap[group.color].icon"
              />
              <span class="font-semibold text-sm text-gray-800">{{
                group.group
              }}</span>
              <span class="ml-auto text-xs text-gray-400"
                >{{ group.placeholders.length }} field{{
                  group.placeholders.length !== 1 ? "s" : ""
                }}</span
              >
            </div>

            <div class="divide-y divide-gray-50">
              <div
                v-for="ph in group.placeholders"
                :key="ph.key"
                class="px-5 py-3 hover:bg-gray-50/60 transition-colors"
              >
                <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
                  <!-- Primary key — click to copy -->
                  <button
                    @click="copyToClipboard(ph.key)"
                    :class="[
                      'flex items-center gap-1 font-mono text-xs px-2 py-1 rounded-md font-semibold transition-all',
                      copiedKey === ph.key
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : colorMap[group.color].primary +
                          ' hover:opacity-80 cursor-pointer',
                    ]"
                    title="Click to copy as {{placeholder}}"
                  >
                    <CheckIcon v-if="copiedKey === ph.key" class="w-3 h-3" />
                    <ClipboardDocumentIcon v-else class="w-3 h-3" />
                    &#123;&#123;{{ ph.key }}&#125;&#125;
                  </button>

                  <!-- Alias tags -->
                  <button
                    v-for="alias in ph.aliases.slice(1)"
                    :key="alias"
                    @click="copyToClipboard(alias)"
                    :class="[
                      'font-mono text-xs px-2 py-0.5 rounded-md transition-all',
                      copiedKey === alias
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-500 border border-gray-200 hover:bg-gray-200 cursor-pointer',
                    ]"
                    title="Click to copy as {{placeholder}}"
                  >
                    {{ alias }}
                  </button>
                </div>
                <p class="text-xs text-gray-500 leading-relaxed">
                  {{ ph.description }}
                </p>
              </div>
            </div>
          </div>

          <!-- Warning notes -->
          <div
            class="flex gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4"
          >
            <ExclamationTriangleIcon
              class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5"
            />
            <div>
              <p class="text-sm font-semibold text-amber-800 mb-1.5">
                Important Notes
              </p>
              <ul class="text-xs text-amber-700 space-y-1.5 leading-relaxed">
                <li>
                  • <strong>Exact spelling required.</strong> Placeholders are
                  case-sensitive.
                  <code class="bg-amber-100 px-1 rounded font-mono"
                    >Full_Name</code
                  >
                  will NOT work — use
                  <code class="bg-amber-100 px-1 rounded font-mono"
                    >full_name</code
                  >.
                </li>
                <li>
                  • <strong>Click any tag to copy it</strong> as a
                  ready-to-paste
                  <code class="bg-amber-100 px-1 rounded font-mono"
                    >&#123;&#123;placeholder&#125;&#125;</code
                  >
                  string.
                </li>
                <li>
                  • <strong>Aliases are interchangeable.</strong>
                  <code class="bg-amber-100 px-1 rounded font-mono"
                    >&#123;&#123;name&#125;&#125;</code
                  >
                  and
                  <code class="bg-amber-100 px-1 rounded font-mono"
                    >&#123;&#123;full_name&#125;&#125;</code
                  >
                  both produce the resident's full name.
                </li>
                <li>
                  •
                  <strong
                    >Auto-fill only applies to RFID-authenticated
                    sessions.</strong
                  >
                  Walk-in residents fill forms manually.
                </li>
                <li>
                  • <strong>Missing profile data leaves a blank</strong> in the
                  output document — no error is thrown.
                </li>
              </ul>
            </div>
          </div>
        </template>

        <!-- ==================
             PRIVACY & TERMS
        =================== -->
        <template v-if="activeSection === 'privacy'">
          <!-- Privacy Policy -->
          <div
            class="bg-white rounded-xl border border-gray-200 overflow-hidden"
          >
            <div class="bg-blue-600 px-5 py-4">
              <h3 class="font-bold text-white text-sm flex items-center gap-2">
                <ShieldCheckIcon class="w-4 h-4" /> Privacy Policy
              </h3>
              <p class="text-blue-100 text-xs mt-0.5">
                Effective as of Deployment Date · Poblacion I, Amadeo, Cavite
              </p>
            </div>
            <div class="p-5 space-y-4 text-sm text-gray-600 leading-relaxed">
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  1. Data Controller
                </h4>
                <p>
                  The Barangay of Poblacion I, Amadeo, Cavite ("the Barangay")
                  is the data controller for all personal information collected
                  through the Barangay Transaction Kiosk and Admin Dashboard
                  System. Staff designated by the Barangay Captain are
                  authorized data processors.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  2. Information We Collect
                </h4>
                <p class="mb-2">
                  The system collects the following from residents:
                </p>
                <ul class="space-y-1 ml-4 text-xs">
                  <li>
                    • <strong>Identity:</strong> Full name, date of birth,
                    gender, suffix
                  </li>
                  <li>
                    • <strong>Contact:</strong> Mobile phone number, email
                    address
                  </li>
                  <li>
                    • <strong>Address:</strong> Complete residential address,
                    purok/sitio
                  </li>
                  <li>
                    • <strong>Residency:</strong> Years of residency, residency
                    start date
                  </li>
                  <li>
                    • <strong>Photo:</strong> ID photo captured at the kiosk
                    camera
                  </li>
                  <li>
                    • <strong>System:</strong> RFID card UID, transaction
                    history, submitted requests
                  </li>
                </ul>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  3. Legal Basis & Purpose
                </h4>
                <p>
                  Data is collected under RA 7160 (Local Government Code) for:
                  processing official barangay documents, verifying resident
                  identity, sending SMS transaction notifications, maintaining
                  resident records, and DILG reporting compliance.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  4. Data Storage & Security
                </h4>
                <p>
                  All data is stored locally on the Raspberry Pi server within
                  the barangay hall.
                  <strong
                    >No resident data is transmitted to any third-party cloud
                    service.</strong
                  >
                  Security measures include RFID access control, PIN-based admin
                  authentication, LAN isolation, and full audit logging.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  5. Data Sharing
                </h4>
                <p>
                  Resident data shall not be sold or disclosed to third parties
                  except when legally required by a competent authority, when
                  shared within the LGU of Amadeo for official purposes, or in
                  anonymized form for government statistical reporting.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  6. Resident Rights (RA 10173)
                </h4>
                <p>
                  Residents may exercise their rights to:
                  <strong>access</strong> their data,
                  <strong>correct</strong> inaccurate information,
                  <strong>request erasure</strong> subject to legal retention,
                  and <strong>object</strong> to processing under certain
                  conditions. Submit requests in writing to the Barangay
                  Secretary.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">7. SMS Consent</h4>
                <p class="text-xs">
                  By registering a mobile number, residents consent to receive
                  official SMS notifications. Residents may opt out via written
                  request to the Barangay Secretary.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  8. Data Retention
                </h4>
                <p class="text-xs">
                  Data is retained per applicable Philippine law and LGU
                  record-keeping policies. Transaction logs are kept for a
                  minimum of five (5) years.
                </p>
              </section>
            </div>
          </div>

          <!-- Terms & Conditions -->
          <div
            class="bg-white rounded-xl border border-gray-200 overflow-hidden"
          >
            <div class="bg-gray-700 px-5 py-4">
              <h3 class="font-bold text-white text-sm flex items-center gap-2">
                <DocumentTextIcon class="w-4 h-4" /> Terms & Conditions of Use
              </h3>
              <p class="text-gray-300 text-xs mt-0.5">
                For Barangay Admin Staff Users
              </p>
            </div>
            <div class="p-5 space-y-4 text-sm text-gray-600 leading-relaxed">
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  1. Authorized Users
                </h4>
                <p class="text-xs">
                  Access is restricted to staff designated by the Barangay
                  Captain. Unauthorized use may violate RA 10175 (Cybercrime
                  Prevention Act of 2012).
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  2. Credential Responsibility
                </h4>
                <p class="text-xs">
                  Admin accounts are personal and non-transferable. You are
                  responsible for all actions performed under your credentials.
                  Do not share passwords. Report suspected unauthorized access
                  immediately.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  3. Acceptable Use
                </h4>
                <p class="mb-1.5 text-xs">
                  The system must only be used for legitimate barangay service
                  delivery. Prohibited activities include:
                </p>
                <ul class="space-y-1 ml-4 text-xs">
                  <li>
                    • Accessing or modifying resident data without official need
                  </li>
                  <li>
                    • Creating false or fraudulent records or transaction
                    entries
                  </li>
                  <li>
                    • Using the SMS system for personal or non-official messages
                  </li>
                  <li>
                    • Attempting to bypass security controls or access other LAN
                    devices
                  </li>
                  <li>
                    • Exporting or copying resident data for personal or
                    unauthorized use
                  </li>
                </ul>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  4. Audit & Monitoring
                </h4>
                <p class="text-xs">
                  All actions in this dashboard are logged in the audit trail,
                  including data modifications, document approvals, and logins.
                  Logs are accessible to the Barangay Captain for compliance and
                  accountability review.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  5. System Availability
                </h4>
                <p class="text-xs">
                  The system operates on local infrastructure and does not
                  guarantee 100% uptime. Power outages, hardware failures, or
                  planned maintenance may cause temporary unavailability.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">
                  6. Disclaimer of Warranty
                </h4>
                <p class="text-xs">
                  This system is deployed as a thesis prototype. It is provided
                  "as-is" without warranty of any kind. The development team
                  shall not be liable for consequential damages arising from
                  system use, data loss, or inaccuracies in generated documents.
                </p>
              </section>
              <section>
                <h4 class="font-semibold text-gray-800 mb-1">7. Amendments</h4>
                <p class="text-xs">
                  These terms may be updated by barangay administration as the
                  system evolves. Continued use constitutes acceptance of any
                  revised terms.
                </p>
              </section>
              <div class="pt-4 border-t border-gray-100">
                <p class="text-xs text-gray-400 text-center leading-relaxed">
                  Developed in partial fulfillment of the requirements for the
                  degree of Bachelor of Science in Computer Engineering<br />
                  Polytechnic University of the Philippines · 2025
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
</style>
