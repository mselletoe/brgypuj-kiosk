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
  KeyIcon,
  Cog6ToothIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  CircleStackIcon,
  AdjustmentsHorizontalIcon,
  ClipboardDocumentListIcon,
  UserCircleIcon,
} from "@heroicons/vue/24/outline";

import imgPage1  from "@/assets/manual_imgs/page1.png";
import imgPage2  from "@/assets/manual_imgs/page2.png";
import imgPage3  from "@/assets/manual_imgs/page3.png";
import imgPage4  from "@/assets/manual_imgs/page4.png";
import imgPage5  from "@/assets/manual_imgs/page5.png";
import imgPage6  from "@/assets/manual_imgs/page6.png";
import imgPage7  from "@/assets/manual_imgs/page7.png";
import imgPage8  from "@/assets/manual_imgs/page8.png";
import imgPage9  from "@/assets/manual_imgs/page9.png";
import imgPage10 from "@/assets/manual_imgs/page10.png";
import imgPage11 from "@/assets/manual_imgs/page11.png";
import imgPage12 from "@/assets/manual_imgs/page12.png";
import imgPage13 from "@/assets/manual_imgs/page13.png";
import imgPage14 from "@/assets/manual_imgs/page14.png";
import imgPage15 from "@/assets/manual_imgs/page15.png";
import imgPage16 from "@/assets/manual_imgs/page16.png";
import imgPage17 from "@/assets/manual_imgs/page17.png";
import imgPage18 from "@/assets/manual_imgs/page18.png";
import imgPage19 from "@/assets/manual_imgs/page19.png";
import imgPage20 from "@/assets/manual_imgs/page20.png";
import imgPage21 from "@/assets/manual_imgs/page21.png";
import imgPage22 from "@/assets/manual_imgs/page22.png";
import imgPage23 from "@/assets/manual_imgs/page23.png";
import imgPage24 from "@/assets/manual_imgs/page24.png";

const openGuideItems = ref(new Set());
const toggleGuideItem = (id) => {
  if (openGuideItems.value.has(id)) openGuideItems.value.delete(id);
  else openGuideItems.value.add(id);
};

const guideModules = [
  {
    id: "account-access",
    icon: KeyIcon,
    color: "violet",
    title: "Account Access",
    summary: "How to log in and create new admin accounts.",
    img: imgPage1,
    sections: [
      { heading: "Logging In", img: null },
      { text: "1. Click the **Username** field and type your identifier." },
      { text: "2. Click the **Password** field and type your password." },
      { text: "3. Click the **Eye Icon** to check if your password is typed correctly." },
      { text: "4. Click the **Login** button." },
      {img: imgPage2 },
      { heading: "Creating an Account (New Users)" },
      { text: "1. Click the **Create Account** button at the bottom of the login page." },
      { text: "2. Click the **Select Resident** dropdown and select your name." },
      { text: "3. Type a unique name in the **Username** field." },
      { text: "4. Type your password in the **Password** field and re-type it in the **Confirm Password** field." },
      { text: "5. Click the **Create Account** button to submit." },
    ],
  },
  {
    id: "overview",
    icon: ServerIcon,
    color: "blue",
    title: "Overview & Dashboard Navigation",
    summary: "Interface layout, quick actions, and navigating the dashboard.",
    img: imgPage3,
    sections: [
      { heading: "Interface Layout" },
      { text: "• Click the top-left arrow to expand or collapse the **Left Sidebar Menu** (the blue Home icon indicates the Overview)." },
      { text: "• Use the **Top Navigation Bar** for quick access to Search, Directory, Messages, Notifications, and Settings." },
      { text: "• Access **Account Settings** and **Logout Account** next to the quick-access icons." },
      { text: "• Check the top right of your screen for the yellow **Action Required Banner** to identify urgent pending tasks." },
      { heading: "Quick Actions Grid", style: "margin-top: 1.5rem" },
      { text: "• Click **Send SMS** to broadcast announcements." },
      { text: "• Click **Notifications** to view system alerts." },
      { text: "• Click **System Preferences** to edit underlying settings." },
      { text: "• Click **Maintenance Mode** to manage the kiosk's operational status." },
      { text: "• Click **Add Kiosk FAQs** to manage helpful information for residents." },
      { text: "• Click **Backup Data** to secure system information." },
    ],
  },
  {
    id: "document-requests",
    icon: DocumentTextIcon,
    color: "amber",
    title: "Processing Document Requests",
    summary: "Filter, review, approve, and export resident document requests.",
    img: imgPage4,
    sections: [
      { text: "Navigate to **Document Requests** to manage paperwork requested via the kiosk." },
      { heading: "Filter & Search", style: "margin-top: 1.5rem" },
      { text: "Use the tabs (**Pending, Approved, Released, Rejected**) or the search bar to locate transactions. Click the **Filter** button (funnel icon) to narrow results." },
      { text: "Use the top-right icons for bulk actions: **Undo/Reset arrow**, **Checkbox** (select multiple), or **Trash bin** (delete)." },
      { heading: "Processing Workflow", style: "margin-top: 1.5rem" },
      { text: "1. Select a request to view details." },
      { text: "2. Collect physical payment and click **Mark as Paid**. *(Note: Approval is disabled until the request is marked as paid)*." },
      { text: "3. Click **Approve** to authorize, or **Reject** to decline." },
      { heading: "Export", style: "margin-top: 1.5rem" },
      { text: "Click **Export Financial Statement** for accounting records." },
    ],
  },
  {
    id: "equipment-requests",
    icon: WrenchScrewdriverIcon,
    color: "rose",
    title: "Processing Equipment Requests",
    summary: "Navigate, filter, and process barangay equipment borrowing requests.",
    img: imgPage5,
    sections: [
      { heading: "Navigating and Filtering" },
      { text: "• Access **Equipment Requests** via the Left Sidebar Menu." },
      { text: "• Click the status tabs — **Pending, Approved, Released**, and **Rejected** — to filter requests." },
      { text: "• Type a name or transaction number in the **Search** text box (top right)." },
      { text: "• Click the **Filter** button (funnel icon) to narrow results." },
      { text: "• Use the top-right icons for bulk actions: **Undo/Reset arrow**, **Checkbox** (select multiple), or **Trash bin** (delete)." },
      { text: "• Click the **Export Financial Statement** link to download records." },
      { heading: "Reviewing and Processing", style: "margin-top: 1.5rem" },
      { text: "• Locate the unique **Transaction No** in the left box." },
      { text: "• Identify the **Document Name** in large, bold text." },
      { text: "• Check the **Requester Info** for the resident's name and request date." },
      { text: "• Click the blue **RFID No** to review the resident's profile." },
      { text: "• View the required fee in the green **Payment Status** price tag." },
      { text: "• Click the gray **MARK AS PAID** button after collecting physical payment (offline system requires manual verification)." },
      { text: "• Click the blue **View File** button to review document details." },
      { text: "• Click the white **Notes** button to add or view internal comments." },
      { text: "• Click **Approve** (this button remains grayed-out until you view the file or mark it as paid)." },
      { text: "• Click the white **Reject** button to decline the request." },
      { text: "• Click the red **Trash Icon** to delete the request entirely." },
    ],
  },
  {
    id: "feedbacks",
    icon: ChatBubbleLeftRightIcon,
    color: "teal",
    title: "Feedbacks and Reports",
    summary: "Review resident feedback ratings and manage lost RFID card reports.",
    img: imgPage6,
    sections: [
      { heading: "Managing Community Reviews (Feedbacks Tab)" },
      { text: "• Click **Feedbacks and Reports** on the left sidebar (blue chat bubble icon)." },
      { text: "• Switch between the **Feedbacks** and **Reports** tabs at the top." },
      { text: "• Use the **Search bar** or bulk action tools (**Checkbox**, **Trash** icon) at the top right." },
      { text: "• Read the **Reference No.** in the light blue box." },
      { text: "• Read the bold **Category** to identify the topic." },
      { text: "• Check **Feedback from & Date** and the **RFID No.** (displays orange \"Guest Mode\" if the user did not log in)." },
      { text: "• View the text **Rating** and yellow stars (1 to 5)." },
      { text: "• Read the **Additional Comment** (defaults to \"No comments provided\" if empty)." },
      { text: "• Click the red **Trash Can** icon to delete an entry." },
      {img: imgPage7 },
      { heading: "Checking for Lost Cards (Reports Tab)" },
      { text: "• Click the **Reports** tab to track residents who misplaced their RFID cards." },
      { text: "• Use the top-right tools to manage reports: **Undo/Reset Arrow** (clear view), **Checkbox** (select multiple), or **Trash** icon (delete)." },
    ],
  },
  {
    id: "document-services",
    icon: DocumentTextIcon,
    color: "violet",
    title: "Document Services Management",
    summary: "Add, configure, and manage document types and templates available on the kiosk.",
    img: imgPage8,
    sections: [
      { heading: "Adding and Managing Documents" },
      { text: "• Click **Document Services** under SYSTEM MANAGERS." },
      { text: "• Click the **+ Add** button to create a new service." },
      { text: "• Use the **Search** box, **Checkbox**, or **Trash** icon to manage the list." },
      { text: "• Review the **Document List** table columns: Checkbox, Name, Price, and Status." },
      { heading: "Using the Actions Column", style: "margin-top: 1.5rem" },
      { text: "• Click the orange **Pencil Icon** to edit basic details or price." },
      { text: "• Click the blue **Bulleted List Icon** to manage document requirements." },
      { text: "• Click the purple **Document/Page Icon** to view or edit the digital form." },
      { text: "• Click the blue **Arrow Pointing Up Icon** to upload a new template file." },
      { text: "• Click the red **Trash Can Icon** to delete the service." },
      { heading: "Managing the Barangay I.D Section", style: "margin-top: 1.5rem" },
      { text: "• Locate the light purple box at the top of the page." },
      { text: "• Look for the yellow/orange **No Template** warning badge (requires a template upload to issue IDs)." },
      { text: "• Check the current price and click the dropdown arrow to manage further ID options." },
    ],
  },
  {
    id: "equipment-inventory",
    icon: WrenchScrewdriverIcon,
    color: "orange",
    title: "Equipment Inventory Management",
    summary: "Register and manage borrowable barangay assets and stock levels.",
    img: imgPage9,
    sections: [
      { heading: "Managing Equipment Inventory" },
      { text: "• Click **Equipment Inventory** under SYSTEM MANAGERS." },
      { text: "• Click the **+ Add** button to register new equipment." },
      { text: "• Review the white inventory cards for **ITEM NAME**, **TOTAL OWNED**, **AVAILABLE**, and **RENTAL RATE PER DAY**." },
      { text: "• Use the **Search** box, **Checkbox**, or **Trash** icon at the top right for bulk actions." },
      { text: "• Click the **Checkbox** on an individual card to target it for bulk deletion." },
      { text: "• Click the orange **Pencil Icon** to edit rental rates or total owned stock." },
      { text: "• Click the red **Trash Can Icon** to delete the item permanently." },
    ],
  },
  {
    id: "announcements",
    icon: BellAlertIcon,
    color: "cyan",
    title: "Kiosk Announcements",
    summary: "Post and manage event notices displayed on the kiosk screensaver.",
    img: imgPage10,
    sections: [
      { heading: "Posting and Managing Notices" },
      { text: "• Click **Kiosk Announcements** under SYSTEM MANAGERS." },
      { text: "• Click the blue **+ Add** button to create a new notice." },
      { text: "• Review active cards for the uploaded cover photo, green **Active** badge, **Event Title**, **DATE**, **TIME**, and **LOCATION**." },
      { text: "• Use the **Search** box, **Checkbox**, or **Trash** icon for bulk actions." },
      { text: "• Click the **Checkbox** on a specific cover photo to target it." },
      { text: "• Click the orange/yellow **Pencil Icon** to edit details or swap the photo." },
      { text: "• Click the red **Trash Can Icon** to delete the announcement." },
    ],
  },
  {
    id: "blotter",
    icon: ExclamationTriangleIcon,
    color: "orange",
    title: "Blotter and KP Logs",
    summary: "File, review, and manage barangay incident and KP mediation records.",
    img: imgPage11,
    sections: [
      { heading: "Filing and Reviewing Records" },
      { text: "• Click **Blotter and KP Logs** under SYSTEM MANAGERS (blue clipboard list icon)." },
      { text: "• Click the blue **+ Add** button (top right) to record a new blotter entry." },
      { text: "• Use the **Search** box or **Filter** (funnel icon) to find specific dates or types." },
      { text: "• Review the table columns: Checkbox, **Blotter No.** (blue and clickable), Complainant, Respondent, Date, and Type of Incident." },
      { text: "• Click the blue **View** button under the \"Actions\" column to open the full report." },
      { text: "• Click the red outline **Trash Can Icon** to permanently delete the record." },
    ],
  },
  {
    id: "residents",
    icon: UserGroupIcon,
    color: "emerald",
    title: "Residents Information",
    summary: "Register residents, manage profiles, and control RFID kiosk access.",
    img: imgPage12,
    sections: [
      { heading: "Accessing and Registering Residents" },
      { text: "• Click **Residents Information** under SYSTEM MANAGERS." },
      { text: "• Click the blue **Register** button to add a new resident." },
      { text: "• Fill out the form (fields with a red asterisk * are required): Basic Info, Demographics (Gender, Birthdate, Residency Start Date), Contact Information, and Address (Purok). Click **Save**." },
      { text: "• Use the **Search** box, **Filter** button, **Checkbox**, or **Trash** icon to manage the database list." },
      { heading: "Reading the Resident Table & Profiles", style: "margin-top: 1.5rem" },
      { text: "• Review table columns: Checkbox/#, Full Name, Phone Number, **RFID No.**, and Current Address." },
      { text: "• Check the **RFID No.** status: Inactive, Blue Clickable Number (Active), or N/A (Grey Text)." },
      { text: "• Click the blue **View** button (Actions column) to open a profile." },
      { text: "• Click the red outline **Trash Can** icon to remove a resident." },
      { text: "• Inside a profile, review the Summary Dashboard (Picture, Age, Residency, I.D. NO.)." },
      { text: "• Click **> Transaction History** or **> Blotter Records** at the bottom of the profile to expand and view interactions." },
      { text: "• Under the **RFID NO.** section, click the toggle switch to change kiosk access between \"Active\" and \"Inactive\". Click the blue **Save** button after any updates." },
    ],
  },
  {
    id: "faqs",
    icon: InformationCircleIcon,
    color: "blue",
    title: "FAQs Management",
    summary: "Add and edit FAQ questions displayed on the kiosk help screen.",
    img: imgPage13,
    sections: [
      { heading: "Adding and Editing Questions" },
      { text: "• Click **FAQs Management** under HELP & SUPPORT (blue question mark icon)." },
      { text: "• Click the blue **+ Add FAQ** button (top right) to create a new entry." },
      { text: "• Use the **Search** box, **Checkbox**, or **Trash Can** icon for bulk actions." },
      { text: "• Review the table for the **Question** column and **Answer** column." },
      { text: "• Click the orange **Pencil Icon** (Actions column) to edit the text." },
      { text: "• Click the red **Trash Can Icon** to delete the FAQ." },
    ],
  },
  {
    id: "contact-info",
    icon: ChatBubbleLeftRightIcon,
    color: "emerald",
    title: "Contact Information",
    summary: "Update emergency contacts, office hours, and kiosk support details.",
    img: imgPage14,
    sections: [
      { heading: "Updating Kiosk Contact Details" },
      { text: "• Click **Contact Information** under HELP & SUPPORT." },
      { text: "• Update **Emergency Contacts**: Type the Number and Description (e.g., 911, \"For emergencies\")." },
      { text: "• Update **Barangay Office**: Type the Phone Number, Email Address, and Office Hours." },
      { text: "• Update **Visit Us**: Type the Physical Address." },
      { text: "• Update **Technical Support Prompt**: Type instructions in the Support Description box." },
      { text: "• Click the blue **Save Changes** button. This step is **mandatory** to push updates to the public kiosk." },
    ],
  },
  {
    id: "sms",
    icon: BellAlertIcon,
    color: "cyan",
    title: "SMS Announcements (Text Blasts)",
    summary: "Send targeted SMS messages to resident groups, puroks, or specific numbers.",
    img: imgPage15,
    sections: [
      { heading: "Step 1: Choose Recipients" },
      { text: "• Look at the **Recipients** box and check the selected counter at the top right." },
      { text: "• Click the **GROUPS** tab (blue when active) to select demographics (Female, Male, 18+, Youth, Senior Citizens, With RFID)." },
      { text: "• Click the **BY PUROK** tab for specific neighborhoods." },
      { text: "• Click the **SPECIFIC NUMBERS** tab to type individual phone numbers manually." },
      { heading: "Step 2: Compose Message", style: "margin-top: 1.5rem" },
      { text: "• Click the **Compose Message** box and type your text. Monitor the character counter (0/500) and SMS PAGE indicator." },
      { text: "• Alternatively, select a predefined category from the right sidebar **Templates** (Blue Assembly, Light Blue Water, Red Emergency, Green Health, Orange Document, Purple Event)." },
      { text: "• Always replace bracketed details like **[DATE]** with actual information." },
      { heading: "Step 3: Send", style: "margin-top: 1.5rem" },
      { text: "• Review the large **Send** button at the bottom (shows recipient count)." },
      { text: "• Check the **Recent Sends** box (bottom right) for past history." },
      { text: "⚠️ Click **Send** only when completely ready. **Text blasts cannot be undone.**" },
    ],
  },
  {
    id: "notifications",
    icon: BellAlertIcon,
    color: "blue",
    title: "Notifications",
    summary: "Access, filter, and manage all system alert notifications.",
    img: imgPage16,
    sections: [
      { heading: "Accessing Your Alerts" },
      { text: "• Click the **Bell Icon** on the top right navigation bar to open the **Notifications** module." },
      { text: "• Check the counter above the right side of the table to view your total alerts at a glance." },
      { heading: "Searching and Filtering", style: "margin-top: 1.5rem" },
      { text: "• Click the **Search** text box at the top right to quickly find specific alerts by keyword or resident name." },
      { text: "• Click the **Filter** button next to the search bar to narrow down your alerts." },
      { heading: "Using Bulk Action Tools", style: "margin-top: 1.5rem" },
      { text: "• Click the blue **Envelope Icon** to mark selected notifications as read." },
      { text: "• Click the red **Trash Bin Icon** to permanently delete the selected notifications." },
      { text: "• Click the **Checkbox Icon** to instantly select or deselect all items on the page." },
      { heading: "Reviewing the Notifications Table", style: "margin-top: 1.5rem" },
      { text: "• **Checkbox:** Click the individual box next to any row to select a specific alert." },
      { text: "• **Type:** Look at the colored badges to quickly identify the category — **Feedback**, **Equipment**, or **Document**." },
      { text: "• **Notification:** Read the main text for a detailed description of the event." },
      { text: "• **Date & Time:** Check the exact date and time the system generated the alert." },
    ],
  },
  {
    id: "settings-general",
    icon: Cog6ToothIcon,
    color: "orange",
    title: "System Settings",
    summary: "General, Security, Backup, and Preferences.",
    sections: [
      { heading: "Accessing System Settings" },
      { text: "1. Click the **gear icon** at the top right of your dashboard." },
      { text: "2. Select from the five main tabs: **General**, **Security**, **Backup Data**, **Preferences**, and **Audit Log**." },
      {img: imgPage18 },
      { heading: "General Tab — Updating Basic Identity" },
      { text: "1. Click the **Upload Logo** button to change the official barangay seal (accepts JPG, PNG, WebP, or SVG formats, maximum 2MB)." },
      { text: "2. Click the **Brgy. Name** field and type the official barangay name." },
      { text: "3. Click the **Subtitle / Municipality** field and type the location (e.g., Amadeo, Cavite). This information will appear directly on **printed documents and the public kiosk**." },
      { text: "4. Click the blue **Save Changes** button to apply your updates." },
      {img: imgPage19 },
      { heading: "Security Tab — Managing Access Rules" },
      { text: "1. To set Brgy. ID (RFID) Expiration, type the number of months in the **Validity Period** box." },
      { text: "2. Type the number of days in the **Expiry Reminder** box to determine when residents get notified." },
      { text: "3. Toggle the **Auto-Logout** switch to automatically log out inactive users. Set your desired timer using the minutes and seconds fields." },
      { text: "4. Toggle the **Failed Login Lockout** switch to block RFID access after too many incorrect PIN entries." },
      { text: "5. Set the **Max Failed Attempts** and define the **Lockout Duration** (in minutes)." },
      { text: "6. Click the blue **Save Settings** button, or click **Reset to Defaults** if you need to start over." },
      {img: imgPage20 },
      { heading: "Backup Data Tab" },
      { text: "1. Toggle the **Automatic Backup** switch to schedule regular system backups." },
      { text: "2. Set the **Frequency** (e.g., Daily) and choose the specific **Time** (e.g., 02:00 AM), then click **Save Settings**." },
      { text: "3. For an immediate backup, click the blue **Run Backup Now** button to create an on-demand data download straight to your computer." },
      { text: "4. Scroll down to the **Backup History** section to view a complete log of all past backups." },
      {img: imgPage21 },
      { heading: "Preferences Tab — Customizing Views & Availability" },
      { text: "1. Use the **Landing Page** dropdown to choose your default view upon logging in, then click **Save Preference**." },
      { text: "2. To pause resident transactions on the kiosk, toggle the **Maintenance Mode** switch. When turned on, the green status bar (\"System is LIVE\") will change to indicate the kiosk is offline." },
      { text: "3. Edit the **Kiosk Maintenance Message** to inform residents why the kiosk is down, and click **Save Message**." },
      { text: "4. To manage system storage, check the boxes for **Audit Logs** and/or **System Logs** under the Clear Logs section." },
      { text: "5. Set how old records must be to be deleted (e.g., older than 90 days)." },
      { text: "6. Click the red **Clear Selected Logs** button. ⚠️ **Warning: This action is permanent and cannot be undone.**" },
      {img: imgPage22 },
      { heading: "Audit Log Tab — Tracking System Activity" },
      { text: "1. Review the read-only table to track all system activity, organized by **DATE & TIME**, **ACTION**, and **DETAILS**." },
      { text: "2. Click the **Search audit logs...** bar in the top right and type keywords to easily find specific events or actions." },
    ],
  },
  {
    id: "account-settings",
    icon: UserCircleIcon,
    color: "violet",
    title: "Account Settings",
    summary: "Update your profile, change your password, and manage account security.",
    img: imgPage23,
    sections: [
      { heading: "Accessing Your Profile" },
      { text: "• Click your **profile block** at the top right corner of the navigation bar." },
      { text: "• Select **Account Settings** from the dropdown menu. You can also select **Log Out** from this menu to securely exit the dashboard." },
      { heading: "Updating the Profile Tab", style: "margin-top: 1.5rem" },
      { text: "• **Upload Photo:** Click the blue **Upload Photo** button to add or change your profile picture (accepts JPG, PNG, or WebP formats, maximum 2 MB)." },
      { text: "• **Personal Information:** Type your complete name in the **Full Name** text box and your official role in the **Position** text box." },
      { text: "• **Account Details:** Update your login identifier in the **Username** text box." },
      { text: "• **Save Updates:** Click the blue **Save Changes** button to apply your modifications." },
      {img: imgPage24 },
      { heading: "Managing the Security Tab", style: "margin-top: 1.5rem" },
      { text: "• Click the **Security** tab next to Profile to manage your login credentials and account status." },
      { text: "• **Change Password:** Type your active password in the **Current Password** field. Enter your desired new password into the **New Password** and **Confirm New Password** fields." },
      { text: "• Click the blue **Update Password** button to finalize your new login credentials." },
      { text: "• **Danger Zone (Delete Account):** Locate the red warning box to permanently remove your profile. ⚠️ **This action deletes all associated data and cannot be undone.**" },
    ],
  },
];

const tips = [
  { title: "Mark as Paid First",        text: "Approval for both document and equipment requests is disabled until the request is marked as paid. Always collect payment before approving." },
  { title: "Verify SMS Before Sending", text: "SMS blasts cannot be undone. Always double-check the recipient count and message content — especially bracketed placeholders like [DATE] — before clicking Send." },
  { title: "Keep Templates Uploaded",   text: "Document types without an uploaded .docx template show a No Template warning. Upload a template to enable document generation and printing." },
  { title: "RFID Must Be Active",       text: "After registering a resident, set their RFID status to Active in their profile. Inactive or unregistered cards are rejected at the kiosk tap." },
  { title: "Backup Regularly",          text: "Use Run Backup Now or schedule automatic backups. The system has no cloud backup — all data is stored locally on the Raspberry Pi." },
  { title: "Monitor Audit Logs",        text: "Review the Audit Log under System Settings daily to catch unauthorized actions or configuration changes early." },
];

// Helper: parse **bold** markers into segments
function parseText(text) {
  const parts = [];
  const re = /\*\*(.+?)\*\*/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push({ bold: false, v: text.slice(last, m.index) });
    parts.push({ bold: true, v: m[1] });
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push({ bold: false, v: text.slice(last) });
  return parts;
}
</script>

<template>
  <div class="guide-root">

    <!-- Hero -->
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
          <span class="gbadge"><span class="gbadge-dot"></span>Admin Reference</span>
          <span class="gbadge gbadge-outline">Dashboard Only</span>
          <span class="gbadge gbadge-outline">{{ guideModules.length }} Modules</span>
        </div>
        <h1 class="guide-hero-title">Admin User <span class="guide-hero-accent">Guide</span></h1>
        <p class="guide-hero-sub">Complete reference for operating the Barangay Kiosk Admin Dashboard</p>
      </div>
    </div>

    <!-- Warning -->
    <div class="warn-banner section-row" style="animation-delay:0.07s">
      <div class="warn-icon-wrap"><ExclamationTriangleIcon class="warn-icon" /></div>
      <div>
        <p class="warn-title">Admin Dashboard Documentation Only</p>
        <p class="warn-body">
          This guide covers this admin dashboard only. For hardware setup, kiosk physical
          installation, and network configuration, refer to the separate
          <strong>Hardware &amp; Deployment Manual</strong> provided with the project deliverables.
        </p>
      </div>
    </div>

    <!-- Stats -->
    <div class="guide-stats section-row" style="animation-delay:0.12s">
      <div v-for="s in [
        { value: guideModules.length, label: 'Guide Modules'   },
        { value: tips.length,         label: 'Quick Tips'      },
        { value: '2',                 label: 'SMS Channels'    },
        { value: '100%',              label: 'Offline Capable' },
      ]" :key="s.label" class="gstat-item">
        <div class="gstat-value">{{ s.value }}</div>
        <div class="gstat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- Module Accordion -->
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
        :style="`animation-delay:${0.2 + i * 0.035}s`"
      >
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

        <Transition name="accordion">
          <div v-if="openGuideItems.has(mod.id)" class="mod-body">
            <div class="mod-divider"></div>
            <div class="mod-content-wrap">

              <!-- Hero screenshot for the module -->
              <div v-if="mod.img" class="mod-screenshot-wrap">
                <img :src="mod.img" :alt="mod.title + ' screenshot'" class="mod-screenshot" />
              </div>

              <!-- Sections -->
              <div v-for="(sec, si) in mod.sections" :key="si">
                <!-- subheading -->
                <div v-if="sec.heading" class="mod-subheading" :style="sec.style">{{ sec.heading }}</div>
                <!-- inline image within sections -->
                <div v-if="sec.img" class="mod-screenshot-wrap mod-screenshot-wrap--inline">
                  <img :src="sec.img" :alt="'screenshot'" class="mod-screenshot" />
                </div>
                <!-- text with bold -->
                <p v-if="sec.text" class="mod-para">
                  <template v-for="(part, pi) in parseText(sec.text)" :key="pi">
                    <strong v-if="part.bold">{{ part.v }}</strong>
                    <span v-else>{{ part.v }}</span>
                  </template>
                </p>
              </div>

            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Quick Tips -->
    <div class="tips-card section-row" style="animation-delay:0.6s">
      <div class="tips-header">
        <div class="card-icon-wrap icon-amber"><LightBulbIcon class="card-icon" /></div>
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
.guide-root {
  display: flex; flex-direction: column; gap: 20px;
  width: 100%; box-sizing: border-box; padding-bottom: 2rem;
}
.section-row { opacity: 0; animation: riseUp 0.55s cubic-bezier(0.16,1,0.3,1) forwards; }
@keyframes riseUp {
  from { opacity:0; transform:translateY(28px); }
  to   { opacity:1; transform:translateY(0); }
}

/* Hero */
.guide-hero {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #1d4ed8 75%, #2563eb 100%);
  border-radius: 20px; padding: 48px 52px 44px; color: #fff;
  isolation: isolate; width: 100%; box-sizing: border-box;
}
@media (max-width: 768px) { .guide-hero { padding: 32px 24px 28px; } }
.guide-hero-rings { position:absolute; inset:0; pointer-events:none; }
.gring { position:absolute; border-radius:50%; border:1.5px solid rgba(255,255,255,0.1); right:-80px; top:-80px; animation:ringPulse 7s ease-in-out infinite; }
.gring-1 { width:240px; height:240px; animation-delay:0s; }
.gring-2 { width:420px; height:420px; animation-delay:1s; }
.gring-3 { width:600px; height:600px; animation-delay:2s; }
@keyframes ringPulse { 0%,100%{opacity:0.1;} 50%{opacity:0.25;} }
.glow-orb { position:absolute; right:-20px; top:-20px; width:260px; height:260px; background:radial-gradient(circle,rgba(96,165,250,0.2) 0%,transparent 70%); border-radius:50%; }
.guide-hero-grid { position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,0.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.035) 1px,transparent 1px); background-size:40px 40px; pointer-events:none; }
.guide-hero-content { position:relative; z-index:2; }
.guide-hero-badges { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:22px; }
.gbadge { display:inline-flex; align-items:center; gap:7px; background:rgba(255,255,255,0.14); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,0.2); color:#fff; font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; padding:5px 14px; border-radius:100px; }
.gbadge-outline { background:transparent; border-color:rgba(255,255,255,0.28); }
.gbadge-dot { width:7px; height:7px; background:#4ade80; border-radius:50%; box-shadow:0 0 0 3px rgba(74,222,128,0.3); animation:blip 1.8s ease-in-out infinite; }
@keyframes blip { 0%,100%{box-shadow:0 0 0 3px rgba(74,222,128,0.3);} 50%{box-shadow:0 0 0 6px rgba(74,222,128,0.1);} }
.guide-hero-title { font-size:clamp(1.8rem,3.5vw,2.9rem); font-weight:900; line-height:1.12; letter-spacing:-0.02em; margin:0 0 10px; text-shadow:0 2px 20px rgba(0,0,0,0.25); }
.guide-hero-accent { background:linear-gradient(90deg,#93c5fd,#e0f2fe); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.guide-hero-sub { font-size:1rem; font-weight:500; color:rgba(255,255,255,0.65); margin:0; max-width:560px; line-height:1.6; }

/* Warning */
.warn-banner { display:flex; align-items:flex-start; gap:14px; background:linear-gradient(135deg,#fffbeb,#fef3c7); border:1px solid #fde68a; border-radius:16px; padding:18px 22px; width:100%; box-sizing:border-box; }
.warn-icon-wrap { width:36px; height:36px; border-radius:10px; background:#fef3c7; border:1px solid #fde68a; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.warn-icon { width:18px; height:18px; color:#d97706; }
.warn-title { font-size:0.9rem; font-weight:800; color:#92400e; margin-bottom:4px; }
.warn-body { font-size:0.83rem; color:#78350f; line-height:1.6; margin:0; }

/* Stats */
.guide-stats { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:#e2e8f0; border:1px solid #e2e8f0; border-radius:16px; overflow:hidden; width:100%; box-sizing:border-box; }
@media (max-width:640px) { .guide-stats { grid-template-columns:repeat(2,1fr); } }
.gstat-item { background:#fff; padding:20px; text-align:center; transition:background 0.2s; }
.gstat-item:hover { background:#f8fafc; }
.gstat-value { font-size:1.9rem; font-weight:900; color:#1e40af; letter-spacing:-0.03em; line-height:1; margin-bottom:5px; }
.gstat-label { font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.08em; }

/* Module list */
.modules-list { background:#fff; border:1px solid #e2e8f0; border-radius:18px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.04); width:100%; box-sizing:border-box; }
.modules-header { padding:24px 28px 20px; border-bottom:1px solid #f1f5f9; background:linear-gradient(to right,#f8fafc,#fff); }
.modules-title { font-size:1.05rem; font-weight:800; color:#0f172a; margin:0 0 4px; letter-spacing:-0.01em; }
.modules-sub { font-size:0.82rem; color:#94a3b8; margin:0; font-weight:500; }

/* Module card */
.mod-card { border-bottom:1px solid #f1f5f9; opacity:0; animation:riseUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards; transition:background 0.2s; }
.mod-card:last-child { border-bottom:none; }
.mod-card--open { background:#fafbff; }
.mod-trigger { width:100%; display:flex; align-items:center; justify-content:space-between; padding:16px 24px; gap:16px; background:transparent; border:none; cursor:pointer; text-align:left; transition:background 0.18s; }
.mod-trigger:hover { background:#f8fafc; }
.mod-left { display:flex; align-items:center; gap:14px; flex:1; min-width:0; }
.mod-icon-wrap { width:40px; height:40px; border-radius:11px; display:flex; align-items:center; justify-content:center; flex-shrink:0; transition:transform 0.2s; }
.mod-trigger:hover .mod-icon-wrap { transform:scale(1.08); }
.mod-icon { width:20px; height:20px; }
.mod-icon--blue    { background:#eff6ff; border:1px solid #bfdbfe; } .mod-icon--blue    .mod-icon { color:#2563eb; }
.mod-icon--emerald { background:#ecfdf5; border:1px solid #a7f3d0; } .mod-icon--emerald .mod-icon { color:#059669; }
.mod-icon--violet  { background:#f5f3ff; border:1px solid #ddd6fe; } .mod-icon--violet  .mod-icon { color:#7c3aed; }
.mod-icon--amber   { background:#fffbeb; border:1px solid #fde68a; } .mod-icon--amber   .mod-icon { color:#d97706; }
.mod-icon--rose    { background:#fff1f2; border:1px solid #fecdd3; } .mod-icon--rose    .mod-icon { color:#e11d48; }
.mod-icon--cyan    { background:#ecfeff; border:1px solid #a5f3fc; } .mod-icon--cyan    .mod-icon { color:#0891b2; }
.mod-icon--orange  { background:#fff7ed; border:1px solid #fed7aa; } .mod-icon--orange  .mod-icon { color:#ea580c; }
.mod-icon--teal    { background:#f0fdfa; border:1px solid #99f6e4; } .mod-icon--teal    .mod-icon { color:#0d9488; }
.mod-meta { flex:1; min-width:0; }
.mod-index { font-size:10px; font-weight:800; color:#94a3b8; letter-spacing:0.1em; margin-bottom:2px; }
.mod-title { font-size:0.92rem; font-weight:800; color:#0f172a; margin-bottom:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mod-summary { font-size:0.78rem; color:#64748b; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mod-chevron { width:28px; height:28px; border-radius:8px; border:1px solid #e2e8f0; background:#f8fafc; display:flex; align-items:center; justify-content:center; flex-shrink:0; color:#94a3b8; transition:transform 0.25s cubic-bezier(0.16,1,0.3,1),background 0.2s,border-color 0.2s,color 0.2s; }
.mod-chevron--open { transform:rotate(180deg); background:#eff6ff; border-color:#bfdbfe; color:#2563eb; }

/* Accordion body */
.mod-body { overflow:hidden; }
.mod-divider { height:1px; background:linear-gradient(to right,#e2e8f0,transparent); margin:0 24px; }
.mod-content-wrap { padding:20px 28px 24px; }

/* Screenshot — hero (first image per module, no top margin needed) */
.mod-screenshot-wrap {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

/* Screenshot — inline within sections (adds one line of breathing room above) */
.mod-screenshot-wrap--inline {
  margin-top: 1lh;   /* one line-height of space above every inline image */
  margin-bottom: 20px;
}

.mod-screenshot {
  width: 100%;
  display: block;
  border-radius: 12px;
}

/* Subheading */
.mod-subheading {
  font-size: 0.82rem;
  font-weight: 800;
  color: #1e40af;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin: 18px 0 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e2e8f0;
}
.mod-subheading:first-child { margin-top: 0; }

/* Para */
.mod-para {
  font-size: 0.87rem;
  color: #475569;
  line-height: 1.72;
  margin: 0 0 6px;
}
.mod-para strong { color: #0f172a; font-weight: 700; }

/* Accordion transition */
.accordion-enter-active, .accordion-leave-active { transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.16,1,0.3,1); }
.accordion-enter-from, .accordion-leave-to { opacity:0; transform:translateY(-6px); }

/* Tips */
.tips-card { background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:28px 32px 32px; box-shadow:0 1px 3px rgba(0,0,0,0.04); transition:box-shadow 0.3s; width:100%; box-sizing:border-box; }
.tips-card:hover { box-shadow:0 8px 32px rgba(0,0,0,0.07); }
.tips-header { display:flex; align-items:flex-start; gap:14px; margin-bottom:24px; padding-bottom:20px; border-bottom:1px solid #f1f5f9; }
.card-icon-wrap { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.icon-amber { background:#fffbeb; border:1px solid #fde68a; }
.card-icon { width:22px; height:22px; color:#d97706; }
.tips-title { font-size:1rem; font-weight:800; color:#0f172a; margin:0 0 4px; letter-spacing:-0.01em; }
.tips-sub { font-size:0.8rem; color:#94a3b8; margin:0; font-weight:500; }
.tips-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
@media (max-width:1024px) { .tips-grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:640px)  { .tips-grid { grid-template-columns:1fr; } }
.tip-item { position:relative; background:linear-gradient(135deg,#f8fafc,#f1f5f9); border:1px solid #e2e8f0; border-radius:12px; padding:18px 18px 16px; opacity:0; animation:riseUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards; transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s; overflow:hidden; }
.tip-item::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#2563eb,#60a5fa); border-radius:12px 12px 0 0; opacity:0; transition:opacity 0.2s; }
.tip-item:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(37,99,235,0.1); border-color:#bfdbfe; }
.tip-item:hover::before { opacity:1; }
.tip-num { font-size:10px; font-weight:900; color:#94a3b8; letter-spacing:0.1em; margin-bottom:6px; }
.tip-title { font-size:0.85rem; font-weight:800; color:#1e40af; margin-bottom:6px; }
.tip-text { font-size:0.79rem; color:#475569; line-height:1.6; }
</style>