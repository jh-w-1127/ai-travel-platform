"""Pydantic models for the planner service"""

from __future__ import annotations

from enum import Enum
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


# ── POI ──────────────────────────────────────────────

class POIType(str, Enum):
    attraction = "attraction"
    restaurant = "restaurant"
    hotel = "hotel"
    transport = "transport"
    experience = "experience"


class PriceTrack(str, Enum):
    premium = "premium"
    budget = "budget"
    both = "both"


class POI(BaseModel):
    id: str
    name_zh: str
    name_en: str
    city: str = "chongqing"
    type: POIType
    lat: float
    lng: float
    tags: List[str] = []
    description_zh: str = ""
    description_en: str = ""
    price_range: str = ""
    opening_hours: str = ""
    tips: List[str] = []
    best_photo_spot: str = ""
    track: PriceTrack = PriceTrack.both
    rating: float = 0.0


# ── Itinerary ────────────────────────────────────────

class ItineraryItem(BaseModel):
    time: str = ""
    poi_id: Optional[str] = None
    poi_name_zh: str = ""
    poi_name_en: str = ""
    activity: str = ""
    transport: str = ""
    duration: str = ""
    cost_estimate: str = ""
    tips: List[str] = []


class DayPlan(BaseModel):
    day: int
    date: str = ""
    title_zh: str = ""
    title_en: str = ""
    items: List[ItineraryItem] = []


class Itinerary(BaseModel):
    id: Optional[str] = None
    city: str = "chongqing"
    track: PriceTrack
    days: int = 3
    total_budget: str = ""
    plan: List[DayPlan] = []
    created_at: datetime = Field(default_factory=datetime.now)


# ── Chat ─────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    track: Optional[PriceTrack] = None


# ── SSE Event Types ──────────────────────────────────

class SSEEventType(str, Enum):
    message = "message"
    function_call = "function_call"
    function_result = "function_result"
    itinerary = "itinerary"
    done = "done"
    error = "error"


class SSEEvent(BaseModel):
    event: SSEEventType
    data: dict = {}
