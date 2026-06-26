"""POI API — search and browse points of interest"""

from fastapi import APIRouter, HTTPException, Query
from app.services.poi_store import get_store

router = APIRouter()


@router.get("/pois")
async def list_pois(
    poi_type: str | None = Query(None, alias="type"),
    track: str = "both",
    limit: int = 20,
):
    """List all POIs with optional filters"""
    store = get_store()
    return await store.search_poi(
        query="",
        poi_type=poi_type,
        track=track,
        limit=limit,
    )


@router.get("/pois/{poi_id}")
async def poi_detail(poi_id: str):
    """Get a single POI with full details"""
    store = get_store()
    poi = await store.get_poi_detail(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return poi


@router.get("/transport")
async def transport(
    origin: str,
    destination: str,
    mode: str = "metro",
):
    """Get transport options between two locations"""
    store = get_store()
    return await store.get_transport(origin, destination, mode)
