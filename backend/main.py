from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents_table, rfid_uid, resident_routes, users, admin_auth

app = FastAPI(title="Kiosk Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(residents_table.router)
app.include_router(rfid_uid.router)
app.include_router(resident_routes.router)
app.include_router(users.router)
app.include_router(admin_auth.router)

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}