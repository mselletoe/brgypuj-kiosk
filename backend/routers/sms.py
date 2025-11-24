from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.sms_service import sms_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS"])

class SMSRequest(BaseModel):
    phone: str = Field(..., description="Recipient phone number")
    message: str = Field(..., max_length=500, description="SMS message")
    requestId: int = Field(None, description="Optional request ID for logging")

class SMSResponse(BaseModel):
    success: bool
    message: str
    requestId: int = None

class SMSStatusResponse(BaseModel):
    connected: bool
    port: str = None
    signal_quality: int = None
    signal_bars: int = None

@router.post("/send", response_model=SMSResponse)
async def send_sms(sms_data: SMSRequest):
    """Send SMS via SIM800L"""
    
    # Validate phone number format
    phone = sms_data.phone.strip()
    if not phone.startswith('+') and not phone.startswith('0'):
        phone = '+' + phone
    
    logger.info(f"API request to send SMS to {phone}")
    
    # Send SMS
    result = sms_service.send_sms(phone, sms_data.message)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return SMSResponse(
        success=True,
        message="SMS sent successfully",
        requestId=sms_data.requestId
    )

@router.get("/status", response_model=SMSStatusResponse)
async def get_sms_status():
    """Get SIM800L module status"""
    status = sms_service.get_status()
    
    return SMSStatusResponse(
        connected=status.get("connected", False),
        port=status.get("port"),
        signal_quality=status.get("signal_quality"),
        signal_bars=status.get("signal_bars", 0)
    )

@router.post("/reconnect")
async def reconnect_sim800l():
    """Reconnect to SIM800L module"""
    logger.info("Reconnecting to SIM800L...")
    
    sms_service.disconnect()
    
    if sms_service.connect():
        return {"success": True, "message": "Reconnected successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reconnect")