<script setup>
import {
  ShieldCheckIcon,
  DocumentTextIcon,
  LockClosedIcon,
  UserCircleIcon,
  ServerIcon,
  ShareIcon,
  DevicePhoneMobileIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  UsersIcon,
  KeyIcon,
  EyeIcon,
  NoSymbolIcon,
  ClipboardDocumentListIcon,
  InformationCircleIcon,
  PencilSquareIcon,
} from "@heroicons/vue/24/outline";

const stats = [
  { value: "8",        label: "Privacy Clauses"  },
  { value: "7",        label: "Terms Clauses"    },
  { value: "RA 10173", label: "Data Privacy Act" },
  { value: "10 yrs",    label: "Data Retention"   },
];

const privacySections = [
  {
    icon: UsersIcon,
    color: "blue",
    title: "1. Data Controller",
    text: 'The Barangay of Poblacion I, Amadeo, Cavite ("the Barangay") is the data controller for all personal information collected through the Barangay Transaction Kiosk and Admin Dashboard System. Staff designated by the Barangay Captain are authorized data processors.',
  },
  {
    icon: EyeIcon,
    color: "violet",
    title: "2. Information We Collect",
    text: "The system collects the following from residents:",
    list: [
      { label: "Identity",  text: "Full name, date of birth, gender, suffix" },
      { label: "Contact",   text: "Mobile phone number, email address" },
      { label: "Address",   text: "Complete residential address, purok/sitio" },
      { label: "Residency", text: "Years of residency, residency start date" },
      { label: "Photo",     text: "ID photo captured at the kiosk camera" },
      { label: "System",    text: "RFID card UID, transaction history, submitted requests" },
    ],
  },
  {
    icon: ClipboardDocumentListIcon,
    color: "emerald",
    title: "3. Legal Basis & Purpose",
    text: "Data is collected under RA 7160 (Local Government Code) for: processing official barangay documents, verifying resident identity, sending SMS transaction notifications, maintaining resident records, and DILG reporting compliance.",
  },
  {
    icon: LockClosedIcon,
    color: "blue",
    title: "4. Data Storage & Security",
    text: "All data is stored locally on the Raspberry Pi server within the barangay hall. No resident data is transmitted to any third-party cloud service. Security measures include RFID access control, PIN-based admin authentication, LAN isolation, and full audit logging.",
    highlight: "No resident data is transmitted to any third-party cloud service.",
  },
  {
    icon: ShareIcon,
    color: "orange",
    title: "5. Data Sharing",
    text: "Resident data shall not be sold or disclosed to third parties except when legally required by a competent authority, when shared within the LGU of Amadeo for official purposes, or in anonymized form for government statistical reporting.",
  },
  {
    icon: UserCircleIcon,
    color: "violet",
    title: "6. Resident Rights (RA 10173)",
    text: null,
    rights: [
      "Access their data",
      "Correct inaccurate information",
      "Request erasure subject to legal retention",
      "Object to processing under certain conditions",
    ],
    footer: "Submit requests in writing to the Barangay Secretary.",
  },
  {
    icon: DevicePhoneMobileIcon,
    color: "teal",
    title: "7. SMS Consent",
    text: "By registering a mobile number, residents consent to receive official SMS notifications. Residents may opt out via written request to the Barangay Secretary.",
  },
  {
    icon: ClockIcon,
    color: "rose",
    title: "8. Data Retention",
    text: "Data is retained per applicable Philippine law and LGU record-keeping policies. Transaction logs are kept for a minimum of five (5) years.",
  },
];

const termsSections = [
  {
    icon: KeyIcon,
    color: "blue",
    title: "1. Authorized Users",
    text: "Access is restricted to staff designated by the Barangay Captain. Unauthorized use may violate RA 10175 (Cybercrime Prevention Act of 2012).",
  },
  {
    icon: LockClosedIcon,
    color: "violet",
    title: "2. Credential Responsibility",
    text: "Admin accounts are personal and non-transferable. You are responsible for all actions performed under your credentials. Do not share passwords. Report suspected unauthorized access immediately.",
  },
  {
    icon: NoSymbolIcon,
    color: "rose",
    title: "3. Acceptable Use",
    text: "The system must only be used for legitimate barangay service delivery. Prohibited activities include:",
    bullets: [
      "Accessing or modifying resident data without official need",
      "Creating false or fraudulent records or transaction entries",
      "Using the SMS system for personal or non-official messages",
      "Attempting to bypass security controls or access other LAN devices",
      "Exporting or copying resident data for personal or unauthorized use",
    ],
  },
  {
    icon: ClipboardDocumentListIcon,
    color: "orange",
    title: "4. Audit & Monitoring",
    text: "All actions in this dashboard are logged in the audit trail, including data modifications, document approvals, and logins. Logs are accessible to the Barangay Captain for compliance and accountability review.",
  },
  {
    icon: ServerIcon,
    color: "teal",
    title: "5. System Availability",
    text: "The system operates on local infrastructure and does not guarantee 100% uptime. Power outages, hardware failures, or planned maintenance may cause temporary unavailability.",
  },
  {
    icon: ExclamationTriangleIcon,
    color: "amber",
    title: "6. Disclaimer of Warranty",
    text: 'This system is deployed as a thesis prototype. It is provided without warranty of any kind. The development team shall not be liable for consequential damages arising from system use, data loss, or inaccuracies in generated documents.',
  },
  {
    icon: PencilSquareIcon,
    color: "emerald",
    title: "7. Amendments",
    text: "These terms may be updated by barangay administration as the system evolves. Continued use constitutes acceptance of any revised terms.",
  },
];
</script>

<template>
  <div class="pt-root">

    <!-- Hero -->
    <div class="pt-hero section-row" style="animation-delay:0s">
      <div class="pt-rings" aria-hidden="true">
        <span class="ptring ptring-1"></span>
        <span class="ptring ptring-2"></span>
        <span class="ptring ptring-3"></span>
        <span class="pt-orb"></span>
      </div>
      <div class="pt-grid" aria-hidden="true"></div>
      <div class="pt-hero-content">
        <div class="pt-badges">
          <span class="ptbadge">
            <span class="ptbadge-dot"></span>
            Legal Documents
          </span>
          <span class="ptbadge ptbadge-outline">RA 10173 Compliant</span>
        </div>
        <h1 class="pt-title">
          Privacy &amp; Terms<br />
          <span class="pt-accent">of Use</span>
        </h1>
        <p class="pt-sub">
          Governing policies for data collection, storage, and admin dashboard usage —
          effective as of system deployment date.
        </p>
      </div>
      <div class="pt-shield-wrap" aria-hidden="true">
        <div class="pt-shield">
          <ShieldCheckIcon class="pt-shield-icon" />
          <div class="pt-shield-label">Data Protected</div>
          <div class="pt-shield-sub">Locally stored · No cloud</div>
        </div>
        <div class="pt-shield-ring pt-shield-ring-1"></div>
        <div class="pt-shield-ring pt-shield-ring-2"></div>
      </div>
    </div>

    <!-- Stats -->
    <div class="pt-stats section-row" style="animation-delay:0.07s">
      <div v-for="s in stats" :key="s.label" class="ptstat-item">
        <div class="ptstat-value">{{ s.value }}</div>
        <div class="ptstat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- Privacy Policy -->
    <div class="policy-card section-row" style="animation-delay:0.13s">
      <div class="policy-header policy-header--blue">
        <div class="policy-header-rings" aria-hidden="true">
          <span class="ph-ring ph-ring-1"></span>
          <span class="ph-ring ph-ring-2"></span>
        </div>
        <div class="policy-header-content">
          <div class="policy-header-icon">
            <ShieldCheckIcon class="hdr-icon" />
          </div>
          <div>
            <h2 class="policy-header-title">Privacy Policy</h2>
            <p class="policy-header-sub">Effective as of Deployment Date · Poblacion I, Amadeo, Cavite</p>
          </div>
        </div>
      </div>
      <div class="policy-body">
        <div
          v-for="(sec, i) in privacySections"
          :key="sec.title"
          class="policy-section"
          :class="'policy-section--' + sec.color"
          :style="'animation-delay:' + (0.16 + i * 0.04) + 's'"
        >
          <div class="ps-icon-wrap" :class="'ps-icon--' + sec.color">
            <component :is="sec.icon" class="ps-icon" />
          </div>
          <div class="ps-body">
            <h3 class="ps-title">{{ sec.title }}</h3>
            <div v-if="sec.highlight" class="ps-highlight">
              <LockClosedIcon class="highlight-icon" />
              <span>{{ sec.highlight }}</span>
            </div>
            <p v-if="sec.text" class="ps-text">{{ sec.text }}</p>
            <div v-if="sec.list" class="ps-list">
              <div v-for="item in sec.list" :key="item.label" class="ps-list-item">
                <span class="ps-list-label">{{ item.label }}</span>
                <span class="ps-list-text">{{ item.text }}</span>
              </div>
            </div>
            <div v-if="sec.rights" class="ps-rights">
              <div v-for="r in sec.rights" :key="r" class="ps-right-item">
                <span class="ps-right-dot"></span>
                {{ r }}
              </div>
              <p class="ps-text ps-mt">{{ sec.footer }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Terms & Conditions -->
    <div class="policy-card section-row" style="animation-delay:0.55s">
      <div class="policy-header policy-header--dark">
        <div class="policy-header-rings" aria-hidden="true">
          <span class="ph-ring ph-ring-1"></span>
          <span class="ph-ring ph-ring-2"></span>
        </div>
        <div class="policy-header-content">
          <div class="policy-header-icon policy-header-icon--dark">
            <DocumentTextIcon class="hdr-icon" />
          </div>
          <div>
            <h2 class="policy-header-title">Terms &amp; Conditions of Use</h2>
            <p class="policy-header-sub">For Barangay Admin Staff Users</p>
          </div>
        </div>
      </div>
      <div class="policy-body">
        <div
          v-for="(sec, i) in termsSections"
          :key="sec.title"
          class="policy-section"
          :class="'policy-section--' + sec.color"
          :style="'animation-delay:' + (0.58 + i * 0.04) + 's'"
        >
          <div class="ps-icon-wrap" :class="'ps-icon--' + sec.color">
            <component :is="sec.icon" class="ps-icon" />
          </div>
          <div class="ps-body">
            <h3 class="ps-title">{{ sec.title }}</h3>
            <p v-if="sec.text" class="ps-text">{{ sec.text }}</p>
            <div v-if="sec.bullets" class="ps-bullets">
              <div v-for="b in sec.bullets" :key="b" class="ps-bullet-item">
                <span class="ps-plain-dot"></span>
                {{ b }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="policy-footer">
        <div class="policy-footer-inner">
          <InformationCircleIcon class="footer-info-icon" />
          <p>
            Developed in partial fulfillment of the requirements for the degree of
            Bachelor of Science in Computer Engineering ·
            Polytechnic University of the Philippines · 2025
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.pt-root {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding-bottom: 2rem;
}
.section-row {
  opacity: 0;
  animation: riseUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes riseUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Hero */
.pt-hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 38%, #1d4ed8 72%, #2563eb 100%);
  border-radius: 20px;
  padding: 48px 52px 44px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  isolation: isolate;
  width: 100%;
  box-sizing: border-box;
}
@media (max-width: 860px) {
  .pt-hero { flex-direction: column; padding: 32px 24px 28px; }
  .pt-shield-wrap { display: none; }
}
.pt-rings { position: absolute; inset: 0; pointer-events: none; }
.ptring {
  position: absolute; border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.1);
  right: -80px; top: -80px;
  animation: ringPulse 7s ease-in-out infinite;
}
.ptring-1 { width: 260px; height: 260px; animation-delay: 0s; }
.ptring-2 { width: 460px; height: 460px; animation-delay: 1s; }
.ptring-3 { width: 660px; height: 660px; animation-delay: 2s; }
@keyframes ringPulse {
  0%, 100% { opacity: 0.1; } 50% { opacity: 0.22; }
}
.pt-orb {
  position: absolute; right: -20px; top: -20px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(96,165,250,0.18) 0%, transparent 70%);
  border-radius: 50%;
}
.pt-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}
.pt-hero-content { position: relative; z-index: 2; flex: 1; min-width: 0; }
.pt-badges { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; }
.ptbadge {
  display: inline-flex; align-items: center; gap: 7px;
  background: rgba(255,255,255,0.14); backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2); color: #fff;
  font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; padding: 5px 14px; border-radius: 100px;
}
.ptbadge-outline { background: transparent; border-color: rgba(255,255,255,0.28); }
.ptbadge-dot {
  width: 7px; height: 7px; background: #4ade80; border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(74,222,128,0.3);
  animation: blip 1.8s ease-in-out infinite;
}
@keyframes blip {
  0%, 100% { box-shadow: 0 0 0 3px rgba(74,222,128,0.3); }
  50%       { box-shadow: 0 0 0 6px rgba(74,222,128,0.1); }
}
.pt-title {
  font-size: clamp(1.8rem, 3.2vw, 2.8rem); font-weight: 900;
  line-height: 1.13; letter-spacing: -0.02em; margin: 0 0 12px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.25);
}
.pt-accent {
  background: linear-gradient(90deg, #93c5fd, #e0f2fe);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.pt-sub { font-size: 0.95rem; color: rgba(255,255,255,0.7); line-height: 1.65; max-width: 500px; margin: 0; }

/* Shield */
.pt-shield-wrap {
  position: relative; z-index: 2; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  width: 180px; height: 180px;
}
.pt-shield {
  position: relative; z-index: 3;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
  background: rgba(255,255,255,0.1); backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.2); border-radius: 50%;
  width: 130px; height: 130px; box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.pt-shield-icon  { width: 40px; height: 40px; color: #fff; }
.pt-shield-label { font-size: 11px; font-weight: 800; color: #fff; letter-spacing: 0.04em; text-align: center; }
.pt-shield-sub   { font-size: 9px; font-weight: 600; color: rgba(255,255,255,0.6); text-align: center; }
.pt-shield-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.15);
  animation: shieldPulse 3s ease-in-out infinite;
}
.pt-shield-ring-1 { width: 155px; height: 155px; animation-delay: 0s; }
.pt-shield-ring-2 { width: 180px; height: 180px; animation-delay: 1s; }
@keyframes shieldPulse {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50%       { opacity: 0.35; transform: scale(1.03); }
}

/* Stats */
.pt-stats {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1px; background: #e2e8f0; border: 1px solid #e2e8f0;
  border-radius: 16px; overflow: hidden; width: 100%; box-sizing: border-box;
}
@media (max-width: 640px) { .pt-stats { grid-template-columns: repeat(2, 1fr); } }
.ptstat-item { background: #fff; padding: 20px; text-align: center; transition: background 0.2s; }
.ptstat-item:hover { background: #f8fafc; }
.ptstat-value { font-size: 1.7rem; font-weight: 900; color: #1e40af; letter-spacing: -0.03em; line-height: 1; margin-bottom: 5px; }
.ptstat-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }

/* Policy card */
.policy-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 20px;
  overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s; width: 100%; box-sizing: border-box;
}
.policy-card:hover { box-shadow: 0 8px 32px rgba(0,0,0,0.07); }

/* Header */
.policy-header { position: relative; overflow: hidden; padding: 24px 32px; isolation: isolate; }
.policy-header--blue { background: linear-gradient(135deg, #1e40af, #2563eb, #3b82f6); }
.policy-header--dark { background: linear-gradient(135deg, #0f172a, #1e293b, #334155); }
.policy-header-rings { position: absolute; inset: 0; pointer-events: none; }
.ph-ring { position: absolute; border-radius: 50%; border: 1px solid rgba(255,255,255,0.1); right: -40px; top: -40px; }
.ph-ring-1 { width: 120px; height: 120px; }
.ph-ring-2 { width: 200px; height: 200px; }
.policy-header-content { position: relative; z-index: 2; display: flex; align-items: center; gap: 14px; }
.policy-header-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.policy-header-icon--dark { background: rgba(255,255,255,0.1); }
.hdr-icon { width: 24px; height: 24px; color: #fff; }
.policy-header-title { font-size: 1.05rem; font-weight: 800; color: #fff; margin: 0 0 3px; letter-spacing: -0.01em; }
.policy-header-sub   { font-size: 0.78rem; color: rgba(255,255,255,0.6); margin: 0; font-weight: 500; }

/* Sections */
.policy-body { padding: 8px 0; }
.policy-section {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 18px 28px; border-bottom: 1px solid #f8fafc;
  opacity: 0; animation: riseUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards;
  transition: background 0.18s;
}
.policy-section:last-child { border-bottom: none; }
.policy-section--blue:hover    { background: #f8fbff; }
.policy-section--violet:hover  { background: #faf8ff; }
.policy-section--emerald:hover { background: #f8fffe; }
.policy-section--orange:hover  { background: #fffaf8; }
.policy-section--teal:hover    { background: #f8fffd; }
.policy-section--rose:hover    { background: #fff8fa; }
.policy-section--amber:hover   { background: #fffdf8; }

.ps-icon-wrap {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}
.ps-icon { width: 18px; height: 18px; }
.ps-icon--blue    { background: #eff6ff; border: 1px solid #bfdbfe; } .ps-icon--blue    .ps-icon { color: #2563eb; }
.ps-icon--violet  { background: #f5f3ff; border: 1px solid #ddd6fe; } .ps-icon--violet  .ps-icon { color: #7c3aed; }
.ps-icon--emerald { background: #ecfdf5; border: 1px solid #a7f3d0; } .ps-icon--emerald .ps-icon { color: #059669; }
.ps-icon--orange  { background: #fff7ed; border: 1px solid #fed7aa; } .ps-icon--orange  .ps-icon { color: #ea580c; }
.ps-icon--teal    { background: #f0fdfa; border: 1px solid #99f6e4; } .ps-icon--teal    .ps-icon { color: #0d9488; }
.ps-icon--rose    { background: #fff1f2; border: 1px solid #fecdd3; } .ps-icon--rose    .ps-icon { color: #e11d48; }
.ps-icon--amber   { background: #fffbeb; border: 1px solid #fde68a; } .ps-icon--amber   .ps-icon { color: #d97706; }

.ps-body { flex: 1; min-width: 0; }
.ps-title { font-size: 0.9rem; font-weight: 800; color: #0f172a; margin: 0 0 8px; letter-spacing: -0.01em; }
.ps-text  { font-size: 0.84rem; color: #475569; line-height: 1.7; margin: 0 0 8px; }
.ps-text:last-child { margin-bottom: 0; }
.ps-mt { margin-top: 8px; }

.ps-highlight {
  display: flex; align-items: flex-start; gap: 8px;
  background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
  padding: 8px 12px; font-size: 0.8rem; font-weight: 700;
  color: #1d4ed8; margin-bottom: 8px; line-height: 1.5;
}
.highlight-icon { width: 14px; height: 14px; color: #2563eb; flex-shrink: 0; margin-top: 2px; }

.ps-list { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
.ps-list-item {
  display: flex; align-items: baseline; gap: 8px; font-size: 0.82rem;
  background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 7px;
  padding: 7px 12px; line-height: 1.5;
}
.ps-list-label { font-weight: 800; color: #334155; flex-shrink: 0; min-width: 72px; }
.ps-list-text  { color: #64748b; }

.ps-rights { margin-top: 8px; display: flex; flex-direction: column; gap: 6px; }
.ps-right-item {
  display: flex; align-items: center; gap: 10px;
  font-size: 0.82rem; color: #475569; padding: 5px 0;
  border-bottom: 1px dashed #f1f5f9;
}
.ps-right-item:last-of-type { border-bottom: none; }
.ps-right-dot { width: 7px; height: 7px; border-radius: 50%; background: #7c3aed; flex-shrink: 0; }

.ps-bullets { display: flex; flex-direction: column; gap: 5px; margin-top: 8px; }
.ps-bullet-item {
  display: flex; align-items: flex-start; gap: 10px;
  font-size: 0.82rem; color: #64748b; line-height: 1.55; padding: 4px 0;
}
.ps-plain-dot { width: 6px; height: 6px; border-radius: 50%; background: #e11d48; flex-shrink: 0; margin-top: 5px; }

/* Footer */
.policy-footer { padding: 18px 28px; border-top: 1px solid #f1f5f9; background: #f8fafc; }
.policy-footer-inner { display: flex; align-items: flex-start; gap: 10px; }
.policy-footer-inner p { font-size: 0.78rem; color: #94a3b8; line-height: 1.6; margin: 0; font-weight: 500; flex: 1; }
.footer-info-icon { width: 16px; height: 16px; color: #94a3b8; flex-shrink: 0; margin-top: 2px; }
</style>