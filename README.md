# 🏛️ Barangay Poblacion Uno Jasmin Kiosk System

A kiosk and admin dashboard system designed for use on a Raspberry Pi (kiosk side) and external PCs (admin side).

---
## 🏗️ System Architecture
- **Kiosk Interface:** Full-screen Vue 3 app running on Raspberry Pi Chromium (Kiosk Mode).
- **Admin Dashboard:** Management UI for Barangay staff.
- **Backend API:** FastAPI (Python) acting as the bridge between UIs and Database.
- **Database:** PostgreSQL storing resident data, requests, and inventory.

## ✅ Tech Stack
- **Frontend:** Vue 3, Vite, TailwindCSS, NaiveUI
- **Backend:** FastAPI (Python), SQLAlchemy/Psycopg2
- **Database:** PostgreSQL
- **Deployment:** Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (15+)
- Docker (Optional)

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