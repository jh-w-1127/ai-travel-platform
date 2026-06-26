"""Itinerary API — retrieve and manage trip plans"""

from fastapi import APIRouter, HTTPException
from app.services.poi_store import get_store

router = APIRouter()


@router.get("/itinerary/generate")
async def generate_itinerary(
    days: int = 3,
    track: str = "budget",
    preferences: str = "",
):
    """Quick generate a structured itinerary without chat flow"""
    store = get_store()
    return await store.generate_itinerary_struct(
        days=days,
        track=track,
        preferences=preferences,
    )


@router.get("/price-estimate")
async def price_estimate(
    track: str = "budget",
    days: int = 3,
):
    """Get price estimate for a trip"""
    store = get_store()
    return await store.calculate_price(
        items=[],
        track=track,
        days=days,
    )
