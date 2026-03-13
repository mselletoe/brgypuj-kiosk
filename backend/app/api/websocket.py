from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager

router = APIRouter()

@router.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await ws_manager.connect_admin(websocket)
    try:
        while True:
            # Keep connection alive, listen for any client pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@router.websocket("/ws/kiosk")
async def kiosk_websocket(websocket: WebSocket):
    await ws_manager.connect_kiosk(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)