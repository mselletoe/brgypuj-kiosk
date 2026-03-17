import httpx
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()

@router.get("/camera/snapshot")
async def get_snapshot():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8085/?action=snapshot")
    return Response(content=response.content, media_type="image/jpeg")