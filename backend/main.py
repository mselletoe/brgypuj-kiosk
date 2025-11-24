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
from contextlib import asynccontextmanager
from routers import (
    residents_table, rfid_uid, resident_routes, users, 
    admin_auth, request_types, templates, requests, sms,
    equipment, announcements
)
from services.sms_service import sms_service
from dotenv import load_dotenv
import logging
import os
from pathlib import Path

# ==============================================================================
# Load Environment Variables
# ==============================================================================
# Load backend/.env first (application config)
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Then try to load root .env (Docker config) - won't override existing vars
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=False)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'False').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==============================================================================
# Lifespan Context Manager - Handle Startup/Shutdown Events
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    - Startup: Connect to SIM800L module
    - Shutdown: Disconnect from SIM800L module
    """
    # ===== STARTUP =====
    logger.info("=" * 60)
    logger.info("Starting Kiosk Backend API")
    logger.info("=" * 60)
    
    # Log configuration (don't log sensitive values in production!)
    if os.getenv('DEBUG', 'False').lower() == 'true':
        logger.debug(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
        logger.debug(f"DEBUG: {os.getenv('DEBUG', 'False')}")
    
    # Initialize SIM800L
    logger.info("Initializing SIM800L module...")
    
    # Get port from environment variable or auto-detect
    configured_port = os.getenv('SIM800L_PORT')
    if configured_port:
        sms_service.port = configured_port
        logger.info(f"Using configured port: {configured_port}")
    else:
        logger.info("Auto-detecting serial port...")
    
    # Attempt connection
    try:
        if sms_service.connect():
            logger.info(f"✓ SIM800L connected successfully on {sms_service.port}")
            
            # Get signal quality
            signal = sms_service.get_signal_quality()
            if signal is not None:
                signal_bars = min(5, (signal // 6))
                logger.info(f"📶 Signal Quality: {signal}/31 ({'▮' * signal_bars}{'▯' * (5-signal_bars)})")
            else:
                logger.warning("⚠ Could not read signal quality")
        else:
            logger.warning("⚠ SIM800L connection failed - SMS features will be disabled")
            logger.warning("  Check: Serial port, power supply, SIM card, antenna")
    except Exception as e:
        logger.error(f"❌ Error initializing SIM800L: {e}")
        logger.warning("  SMS features will be disabled")
    
    logger.info("=" * 60)
    logger.info("Backend API Ready")
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # ===== SHUTDOWN =====
    logger.info("Shutting down Kiosk Backend API...")
    
    # Disconnect SIM800L
    try:
        sms_service.disconnect()
        logger.info("✓ SIM800L disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting SIM800L: {e}")
    
    logger.info("Shutdown complete")

# ==============================================================================
# FastAPI App Initialization
# ==============================================================================
app = FastAPI(
    title="Kiosk Backend API",
    lifespan=lifespan,
    version="1.0.0",
    description="Backend API for Barangay Kiosk System with SMS integration"
)

# ==============================================================================
# CORS Middleware
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:5173",  # Vue.js dev server
        # "http://localhost:8080",
        # "http://localhost:8081",
        "*"  # Remove in production, specify exact origins
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
app.include_router(announcements.router)
app.include_router(sms.router)

# ==============================================================================
# Root Endpoints
# ==============================================================================
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Kiosk backend is running",
        "version": "1.0.0",
        "sms_enabled": sms_service.is_connected
    }

@app.get("/health")
def health_check():
    """Detailed health check including SIM800L status"""
    health_status = {
        "status": "healthy",
        "api": "running",
        "database": {
            "configured": bool(os.getenv('DATABASE_URL'))
        },
        "sms_module": {
            "connected": sms_service.is_connected,
            "port": sms_service.port if sms_service.is_connected else None
        }
    }
    
    # Get signal quality if connected
    if sms_service.is_connected:
        try:
            signal = sms_service.get_signal_quality()
            if signal is not None:
                health_status["sms_module"]["signal_quality"] = signal
                health_status["sms_module"]["signal_bars"] = min(5, (signal // 6))
        except:
            pass
    
    return health_status