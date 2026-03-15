<script setup>
import { ref } from "vue";
import {
  ServerIcon,
  UserGroupIcon,
  DocumentTextIcon,
  WrenchScrewdriverIcon,
  BellAlertIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChevronDownIcon,
  LightBulbIcon,
} from "@heroicons/vue/24/outline";

const openGuideItems = ref(new Set());
const toggleGuideItem = (id) => {
  if (openGuideItems.value.has(id)) openGuideItems.value.delete(id);
  else openGuideItems.value.add(id);
};

const guideModules = [
  {
    id: "dashboard",
    icon: ServerIcon,
    color: "blue",
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
    color: "emerald",
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
    color: "violet",
    title: "Document Services Configuration",
    summary: "Create and configure document types with custom form fields and templates.",
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
    color: "amber",
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
    color: "rose",
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
    color: "cyan",
    title: "Announcements & SMS",
    summary: "Broadcast announcements and send targeted SMS messages to residents.",
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
    color: "orange",
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
    color: "blue",
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
    color: "emerald",
    title: "Notification Logs",
    summary: "View the complete history of all SMS notifications sent by the system.",
    content: `The Notifications log keeps a full history of all SMS messages sent to residents.

You can:
• View message content, recipient, and timestamp
• Check delivery status (sent / failed)
• Retry failed messages
• Filter by date range, recipient, or message type

Triggered SMS events include: request status updates, appointment reminders, disaster/emergency alerts, and custom admin broadcasts.`,
  },
];

const tips = [
  { title: 'Backup Regularly',       text: 'Export resident data and transaction logs weekly. The system has no automatic cloud backup.' },
  { title: 'Test SMS Before Events', text: 'Send a test SMS before mass announcements. Verify the SIM card has sufficient balance.' },
  { title: 'Keep Templates Updated', text: 'Re-upload document templates whenever official formats change. Old templates stay linked until replaced.' },
  { title: 'RFID Registration First',text: 'Always register the RFID UID in the resident profile before issuing a card. Unregistered cards are rejected.' },
  { title: 'Monitor Audit Logs',     text: 'Review the audit logs on the Overview page daily to catch unauthorized actions or issues early.' },
  { title: 'Placeholder Spelling',   text: 'Field names in document templates must exactly match valid placeholders — they are case-sensitive.' },
];
</script>

<template>
  <div class="guide-root">

    <!-- ── Hero Banner ─────────────────────────────────────────── -->
    <div class="guide-hero section-row" style="animation-delay:0s">
      <div class="guide-hero-rings" aria-hidden="true">
        <span class="gring gring-1"></span>
        <span class="gring gring-2"></span>
        <span class="gring gring-3"></span>
        <span class="glow-orb"></span>
      </div>
      <div class="guide-hero-grid" aria-hidden="true"></div>
      <div class="guide-hero-content">
        <div class="guide-hero-badges">
          <span class="gbadge">
            <span class="gbadge-dot"></span>
            Admin Reference
          </span>
          <span class="gbadge gbadge-outline">Dashboard Only</span>
          <span class="gbadge gbadge-outline">{{ guideModules.length }} Modules</span>
        </div>
        <h1 class="guide-hero-title">
          Admin User<br />
          <span class="guide-hero-accent">Guide</span>
        </h1>
        <p class="guide-hero-sub">Complete reference for operating the Barangay Kiosk Admin Dashboard</p>
      </div>
    </div>

    <!-- ── Warning Banner ─────────────────────────────────────── -->
    <div class="warn-banner section-row" style="animation-delay:0.07s">
      <div class="warn-icon-wrap">
        <ExclamationTriangleIcon class="warn-icon" />
      </div>
      <div>
        <p class="warn-title">Admin Dashboard Documentation Only</p>
        <p class="warn-body">
          This guide covers this admin dashboard only. For hardware setup, kiosk physical
          installation, and network configuration, refer to the separate
          <strong>Hardware &amp; Deployment Manual</strong> provided with the project deliverables.
        </p>
      </div>
    </div>

    <!-- ── Stats strip ────────────────────────────────────────── -->
    <div class="guide-stats section-row" style="animation-delay:0.12s">
      <div v-for="s in [
        { value: guideModules.length,  label: 'Guide Modules'   },
        { value: tips.length,          label: 'Quick Tips'      },
        { value: '2',                  label: 'SMS Channels'    },
        { value: '100%',               label: 'Offline Capable' },
      ]" :key="s.label" class="gstat-item">
        <div class="gstat-value">{{ s.value }}</div>
        <div class="gstat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- ── Module Accordion ───────────────────────────────────── -->
    <div class="modules-list section-row" style="animation-delay:0.17s">
      <div class="modules-header">
        <h2 class="modules-title">Module Reference</h2>
        <p class="modules-sub">Click any module to expand its documentation</p>
      </div>

      <div
        v-for="(mod, i) in guideModules"
        :key="mod.id"
        class="mod-card"
        :class="{ 'mod-card--open': openGuideItems.has(mod.id) }"
        :style="`animation-delay:${0.2 + i * 0.04}s`"
      >
        <!-- Accordion trigger -->
        <button
          @click="toggleGuideItem(mod.id)"
          class="mod-trigger"
          :aria-expanded="openGuideItems.has(mod.id)"
        >
          <div class="mod-left">
            <div class="mod-icon-wrap" :class="'mod-icon--' + mod.color">
              <component :is="mod.icon" class="mod-icon" />
            </div>
            <div class="mod-meta">
              <div class="mod-index">{{ String(i + 1).padStart(2, '0') }}</div>
              <div class="mod-title">{{ mod.title }}</div>
              <div class="mod-summary">{{ mod.summary }}</div>
            </div>
          </div>
          <div class="mod-chevron" :class="{ 'mod-chevron--open': openGuideItems.has(mod.id) }">
            <ChevronDownIcon class="w-4 h-4" />
          </div>
        </button>

        <!-- Accordion body -->
        <Transition name="accordion">
          <div v-if="openGuideItems.has(mod.id)" class="mod-body">
            <div class="mod-divider"></div>
            <div class="mod-content">{{ mod.content }}</div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- ── Quick Tips ─────────────────────────────────────────── -->
    <div class="tips-card section-row" style="animation-delay:0.6s">
      <!-- Tips header -->
      <div class="tips-header">
        <div class="card-icon-wrap icon-amber">
          <LightBulbIcon class="card-icon" />
        </div>
        <div>
          <h3 class="tips-title">Quick Tips &amp; Best Practices</h3>
          <p class="tips-sub">Keep these in mind for smooth daily operations</p>
        </div>
      </div>

      <div class="tips-grid">
        <div
          v-for="(tip, i) in tips"
          :key="tip.title"
          class="tip-item"
          :style="`animation-delay:${0.62 + i * 0.05}s`"
        >
          <div class="tip-num">{{ String(i + 1).padStart(2, '0') }}</div>
          <div class="tip-title">{{ tip.title }}</div>
          <div class="tip-text">{{ tip.text }}</div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ─── Root ───────────────────────────────────────────────────── */
.guide-root {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding-bottom: 2rem;
}

/* ─── Section animation ───────────────────────────────────────── */
.section-row {
  opacity: 0;
  animation: riseUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes riseUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0);    }
}

/* ─── Hero Banner ─────────────────────────────────────────────── */
.guide-hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #1d4ed8 75%, #2563eb 100%);
  border-radius: 20px;
  padding: 48px 52px 44px;
  color: #fff;
  isolation: isolate;
  width: 100%;
  box-sizing: border-box;
}
@media (max-width: 768px) {
  .guide-hero { padding: 32px 24px 28px; }
}

.guide-hero-rings {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.gring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.1);
  right: -80px; top: -80px;
  animation: ringPulse 7s ease-in-out infinite;
}
.gring-1 { width: 240px; height: 240px; animation-delay: 0s;   }
.gring-2 { width: 420px; height: 420px; animation-delay: 1s;   }
.gring-3 { width: 600px; height: 600px; animation-delay: 2s;   }
@keyframes ringPulse {
  0%,100% { opacity: 0.1; }
  50%      { opacity: 0.25; }
}
.glow-orb {
  position: absolute;
  right: -20px; top: -20px;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(96,165,250,0.2) 0%, transparent 70%);
  border-radius: 50%;
}
.guide-hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.guide-hero-content { position: relative; z-index: 2; }

.guide-hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 22px;
}
.gbadge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(255,255,255,0.14);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 5px 14px;
  border-radius: 100px;
}
.gbadge-outline {
  background: transparent;
  border-color: rgba(255,255,255,0.28);
}
.gbadge-dot {
  width: 7px; height: 7px;
  background: #4ade80;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(74,222,128,0.3);
  animation: blip 1.8s ease-in-out infinite;
}
@keyframes blip {
  0%,100% { box-shadow: 0 0 0 3px rgba(74,222,128,0.3); }
  50%      { box-shadow: 0 0 0 6px rgba(74,222,128,0.1); }
}

.guide-hero-title {
  font-size: clamp(1.8rem, 3.5vw, 2.9rem);
  font-weight: 900;
  line-height: 1.12;
  letter-spacing: -0.02em;
  margin: 0 0 10px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.25);
}
.guide-hero-accent {
  background: linear-gradient(90deg, #93c5fd, #e0f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.guide-hero-sub {
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255,255,255,0.65);
  margin: 0;
  max-width: 560px;
  line-height: 1.6;
}

/* ─── Warning Banner ──────────────────────────────────────────── */
.warn-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border: 1px solid #fde68a;
  border-radius: 16px;
  padding: 18px 22px;
  width: 100%;
  box-sizing: border-box;
}
.warn-icon-wrap {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: #fef3c7;
  border: 1px solid #fde68a;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.warn-icon { width: 18px; height: 18px; color: #d97706; }
.warn-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #92400e;
  margin-bottom: 4px;
}
.warn-body {
  font-size: 0.83rem;
  color: #78350f;
  line-height: 1.6;
  margin: 0;
}

/* ─── Stats strip ─────────────────────────────────────────────── */
.guide-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #e2e8f0;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}
@media (max-width: 640px) {
  .guide-stats { grid-template-columns: repeat(2, 1fr); }
}
.gstat-item {
  background: #fff;
  padding: 20px;
  text-align: center;
  transition: background 0.2s;
}
.gstat-item:hover { background: #f8fafc; }
.gstat-value {
  font-size: 1.9rem;
  font-weight: 900;
  color: #1e40af;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-bottom: 5px;
}
.gstat-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ─── Module list wrapper ─────────────────────────────────────── */
.modules-list {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  width: 100%;
  box-sizing: border-box;
}
.modules-header {
  padding: 24px 28px 20px;
  border-bottom: 1px solid #f1f5f9;
  background: linear-gradient(to right, #f8fafc, #fff);
}
.modules-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}
.modules-sub {
  font-size: 0.82rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 500;
}

/* ─── Module accordion card ───────────────────────────────────── */
.mod-card {
  border-bottom: 1px solid #f1f5f9;
  opacity: 0;
  animation: riseUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards;
  transition: background 0.2s;
}
.mod-card:last-child { border-bottom: none; }
.mod-card--open { background: #fafbff; }

.mod-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  gap: 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.18s;
}
.mod-trigger:hover { background: #f8fafc; }

.mod-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

/* Icon */
.mod-icon-wrap {
  width: 40px; height: 40px;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.mod-trigger:hover .mod-icon-wrap { transform: scale(1.08); }
.mod-icon { width: 20px; height: 20px; }

.mod-icon--blue    { background:#eff6ff; border:1px solid #bfdbfe; }
.mod-icon--blue    .mod-icon { color:#2563eb; }
.mod-icon--emerald { background:#ecfdf5; border:1px solid #a7f3d0; }
.mod-icon--emerald .mod-icon { color:#059669; }
.mod-icon--violet  { background:#f5f3ff; border:1px solid #ddd6fe; }
.mod-icon--violet  .mod-icon { color:#7c3aed; }
.mod-icon--amber   { background:#fffbeb; border:1px solid #fde68a; }
.mod-icon--amber   .mod-icon { color:#d97706; }
.mod-icon--rose    { background:#fff1f2; border:1px solid #fecdd3; }
.mod-icon--rose    .mod-icon { color:#e11d48; }
.mod-icon--cyan    { background:#ecfeff; border:1px solid #a5f3fc; }
.mod-icon--cyan    .mod-icon { color:#0891b2; }
.mod-icon--orange  { background:#fff7ed; border:1px solid #fed7aa; }
.mod-icon--orange  .mod-icon { color:#ea580c; }

/* Meta */
.mod-meta { flex: 1; min-width: 0; }
.mod-index {
  font-size: 10px;
  font-weight: 800;
  color: #94a3b8;
  letter-spacing: 0.1em;
  margin-bottom: 2px;
}
.mod-title {
  font-size: 0.92rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mod-summary {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Chevron */
.mod-chevron {
  width: 28px; height: 28px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: #94a3b8;
  transition: transform 0.25s cubic-bezier(0.16,1,0.3,1), background 0.2s, border-color 0.2s, color 0.2s;
}
.mod-chevron--open {
  transform: rotate(180deg);
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #2563eb;
}

/* Accordion body */
.mod-body { overflow: hidden; }
.mod-divider {
  height: 1px;
  background: linear-gradient(to right, #e2e8f0, transparent);
  margin: 0 24px;
}
.mod-content {
  padding: 18px 24px 22px 78px;
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.75;
  white-space: pre-line;
}
@media (max-width: 640px) {
  .mod-content { padding-left: 24px; }
}

/* Accordion transition */
.accordion-enter-active,
.accordion-leave-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.16,1,0.3,1);
}
.accordion-enter-from,
.accordion-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ─── Tips card ───────────────────────────────────────────────── */
.tips-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 28px 32px 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s;
  width: 100%;
  box-sizing: border-box;
}
.tips-card:hover { box-shadow: 0 8px 32px rgba(0,0,0,0.07); }

.tips-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.card-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.icon-amber  { background: #fffbeb; border: 1px solid #fde68a; }
.card-icon   { width: 22px; height: 22px; color: #d97706; }
.tips-title {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}
.tips-sub {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 500;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 1024px) {
  .tips-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .tips-grid { grid-template-columns: 1fr; }
}

.tip-item {
  position: relative;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px 18px 16px;
  opacity: 0;
  animation: riseUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  overflow: hidden;
}
.tip-item::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 12px 12px 0 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.tip-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(37,99,235,0.1);
  border-color: #bfdbfe;
}
.tip-item:hover::before { opacity: 1; }

.tip-num {
  font-size: 10px;
  font-weight: 900;
  color: #94a3b8;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}
.tip-title {
  font-size: 0.85rem;
  font-weight: 800;
  color: #1e40af;
  margin-bottom: 6px;
}
.tip-text {
  font-size: 0.79rem;
  color: #475569;
  line-height: 1.6;
}
</style>