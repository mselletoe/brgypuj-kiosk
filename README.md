# 🏛️ Barangay Poblacion Uno Jasmin Kiosk System

A kiosk and admin dashboard system built with **Vue 3**, **Vite**, **TailwindCSS + DaisyUI**, **FastAPI**, and **PostgreSQL**.  
Designed for use on a Raspberry Pi (kiosk side) and external PCs (admin side). The system manages resident data, requests, and announcements through a shared backend and database.

---

## ✅ Tech Stack

### Frontend (Both UIs)
- Vue 3 + Vite  
- TailwindCSS  
- DaisyUI  
- Vue Router  

### Backend
- FastAPI (Python)

### Database
- PostgreSQL

### Containerization
- Docker & Docker Compose

---

## 🚀 Getting Started (Development)

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
pip install -r requirements.txt
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
