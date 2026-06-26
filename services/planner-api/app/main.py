# Planner API — AI行程规划微服务
# 重庆 MVP 打样版

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import chat, itinerary, poi


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed Chongqing POIs into DB
    from app.services.seed import seed_chongqing_pois
    await seed_chongqing_pois()
    yield


app = FastAPI(
    title="AI Travel Planner API",
    version="0.1.0-mvp-chongqing",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/planner", tags=["Chat"])
app.include_router(itinerary.router, prefix="/api/planner", tags=["Itinerary"])
app.include_router(poi.router, prefix="/api/planner", tags=["POI"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "city": "chongqing", "version": "0.1.0-mvp"}
