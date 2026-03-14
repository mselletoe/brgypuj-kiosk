import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.admin.routes import router as admin_router
from app.api.kiosk.routes import router as kiosk_router
from app.api.websocket import router as ws_router
from app.services.backup_service import start_scheduler, stop_scheduler

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="Barangay Kiosk Backend", lifespan=lifespan)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

if CORS_ORIGINS == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(kiosk_router, prefix="/kiosk", tags=["Kiosk"])
app.include_router(ws_router, tags=["WebSocket"])

@app.get("/")
def root():
    return {"message": "Backend is running"}