# 🏛️ RFID-enabled Barangay Transaction Kiosk with SMS Notification System

An RFID-Based Barangay Service Delivery and Management System that automates resident transactions and communication, ensuring high functional suitability and accessibility even in offline environments.

---
## 🏗️ System Architecture
- **Kiosk Interface:** A lightweight Vue 3 application optimized for Raspberry Pi Chromium (Kiosk Mode), providing a seamless touch-screen experience for residents.
- **Admin Dashboard:** A Vue 3 Management UI for Barangay staff to oversee requests, inventory, and resident records.
- **Backend API:** A FastAPI (Python) REST API serving as the central orchestration layer.
- **Database:** PostgreSQL for relational data integrity, storing resident profiles, transaction logs, and system configurations.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (15+)
- Hardware: RFID Reader & Raspberry Pi

### 1. Clone the Repository
```bash
git clone https://github.com/mselletoe/brgypuj-kiosk.git
cd brgypuj-kiosk
```

### 2. Install Frontend Dependencies
```bash
cd admin-dashboard
npm install
npm run dev
```
```bash
cd kiosk-interface
npm install
npm run dev
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# Configure .env file
uvicorn app.main:app --reload
```



## 📝 Notes

### Commit and Push
```bash
git add .
git commit -m "Desc"
git push
```

### REMINDER: Always move to the parent folder before committing.

### Create Branch
```bash
git checkout -b branchname

for sure after first push using bagong branch lalabas to:
git push --set-upstream origin branchname
```

### AFTER CREATING BRANCH AND BEFORE PUSHING COMMITS
```bash
git pull origin main
```

### Switch Branch
```bash
git checkout branchname
```

### Use PascalCase
```bash
SharedComponents.vue
DocumentTemplates.vue
```

### script first before template

### Move up one directory level
```bash
cd ..

Ex. From /home/user/Documents/Projects
cd ..
You'll end up to /home/user/Documents
```
