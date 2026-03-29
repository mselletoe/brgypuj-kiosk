<script setup>
import { ref } from "vue";
import {
  CodeBracketIcon,
  CheckIcon,
  ClipboardDocumentIcon,
  IdentificationIcon,
  UserGroupIcon,
  BellAlertIcon,
  ServerIcon,
  ClockIcon,
  LockClosedIcon,
  ExclamationTriangleIcon,
} from "@heroicons/vue/24/outline";

const placeholderGroups = [
  {
    group: "Name Fields",
    icon: IdentificationIcon,
    color: "blue",
    placeholders: [
      { key: "full_name", aliases: ["full_name", "name", "resident_name", "applicant_name"], description: "Full legal name of the resident" },
      { key: "first_name", aliases: ["first_name", "fname"], description: "First (given) name" },
      { key: "middle_name", aliases: ["middle_name", "mname"], description: "Middle name" },
      { key: "last_name", aliases: ["last_name", "lname", "surname"], description: "Last name / Surname" },
      { key: "suffix", aliases: ["suffix", "name_suffix"], description: "Name suffix (e.g., Jr., Sr., III)" },
    ],
  },
  {
    group: "Personal Information",
    icon: UserGroupIcon,
    color: "violet",
    placeholders: [
      { key: "gender", aliases: ["gender", "sex"], description: "Gender or biological sex" },
      { key: "birthdate", aliases: ["birthdate", "date_of_birth", "birth_date", "dob"], description: "Date of birth" },
      { key: "age", aliases: ["age"], description: "Current age of the resident" },
    ],
  },
  {
    group: "Contact Information",
    icon: BellAlertIcon,
    color: "emerald",
    placeholders: [
      { key: "email", aliases: ["email", "email_address"], description: "Email address" },
      { key: "phone_number", aliases: ["phone_number", "contact_number", "mobile_number", "phone", "contact"], description: "Mobile / contact number" },
    ],
  },
  {
    group: "Address Fields",
    icon: ServerIcon,
    color: "orange",
    placeholders: [
      { key: "unit_blk_street", aliases: ["unit_blk_street", "street", "house_number", "house_no"], description: "Unit, block, or street address" },
      { key: "purok_name", aliases: ["purok_name", "purok", "sitio"], description: "Purok or sitio name" },
      { key: "barangay", aliases: ["barangay", "brgy"], description: "Barangay name" },
      { key: "municipality", aliases: ["municipality", "city"], description: "Municipality or city" },
      { key: "province", aliases: ["province", "prov"], description: "Province" },
      { key: "region", aliases: ["region"], description: "Region" },
      { key: "full_address", aliases: ["full_address", "address", "complete_address"], description: "Complete combined address string" },
    ],
  },
  {
    group: "Residency Information",
    icon: ClockIcon,
    color: "teal",
    placeholders: [
      { key: "yr_res", aliases: ["yr_res", "years_residency", "years_of_residency", "residency_years", "year_residency"], description: "Number of years residing in the barangay" },
      { key: "rds", aliases: ["rds", "residency_start_date", "date_started_residency"], description: "Date when residency started" },
    ],
  },
  {
    group: "ID Numbers",
    icon: LockClosedIcon,
    color: "rose",
    placeholders: [
      { key: "rfid_uid", aliases: ["rfid_uid", "rfid", "card_number", "rfid_number"], description: "Resident RFID card unique identifier" },
      { key: "id_num", aliases: ["id_num", "brgy_id"], description: "Resident Barangay I.D Number" },
    ],
  },
];

const copiedKey = ref(null);

const copyToClipboard = (text) => {
  const normalized = ` ${text.trim()} `;
  navigator.clipboard.writeText(`{{${normalized}}}`);
  copiedKey.value = text;
  setTimeout(() => { copiedKey.value = null; }, 2000);
};

const totalFields = placeholderGroups.reduce((a, g) => a + g.placeholders.length, 0);
const totalAliases = placeholderGroups.reduce((a, g) => a + g.placeholders.reduce((b, p) => b + p.aliases.length, 0), 0);

const colorStyles = {
  blue:    { wrap: 'grp-wrap--blue',    primary: 'tag--blue',    alias: 'alias--blue'    },
  violet:  { wrap: 'grp-wrap--violet',  primary: 'tag--violet',  alias: 'alias--violet'  },
  emerald: { wrap: 'grp-wrap--emerald', primary: 'tag--emerald', alias: 'alias--emerald' },
  orange:  { wrap: 'grp-wrap--orange',  primary: 'tag--orange',  alias: 'alias--orange'  },
  teal:    { wrap: 'grp-wrap--teal',    primary: 'tag--teal',    alias: 'alias--teal'    },
  rose:    { wrap: 'grp-wrap--rose',    primary: 'tag--rose',    alias: 'alias--rose'    },
};
</script>

<template>
  <div class="ph-root">

    <!-- ── Hero Banner ─────────────────────────────────────────── -->
    <div class="ph-hero section-row" style="animation-delay:0s">
      <div class="ph-rings" aria-hidden="true">
        <span class="pring pring-1"></span>
        <span class="pring pring-2"></span>
        <span class="pring pring-3"></span>
        <span class="ph-orb"></span>
      </div>
      <div class="ph-grid" aria-hidden="true"></div>
      <div class="ph-hero-content">
        <div class="ph-badges">
          <span class="pbadge">
            <span class="pbadge-dot"></span>
            Template Reference
          </span>
          <span class="pbadge pbadge-outline">{{ placeholderGroups.length }} Groups</span>
          <span class="pbadge pbadge-outline">{{ totalFields }} Fields</span>
        </div>
        <h1 class="ph-title">
          Document Template<br />
          <span class="ph-accent">Placeholders</span>
        </h1>
        <p class="ph-sub">
          Insert these into your <code class="ph-code">.docx</code> templates using double curly braces.
          The system auto-replaces them with resident profile data on request submission.
        </p>
      </div>

      <!-- Floating code preview -->
      <div class="ph-code-preview" aria-hidden="true">
        <div class="code-preview-bar">
          <span class="code-dot code-dot-red"></span>
          <span class="code-dot code-dot-yellow"></span>
          <span class="code-dot code-dot-green"></span>
          <span class="code-preview-label">template.docx</span>
        </div>
        <div class="code-preview-body">
          <div class="code-line"><span class="code-plain">This certifies that </span><span class="code-ph">&#123;&#123;full_name&#125;&#125;</span></div>
          <div class="code-line"><span class="code-plain">of </span><span class="code-ph">&#123;&#123;full_address&#125;&#125;</span><span class="code-plain">,</span></div>
          <div class="code-line"><span class="code-plain">Age: </span><span class="code-ph">&#123;&#123;age&#125;&#125;</span><span class="code-plain"> | </span><span class="code-ph">&#123;&#123;gender&#125;&#125;</span></div>
          <div class="code-line"><span class="code-plain">has been a resident for </span><span class="code-ph">&#123;&#123;years_residency&#125;&#125;</span><span class="code-plain"> years.</span></div>
        </div>
      </div>
    </div>

    <!-- ── Stats strip ─────────────────────────────────────────── -->
    <div class="ph-stats section-row" style="animation-delay:0.07s">
      <div v-for="s in [
        { value: placeholderGroups.length, label: 'Field Groups'   },
        { value: totalFields,              label: 'Total Fields'   },
        { value: totalAliases,             label: 'Total Aliases'  },
        { value: '1-click',                label: 'Copy to Clipboard' },
      ]" :key="s.label" class="phstat-item">
        <div class="phstat-value">{{ s.value }}</div>
        <div class="phstat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- ── How-to steps ───────────────────────────────────────── -->
    <div class="steps-card section-row" style="animation-delay:0.13s">
      <div class="steps-header">
        <div class="steps-icon-wrap">
          <CodeBracketIcon class="steps-icon" />
        </div>
        <div>
          <h2 class="steps-title">How to Use Placeholders</h2>
          <p class="steps-sub">Three steps to get your template working</p>
        </div>
      </div>
      <div class="steps-grid">
        <div v-for="(step, i) in [
          { title: 'Create a .docx Template', text: 'Open Microsoft Word and design your document (e.g., Barangay Clearance) as normal.' },
          { title: 'Insert Placeholders',     text: 'Where resident data should appear, type the placeholder in double curly braces: e.g. {{full_name}}.' },
          { title: 'Upload in Document Services', text: 'Go to Document Services, open the document type, and upload the .docx file.' },
        ]" :key="step.title" class="step-item">
          <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
          <div class="step-line"></div>
          <div class="step-body">
            <div class="step-title">{{ step.title }}</div>
            <p class="step-text">{{ step.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Placeholder Groups ─────────────────────────────────── -->
    <div
      v-for="(group, gi) in placeholderGroups"
      :key="group.group"
      class="grp-card section-row"
      :style="`animation-delay:${0.18 + gi * 0.05}s`"
    >
      <!-- Group header -->
      <div class="grp-header" :class="colorStyles[group.color].wrap">
        <div class="grp-icon-wrap" :class="'grp-icon--' + group.color">
          <component :is="group.icon" class="grp-icon" />
        </div>
        <div class="grp-header-meta">
          <span class="grp-title">{{ group.group }}</span>
          <span class="grp-count">{{ group.placeholders.length }} field{{ group.placeholders.length !== 1 ? 's' : '' }}</span>
        </div>
      </div>

      <!-- Placeholder rows -->
      <div class="grp-rows">
        <div
          v-for="ph in group.placeholders"
          :key="ph.key"
          class="ph-row"
        >
          <div class="ph-row-tags">
            <!-- Primary key -->
            <button
              @click="copyToClipboard(ph.key)"
              class="ph-tag"
              :class="copiedKey === ph.key ? 'ph-tag--copied' : colorStyles[group.color].primary"
              title="Click to copy"
            >
              <CheckIcon v-if="copiedKey === ph.key" class="tag-icon" />
              <ClipboardDocumentIcon v-else class="tag-icon" />
              <span class="tag-text">&#123;&#123;{{ ph.key }}&#125;&#125;</span>
            </button>

            <!-- Aliases -->
            <button
              v-for="alias in ph.aliases.slice(1)"
              :key="alias"
              @click="copyToClipboard(alias)"
              class="ph-alias"
              :class="copiedKey === alias ? 'ph-tag--copied' : colorStyles[group.color].alias"
              title="Click to copy"
            >
              {{ alias }}
            </button>
          </div>
          <p class="ph-desc">{{ ph.description }}</p>
        </div>
      </div>
    </div>

    <!-- ── Important Notes ────────────────────────────────────── -->
    <div class="notes-card section-row" style="animation-delay:0.55s">
      <div class="notes-header">
        <div class="notes-icon-wrap">
          <ExclamationTriangleIcon class="notes-icon" />
        </div>
        <div>
          <h3 class="notes-title">Important Notes</h3>
          <p class="notes-sub">Read before uploading templates</p>
        </div>
      </div>
      <div class="notes-list">
        <div v-for="(note, i) in [
          { label: 'Exact spelling required.',        text: 'Placeholders are case-sensitive. \`Full_Name\` will NOT work — use \`full_name\`.' },
          { label: 'Click any tag to copy it',        text: 'Tags copy as a ready-to-paste {{placeholder}} string. Primary and alias tags both work.' },
          { label: 'Aliases are interchangeable.',    text: '{{name}} and {{full_name}} both produce the resident\'s full name.' },
          { label: 'RFID sessions only for auto-fill.', text: 'Walk-in residents fill forms manually; RFID tap triggers the auto-fill.' },
          { label: 'Missing data leaves a blank.',    text: 'If a resident has no email on file, the {{email}} placeholder becomes empty — no error is thrown.' },
        ]" :key="note.label" class="note-item">
          <div class="note-num">{{ String(i + 1).padStart(2, '0') }}</div>
          <div>
            <span class="note-label">{{ note.label }}</span>
            <span class="note-text"> {{ note.text }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ─── Root ───────────────────────────────────────────────────── */
.ph-root {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding-bottom: 2rem;
}

/* ─── Animations ─────────────────────────────────────────────── */
.section-row {
  opacity: 0;
  animation: riseUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes riseUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0);    }
}

/* ─── Hero ───────────────────────────────────────────────────── */
.ph-hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 35%, #1d4ed8 70%, #2563eb 100%);
  border-radius: 20px;
  padding: 48px 52px 44px;
  color: #fff;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 32px;
  isolation: isolate;
  width: 100%;
  box-sizing: border-box;
}
@media (max-width: 900px) {
  .ph-hero { flex-direction: column; padding: 32px 24px 28px; }
  .ph-code-preview { display: none; }
}

/* rings */
.ph-rings { position: absolute; inset: 0; pointer-events: none; }
.pring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.1);
  right: -80px; top: -80px;
  animation: ringPulse 7s ease-in-out infinite;
}
.pring-1 { width: 260px; height: 260px; animation-delay: 0s; }
.pring-2 { width: 460px; height: 460px; animation-delay: 1s; }
.pring-3 { width: 660px; height: 660px; animation-delay: 2s; }
@keyframes ringPulse {
  0%,100% { opacity: 0.1; }
  50%      { opacity: 0.22; }
}
.ph-orb {
  position: absolute;
  right: -20px; top: -20px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(96,165,250,0.18) 0%, transparent 70%);
  border-radius: 50%;
}
.ph-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.ph-hero-content { position: relative; z-index: 2; flex: 1; min-width: 0; }

.ph-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 22px;
}
.pbadge {
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
.pbadge-outline { background: transparent; border-color: rgba(255,255,255,0.28); }
.pbadge-dot {
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

.ph-title {
  font-size: clamp(1.7rem, 3vw, 2.7rem);
  font-weight: 900;
  line-height: 1.13;
  letter-spacing: -0.02em;
  margin: 0 0 12px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.25);
}
.ph-accent {
  background: linear-gradient(90deg, #93c5fd, #e0f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.ph-sub {
  font-size: 0.95rem;
  color: rgba(255,255,255,0.7);
  line-height: 1.65;
  max-width: 520px;
  margin: 0;
}
.ph-code {
  background: rgba(255,255,255,0.18);
  border-radius: 5px;
  padding: 1px 7px;
  font-size: 0.85em;
  font-family: ui-monospace, monospace;
}

/* floating code preview */
.ph-code-preview {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
  width: 290px;
  background: rgba(15,23,42,0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
  align-self: center;
}
.code-preview-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.05);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.code-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
}
.code-dot-red    { background: #f87171; }
.code-dot-yellow { background: #fbbf24; }
.code-dot-green  { background: #4ade80; }
.code-preview-label {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  font-family: ui-monospace, monospace;
  margin-left: 4px;
}
.code-preview-body {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.code-line {
  font-family: ui-monospace, monospace;
  font-size: 12px;
  line-height: 1.5;
}
.code-plain { color: rgba(255,255,255,0.5); }
.code-ph {
  color: #93c5fd;
  background: rgba(147,197,253,0.12);
  border-radius: 4px;
  padding: 1px 5px;
}

/* ─── Stats ──────────────────────────────────────────────────── */
.ph-stats {
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
@media (max-width: 640px) { .ph-stats { grid-template-columns: repeat(2,1fr); } }
.phstat-item {
  background: #fff;
  padding: 20px;
  text-align: center;
  transition: background 0.2s;
}
.phstat-item:hover { background: #f8fafc; }
.phstat-value {
  font-size: 1.85rem;
  font-weight: 900;
  color: #1e40af;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-bottom: 5px;
}
.phstat-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ─── Steps card ─────────────────────────────────────────────── */
.steps-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 28px 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s;
  width: 100%;
  box-sizing: border-box;
}
.steps-card:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.07); }
.steps-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
  border-bottom: 1px solid #f1f5f9;
}
.steps-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.steps-icon { width: 22px; height: 22px; color: #2563eb; }
.steps-title {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 3px;
  letter-spacing: -0.01em;
}
.steps-sub { font-size: 0.8rem; color: #94a3b8; margin: 0; font-weight: 500; }

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
}
@media (max-width: 768px) { .steps-grid { grid-template-columns: 1fr; } }

.step-item {
  display: flex;
  flex-direction: column;
  padding: 0 24px;
  border-right: 1px solid #f1f5f9;
}
.step-item:first-child { padding-left: 0; }
.step-item:last-child  { border-right: none; padding-right: 0; }
@media (max-width: 768px) {
  .step-item { padding: 16px 0; border-right: none; border-bottom: 1px solid #f1f5f9; }
  .step-item:last-child { border-bottom: none; }
}

.step-num {
  font-size: 2.2rem;
  font-weight: 900;
  color: #7db6ff;
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 6px;
}
.step-line {
  width: 32px; height: 3px;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 100px;
  margin-bottom: 12px;
}
.step-title {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}
.step-text {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

/* ─── Group card ─────────────────────────────────────────────── */
.grp-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s, transform 0.3s;
  width: 100%;
  box-sizing: border-box;
}
.grp-card:hover {
  box-shadow: 0 8px 28px rgba(0,0,0,0.07);
  transform: translateY(-2px);
}

.grp-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 22px;
  border-bottom: 1px solid transparent;
}
/* per-color header backgrounds */
.grp-wrap--blue    { background: #eff6ff; border-bottom-color: #dbeafe; }
.grp-wrap--violet  { background: #f5f3ff; border-bottom-color: #ede9fe; }
.grp-wrap--emerald { background: #ecfdf5; border-bottom-color: #d1fae5; }
.grp-wrap--orange  { background: #fff7ed; border-bottom-color: #fed7aa; }
.grp-wrap--teal    { background: #f0fdfa; border-bottom-color: #ccfbf1; }
.grp-wrap--rose    { background: #fff1f2; border-bottom-color: #fecdd3; }

.grp-icon-wrap {
  width: 34px; height: 34px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.grp-icon { width: 18px; height: 18px; }
.grp-icon--blue    { background: #dbeafe; } .grp-icon--blue    .grp-icon { color: #2563eb; }
.grp-icon--violet  { background: #ede9fe; } .grp-icon--violet  .grp-icon { color: #7c3aed; }
.grp-icon--emerald { background: #d1fae5; } .grp-icon--emerald .grp-icon { color: #059669; }
.grp-icon--orange  { background: #fed7aa; } .grp-icon--orange  .grp-icon { color: #ea580c; }
.grp-icon--teal    { background: #ccfbf1; } .grp-icon--teal    .grp-icon { color: #0d9488; }
.grp-icon--rose    { background: #fecdd3; } .grp-icon--rose    .grp-icon { color: #e11d48; }

.grp-header-meta { flex: 1; display: flex; align-items: center; justify-content: space-between; }
.grp-title { font-size: 0.92rem; font-weight: 800; color: #0f172a; }
.grp-count { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.07em; }

/* rows */
.ph-row {
  padding: 14px 22px;
  border-bottom: 1px solid #f8fafc;
  transition: background 0.15s;
}
.ph-row:last-child { border-bottom: none; }
.ph-row:hover { background: #fafbff; }

.ph-row-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

/* Primary tag */
.ph-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: ui-monospace, monospace;
  font-size: 12px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 7px;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, transform 0.15s;
}
.ph-tag:hover { opacity: 0.82; transform: scale(0.97); }
.tag-icon { width: 12px; height: 12px; flex-shrink: 0; }
.tag-text { letter-spacing: -0.01em; }

.ph-tag--copied { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }

.tag--blue    { background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }
.tag--violet  { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
.tag--emerald { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
.tag--orange  { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }
.tag--teal    { background: #ccfbf1; color: #0f766e; border: 1px solid #99f6e4; }
.tag--rose    { background: #ffe4e6; color: #be123c; border: 1px solid #fecdd3; }

/* Alias tag */
.ph-alias {
  display: inline-block;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 9px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, transform 0.15s;
}
.ph-alias:hover { opacity: 0.75; transform: scale(0.97); }

.alias--blue    { background: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe; }
.alias--violet  { background: #f5f3ff; color: #8b5cf6; border: 1px solid #ddd6fe; }
.alias--emerald { background: #f0fdf4; color: #22c55e; border: 1px solid #bbf7d0; }
.alias--orange  { background: #fff7ed; color: #f97316; border: 1px solid #fed7aa; }
.alias--teal    { background: #f0fdfa; color: #14b8a6; border: 1px solid #ccfbf1; }
.alias--rose    { background: #fff1f2; color: #f43f5e; border: 1px solid #fecdd3; }

.ph-desc {
  font-size: 0.79rem;
  color: #64748b;
  line-height: 1.55;
  margin: 0;
}

/* ─── Notes card ─────────────────────────────────────────────── */
.notes-card {
  background: linear-gradient(135deg, #fffbeb, #fef9ec);
  border: 1px solid #fde68a;
  border-radius: 18px;
  padding: 26px 30px;
  width: 100%;
  box-sizing: border-box;
}
.notes-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid #fde68a;
}
.notes-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: #fef3c7;
  border: 1px solid #fde68a;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.notes-icon { width: 22px; height: 22px; color: #d97706; }
.notes-title {
  font-size: 1rem;
  font-weight: 800;
  color: #92400e;
  margin: 0 0 3px;
}
.notes-sub { font-size: 0.8rem; color: #b45309; margin: 0; font-weight: 500; }

.notes-list { display: flex; flex-direction: column; gap: 12px; }
.note-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: rgba(255,255,255,0.6);
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 12px 16px;
  transition: background 0.2s;
}
.note-item:hover { background: rgba(255,255,255,0.85); }
.note-num {
  font-size: 10px;
  font-weight: 900;
  color: #d97706;
  letter-spacing: 0.08em;
  flex-shrink: 0;
  margin-top: 2px;
  min-width: 20px;
}
.note-label {
  font-size: 0.84rem;
  font-weight: 800;
  color: #92400e;
}
.note-text {
  font-size: 0.84rem;
  color: #78350f;
  line-height: 1.6;
}
</style>