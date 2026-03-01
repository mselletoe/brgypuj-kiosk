from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.admin.routes import router as admin_router
from app.api.kiosk.routes import router as kiosk_router

app = FastAPI(title="Barangay Kiosk Backend")

# Define specifically allowed origins
origins = [
    "http://localhost:8080",  # Your Admin Dashboard
    "http://127.0.0.1:8080",
    "http://localhost:5173",  # Vite default
]

# Add middleware ONLY ONCE
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(kiosk_router, prefix="/kiosk", tags=["Kiosk"])

@app.get("/")
def root():
    return {"message": "Backend is running"}