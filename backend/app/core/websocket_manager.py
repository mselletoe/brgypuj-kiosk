from typing import List
from fastapi import WebSocket
from sqlalchemy.orm import Session
import json

class WebSocketManager:
    def __init__(self):
        self.admin_connections: List[WebSocket] = []
        self.kiosk_connections: List[WebSocket] = []

    async def connect_admin(self, websocket: WebSocket):
        await websocket.accept()
        self.admin_connections.append(websocket)

    async def connect_kiosk(self, websocket: WebSocket):
        await websocket.accept()
        self.kiosk_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
        if websocket in self.kiosk_connections:
            self.kiosk_connections.remove(websocket)

    async def broadcast_to_admin(self, event: str, data: dict, db: Session = None):  # 👈 db added
        """Save to DB first, then broadcast to all connected admin clients."""

        # ── Persist to database ───────────────────────────────────────────────
        if db:
            from app.services.notification_service import save_notification
            type_map = {
                "new_transaction":    "Document",
                "new_equipment_request": "Equipment",
                "new_feedback":       "Feedback",
                "new_id_application": "Document",
                "new_lost_card_report": "Document",
                "new_rfid_linked":    "Document",
            }
            msg_map = {
                "new_transaction":       f"New {data.get('document_type', 'Document')} request submitted by {data.get('resident_name', 'a resident')}",
                "new_equipment_request": f"New Equipment request submitted by {data.get('resident_name', 'a resident')}",
                "new_feedback":          f"New feedback received — rated {data.get('rating', '?')}/5 stars" if data.get('rating') else "New feedback received from a resident",
                "new_id_application":    f"New ID Application submitted by {data.get('resident_name', 'a resident')}",
                "new_lost_card_report":  f"Lost card reported by {data.get('resident_name', 'a resident')}",
                "new_rfid_linked":       f"New RFID card linked for {data.get('resident_name', 'a resident')}",
            }
            notif = save_notification(
                db,
                type=type_map.get(event, "Document"),
                msg=msg_map.get(event, "New notification"),
            )
            # Include DB id in the broadcast so frontend can track it
            data["db_id"] = notif.id
            data["created_at"] = notif.created_at.isoformat()

        # ── Broadcast to connected clients ────────────────────────────────────
        message = json.dumps({"event": event, "data": data})
        for connection in self.admin_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

    async def broadcast_to_kiosk(self, event: str, data: dict):
        message = json.dumps({"event": event, "data": data})
        for connection in self.kiosk_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

    async def broadcast_to_all(self, event: str, data: dict):
        await self.broadcast_to_admin(event, data)
        await self.broadcast_to_kiosk(event, data)

ws_manager = WebSocketManager()