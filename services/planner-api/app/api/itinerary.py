"""Itinerary API — retrieve and manage trip plans"""

import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.services.poi_store import get_store
from app.core.config import settings

router = APIRouter()


@router.get("/itinerary/generate")
async def generate_itinerary(
    days: int = 3,
    track: str = "budget",
    preferences: str = "",
):
    """Quick generate a structured itinerary using template engine"""
    store = get_store()
    return await store.generate_itinerary_struct(
        days=days,
        track=track,
        preferences=preferences,
    )


@router.post("/itinerary/ai-plan")
async def ai_itinerary_plan(
    days: int = Query(3),
    track: str = Query("budget"),
    preferences: str = Query(""),
):
    """AI-powered itinerary generation via SSE streaming.
    Falls back to template engine if LLM key is not configured."""
    
    store = get_store()
    
    # Check if LLM is available
    if settings.llm_api_key == "sk-placeholder" or not settings.llm_api_key:
        # Fall back to template engine
        async def fallback_stream():
            result = await store.generate_itinerary_struct(days=days, track=track, preferences=preferences)
            yield f"data: {json.dumps({'type':'itinerary','data':result}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(fallback_stream(), media_type="text/event-stream",
            headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"})
    
    # LLM-powered: use the chat engine with a structured prompt
    from app.llm.engine import chat_with_tools
    from app.models.schemas import ChatMessage
    
    track_label = "高端品质" if track == "premium" else "经济实惠"
    prompt = f"""请帮我规划一个重庆{days}天的{track_label}行程。

我的偏好：{preferences if preferences else '经典路线，喜欢美食和夜景'}

请先调用search_poi和search_hotel查找合适的景点和酒店，然后调用generate_itinerary生成最终行程。务必使用真实数据，不要编造。"""
    
    messages = [ChatMessage(role="user", content=prompt)]
    
    async def ai_stream():
        collected = ""
        async for event in chat_with_tools(messages=messages, track=track):
            if event["event"] in ("message", "function_call", "function_result"):
                yield f"data: {json.dumps({'type':event['event'],'data':event['data']}, ensure_ascii=False)}\n\n"
                if event["event"] == "message":
                    collected += event["data"].get("content", "")
            elif event["event"] == "done":
                # Try to extract itinerary from the response
                yield f"data: {json.dumps({'type':'done','data':{'status':'complete'}}, ensure_ascii=False)}\n\n"
            elif event["event"] == "error":
                # Error: fall back to template
                result = await store.generate_itinerary_struct(days=days, track=track, preferences=preferences)
                yield f"data: {json.dumps({'type':'itinerary','data':result}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(ai_stream(), media_type="text/event-stream",
        headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"})


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
