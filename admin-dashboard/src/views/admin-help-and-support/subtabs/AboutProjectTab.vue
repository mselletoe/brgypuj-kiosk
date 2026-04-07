<script setup>
import {
  InformationCircleIcon,
  LightBulbIcon,
  ServerIcon,
  UserGroupIcon,
  CheckCircleIcon,
  WifiIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
} from "@heroicons/vue/24/outline";
</script>

<template>
  <!-- Full bleed wrapper — breaks out of any parent padding -->
  <div class="about-root">

    <!-- ═══════════════════════════════════════════════════════
         HERO BANNER
    ═══════════════════════════════════════════════════════ -->
    <div class="hero-banner section-row" style="animation-delay:0s">
      <!-- Animated rings -->
      <div class="hero-rings" aria-hidden="true">
        <span class="ring-1"></span>
        <span class="ring-2"></span>
        <span class="ring-3"></span>
        <span class="ring-4"></span>
        <span class="glow-dot"></span>
      </div>

      <!-- Grid overlay -->
      <div class="hero-grid" aria-hidden="true"></div>

      <div class="hero-content">
        <div class="hero-badges">
          <span class="badge">
            <span class="badge-dot"></span>
            PUP CPE Thesis Project
          </span>
          <span class="badge badge-outline">2025-2026</span>
          <span class="badge badge-outline">Poblacion I, Amadeo, Cavite</span>
        </div>

        <h1 class="hero-title">
          RFID-Enabled Barangay<br />
          <span class="hero-title-accent">Transaction Kiosk System</span>
        </h1>
        <p class="hero-sub">with SMS Notification</p>

        <p class="hero-desc">
          A self-service platform designed to modernize barangay transactions through RFID authentication,
          automated form handling, and GSM-based SMS notifications — fully offline, no cloud dependency.
        </p>

        <div class="hero-tags">
          <span v-for="tag in ['Vue.js','FastAPI','Raspberry Pi 4 Model B','RFID Reader','SIMCOM A7670E','PostgreSQL','Local LAN']"
                :key="tag" class="hero-tag">{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         STATS STRIP
    ═══════════════════════════════════════════════════════ -->
    <div class="stats-strip section-row" style="animation-delay:0.08s">
      <div v-for="s in [
        { value:'7', label:'Core Features' },
        { value:'4', label:'System Components' },
        { value:'4', label:'Research Members' },
        { value:'100%', label:'Offline Operation' },
      ]" :key="s.label" class="stat-item">
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         BACKGROUND + FEATURES GRID
    ═══════════════════════════════════════════════════════ -->
    <div class="two-col-grid section-row" style="animation-delay:0.15s">

      <!-- Project Background -->
      <div class="card card-bg">
        <div class="card-header-row">
          <div class="card-icon-wrap icon-blue">
            <InformationCircleIcon class="card-icon" />
          </div>
          <h3 class="card-title">Project Background</h3>
        </div>
        <p class="card-body">
          Barangay service delivery has long relied on manual processes — paper forms,
          manual encoding, and verbal announcements. This system addresses those
          inefficiencies with a centralized, offline-capable digital platform covering
          document requests, equipment borrowing, resident management, and community
          communication.
        </p>
        <div class="card-footer-tag">Est. Problem → Digital Solution</div>
      </div>

      <!-- Key Features -->
      <div class="card card-feat">
        <div class="card-header-row">
          <div class="card-icon-wrap icon-amber">
            <LightBulbIcon class="card-icon" />
          </div>
          <h3 class="card-title">Key Features</h3>
        </div>
        <ul class="feature-list">
          <li v-for="f in [
            'RFID-based resident authentication with auto-fill forms',
            'Document requests with .docx template auto-generation',
            'Equipment borrowing with availability tracking',
            'GSM-based SMS notifications — no internet required',
            'Bilingual kiosk UI (English / Filipino)',
            'Staff admin dashboard with full audit logs',
            'Fully offline — no cloud dependency',
          ]" :key="f" class="feature-item">
            <CheckCircleIcon class="feat-check" />
            <span>{{ f }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         SYSTEM COMPONENTS
    ═══════════════════════════════════════════════════════ -->
    <div class="card card-components section-row" style="animation-delay:0.22s">
      <div class="components-header">
        <div class="card-icon-wrap icon-purple">
          <ServerIcon class="card-icon" />
        </div>
        <h3 class="card-title">System Components</h3>
      </div>

      <div class="components-grid">
        <div v-for="(c, i) in [
          { name:'Kiosk Unit',      sub:'Raspberry Pi 4 Model B + Touchscreen',   icon:'computer', color:'blue'   },
          { name:'RFID Reader',     sub:'13.56 MHz Contactless', icon:'wifi',     color:'violet' },
          { name:'4G LTE module',      sub:'SIMCOM A7670E LTE Cat 1 Module',          icon:'phone',    color:'emerald'},
          { name:'Admin Dashboard', sub:'This interface · LAN-connected',  icon:'desktop',  color:'amber'  },
        ]" :key="c.name" class="comp-card" :class="'comp-card--'+c.color" :style="`animation-delay:${0.25+i*0.07}s`">
          <div class="comp-num">0{{ i+1 }}</div>
          <component :is="c.icon === 'wifi' ? WifiIcon : c.icon === 'phone' ? DevicePhoneMobileIcon : ComputerDesktopIcon"
                     class="comp-icon" />
          <div class="comp-name">{{ c.name }}</div>
          <div class="comp-sub">{{ c.sub }}</div>
          <div class="comp-bar"></div>
        </div>
      </div>

      <div class="comp-note">
        <span class="comp-note-dot"></span>
        The kiosk communicates with this dashboard over a local wireless LAN. No internet
        connection is required for any core operation. The GSM module handles outbound
        SMS independently through the cellular network.
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         RESEARCH TEAM
    ═══════════════════════════════════════════════════════ -->
    <div class="card card-team section-row" style="animation-delay:0.3s">
      <div class="card-header-row mb-6">
        <div class="card-icon-wrap icon-green">
          <UserGroupIcon class="card-icon" />
        </div>
        <h3 class="card-title">Research Team</h3>
      </div>

      <div class="team-grid">
        <div v-for="(m, i) in [
          { name:'Keanno Brennel A. Macatangay',   role:'Project Manager & Lead Writer'                    },
          { name:'Eloissa S. Francisco',           role:'Lead Full-Stack Developer & Database Administrator'},
          { name:'Alleah Marie G. Bayas',          role:'Communication & Client Liaison'                   },
          { name:'Justine Mae L. Convicto',        role:'UI/UX & Quality Assurance (QA) Lead'              },
        ]" :key="m.name" class="member-card" :style="`animation-delay:${0.33+i*0.06}s`">
          <div class="member-avatar">
            <span>{{ m.name.charAt(0) }}{{ m.name.split(' ').at(-1).charAt(0) }}</span>
            <div class="avatar-ring"></div>
          </div>
          <div class="member-name">{{ m.name }}</div>
          <div class="member-role">{{ m.role }}</div>
        </div>
      </div>

      <div class="team-footer">
        BS Computer Engineering &nbsp;·&nbsp; Polytechnic University of the Philippines &nbsp;·&nbsp; 2025-2026
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ─── Tokens ──────────────────────────────────────────────────── */
:root {
  --blue:    #2563eb;
  --blue-d:  #1d4ed8;
  --blue-l:  #eff6ff;
  --amber:   #f59e0b;
  --purple:  #7c3aed;
  --green:   #059669;
  --slate:   #0f172a;
  --muted:   #64748b;
  --border:  #e2e8f0;
}

/* ─── Root: break out of parent padding ──────────────────────── */
.about-root {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-left:  calc(-1 * var(--page-px, 2rem));
  margin-right: calc(-1 * var(--page-px, 2rem));
  padding-left:  var(--page-px, 2rem);
  padding-right: var(--page-px, 2rem);
  padding-bottom: 2rem;
}

/* ─── Section animation ───────────────────────────────────────── */
.section-row {
  opacity: 0;
  animation: riseUp 0.55s cubic-bezier(0.16,1,0.3,1) forwards;
}
@keyframes riseUp {
  from { opacity:0; transform:translateY(28px); }
  to   { opacity:1; transform:translateY(0);    }
}

/* ─── Hero Banner ─────────────────────────────────────────────── */
.hero-banner {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 45%, #2563eb 70%, #1e40af 100%);
  border-radius: 20px;
  padding: 45px 45px 36px;
  color: #fff;
  isolation: isolate;
}
@media (max-width: 768px) {
  .hero-banner { padding: 36px 28px 32px; }
}

.hero-rings {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.ring-1, .ring-2, .ring-3, .ring-4 {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.12);
  right: -60px; top: -60px;
  animation: ringPulse 6s ease-in-out infinite;
}
.ring-1 { width:220px; height:220px; animation-delay:0s;    }
.ring-2 { width:360px; height:360px; animation-delay:0.8s;  }
.ring-3 { width:500px; height:500px; animation-delay:1.6s;  }
.ring-4 { width:640px; height:640px; animation-delay:2.4s;  }

@keyframes ringPulse {
  0%,100% { opacity:0.12; }
  50%      { opacity:0.28; }
}
.glow-dot {
  position: absolute;
  right: 0; top: 0;
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(40%, -40%);
}
.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.hero-content { position: relative; z-index: 2; max-width: 820px; }

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(255,255,255,0.15);
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
.badge-outline {
  background: transparent;
  border-color: rgba(255,255,255,0.3);
}
.badge-dot {
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

.hero-title {
  font-size: clamp(1.8rem, 3.5vw, 2.9rem);
  font-weight: 900;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.2);
}
.hero-title-accent {
  background: linear-gradient(90deg, #93c5fd, #e0f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 1.15rem;
  font-weight: 500;
  color: rgba(255,255,255,0.6);
  margin: 0 0 20px;
  letter-spacing: 0.01em;
}
.hero-desc {
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255,255,255,0.82);
  max-width: 750px;
  margin-bottom: 28px;
}
.hero-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.hero-tag {
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 14px;
  border-radius: 8px;
  transition: background 0.2s, border-color 0.2s;
  cursor: default;
}
.hero-tag:hover {
  background: rgba(255,255,255,0.18);
  border-color: rgba(255,255,255,0.4);
}

/* ─── Stats strip ─────────────────────────────────────────────── */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #e2e8f0;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
}
@media (max-width: 640px) {
  .stats-strip { grid-template-columns: repeat(2,1fr); }
}
.stat-item {
  background: #fff;
  padding: 22px 20px;
  text-align: center;
  transition: background 0.2s;
}
.stat-item:hover { background: #f8fafc; }
.stat-value {
  font-size: 2rem;
  font-weight: 900;
  color: #1e40af;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ─── Cards shared ────────────────────────────────────────────── */
.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 32px 36px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s, transform 0.3s;
}
.card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
@media (max-width: 768px) {
  .card { padding: 24px 22px; }
}

/* ── ONLY CHANGE: icon + title side-by-side ── */
.card-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.card-header-row .card-icon-wrap {
  margin-bottom: 0;   /* override the standalone bottom margin */
  flex-shrink: 0;
}
.card-header-row .card-title {
  margin: 0;          /* override the standalone bottom margin */
}
/* mb-6 used on Research Team header-row */
.card-header-row.mb-6 {
  margin-bottom: 24px;
}

.card-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.icon-blue   { background:#eff6ff; }
.icon-amber  { background:#fffbeb; }
.icon-purple { background:#f5f3ff; }
.icon-green  { background:#ecfdf5; }

.card-icon { width: 24px; height: 24px; }
.icon-blue   .card-icon { color:#2563eb; }
.icon-amber  .card-icon { color:#d97706; }
.icon-purple .card-icon { color:#7c3aed; }
.icon-green  .card-icon { color:#059669; }

.card-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 14px;
  letter-spacing: -0.01em;
}
.card-body {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #475569;
}
.card-footer-tag {
  display: inline-block;
  margin-top: 18px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2563eb;
  background: #eff6ff;
  padding: 4px 12px;
  border-radius: 100px;
}

/* ─── 2-column grid ───────────────────────────────────────────── */
.two-col-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .two-col-grid { grid-template-columns: 1fr; }
}
.two-col-grid .card { margin: 0; }

/* ─── Feature list ────────────────────────────────────────────── */
.feature-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 11px; }
.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.93rem;
  color: #334155;
  line-height: 1.5;
}
.feat-check {
  width: 18px; height: 18px;
  color: #22c55e;
  flex-shrink: 0;
  margin-top: 1px;
}

/* ─── Components ──────────────────────────────────────────────── */
.components-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.components-header .card-icon-wrap { margin-bottom: 0; }
.components-header .card-title { margin: 0; }

.components-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 14px;
  margin-bottom: 20px;
}
@media (max-width: 900px) {
  .components-grid { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 500px) {
  .components-grid { grid-template-columns: 1fr; }
}

.comp-card {
  position: relative;
  border-radius: 14px;
  padding: 22px 20px 18px;
  border: 1px solid transparent;
  overflow: hidden;
  opacity: 0;
  animation: riseUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
  transition: transform 0.25s, box-shadow 0.25s;
}
.comp-card:hover { transform: translateY(-4px) scale(1.01); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }

.comp-card--blue   { background: linear-gradient(135deg,#eff6ff,#dbeafe); border-color:#bfdbfe; }
.comp-card--violet { background: linear-gradient(135deg,#f5f3ff,#ede9fe); border-color:#ddd6fe; }
.comp-card--emerald{ background: linear-gradient(135deg,#ecfdf5,#d1fae5); border-color:#a7f3d0; }
.comp-card--amber  { background: linear-gradient(135deg,#fffbeb,#fef3c7); border-color:#fde68a; }

.comp-num {
  position: absolute;
  top: 12px; right: 14px;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.06em;
  opacity: 0.35;
  color: #0f172a;
}
.comp-icon { width: 28px; height: 28px; margin-bottom: 12px; }
.comp-card--blue    .comp-icon { color:#2563eb; }
.comp-card--violet  .comp-icon { color:#7c3aed; }
.comp-card--emerald .comp-icon { color:#059669; }
.comp-card--amber   .comp-icon { color:#d97706; }

.comp-name { font-size: 0.95rem; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
.comp-sub  { font-size: 0.78rem; color: #475569; font-weight: 500; line-height: 1.4; }

.comp-bar {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 0 0 14px 14px;
}
.comp-card--blue    .comp-bar { background:#2563eb; }
.comp-card--violet  .comp-bar { background:#7c3aed; }
.comp-card--emerald .comp-bar { background:#059669; }
.comp-card--amber   .comp-bar { background:#d97706; }

.comp-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 0.88rem;
  color: #64748b;
  line-height: 1.6;
}
.comp-note-dot {
  flex-shrink: 0;
  margin-top: 6px;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
}

/* ─── Team ────────────────────────────────────────────────────── */
.mb-6 { margin-bottom: 24px; }
.team-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 16px;
  margin-bottom: 28px;
}
@media (max-width: 900px) {
  .team-grid { grid-template-columns: repeat(2,1fr); }
}

.member-card {
  text-align: center;
  padding: 26px 16px 22px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: #fff;
  opacity: 0;
  animation: riseUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
  transition: transform 0.3s, box-shadow 0.3s;
}
.member-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(37,99,235,0.12);
  border-color: #bfdbfe;
}

.member-avatar {
  position: relative;
  width: 60px; height: 60px;
  margin: 0 auto 14px;
}
.member-avatar span {
  position: relative;
  z-index: 2;
  display: flex;
  width: 60px; height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  font-size: 1.1rem;
  font-weight: 800;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(37,99,235,0.35);
}
.avatar-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid #bfdbfe;
  opacity: 0;
  transition: opacity 0.3s, transform 0.3s;
  transform: scale(0.85);
}
.member-card:hover .avatar-ring {
  opacity: 1;
  transform: scale(1);
}

.member-name {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.35;
  margin-bottom: 5px;
}
.member-role {
  font-size: 0.76rem;
  font-weight: 600;
  color: #2563eb;
  background: #eff6ff;
  display: inline-block;
  padding: 2px 10px;
  border-radius: 100px;
}

.team-footer {
  border-top: 1px solid #e2e8f0;
  padding-top: 18px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #94a3b8;
}
</style>