"""
================================================================================
File: main.py
Description:
    This is the main entry point for the Kiosk Backend API built with FastAPI.
    It initializes the FastAPI application, configures CORS middleware for 
    frontend communication, and registers all API routers that handle different 
    system features.

    The included routers manage:
      • Resident and RFID record operations
      • Authentication for barangay staff
      • User PIN management
      • Request type and document template management

    The root endpoint ("/") provides a simple status message to verify that
    the backend service is running correctly.
================================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents_table, rfid_uid, resident_routes, users, admin_auth, request_types, templates, requests
from routers import equipment

app = FastAPI(title="Kiosk Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:8080",
        # "http://localhost:8081",
        # "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Router Registration
# ==============================================================================
app.include_router(residents_table.router)
app.include_router(rfid_uid.router)
app.include_router(resident_routes.router)
app.include_router(users.router)
app.include_router(admin_auth.router)
app.include_router(request_types.router)
app.include_router(templates.router)
app.include_router(equipment.router)
app.include_router(requests.router)

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}