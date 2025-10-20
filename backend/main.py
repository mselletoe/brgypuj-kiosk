from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents_table, rfid_uid, resident_routes

app = FastAPI(title="Kiosk Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(residents_table.router)
app.include_router(rfid_uid.router)
app.include_router(resident_routes.router)

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}