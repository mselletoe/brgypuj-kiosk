import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.sse_manager import sse_manager

router = APIRouter(prefix="/sse")

@router.get("/events")
async def kiosk_event_stream():
    queue = await sse_manager.connect()

    async def generator():
        try:
            while True:
                message = await queue.get()
                yield f"event: {message['event']}\ndata: {json.dumps(message['data'])}\n\n"
        except asyncio.CancelledError:
            sse_manager.disconnect(queue)

    return StreamingResponse(generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    })