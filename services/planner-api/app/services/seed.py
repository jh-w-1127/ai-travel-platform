"""Seed Chongqing data on startup"""

from app.services.poi_store import get_store


async def seed_chongqing_pois() -> int:
    store = get_store()
    count = await store.seed()
    print(f"[Seed] Loaded {count} Chongqing POIs")
    return count
