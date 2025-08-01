"""
Calendar router placeholder
"""
from fastapi import APIRouter

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/")
async def get_calendar():
    return {"message": "Calendar functionality"}