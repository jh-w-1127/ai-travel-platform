"""Chat API — SSE streaming endpoint for AI travel planning"""

import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.llm.engine import chat_with_tools

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    SSE streaming chat for AI itinerary planning.
    
    Events:
      - message: text chunk from the AI
      - function_call: AI is calling a tool
      - function_result: tool execution result
      - itinerary: final itinerary JSON
      - done: conversation complete
      - error: something went wrong
    """
    async def event_stream():
        async for event in chat_with_tools(
            messages=req.messages,
            track=req.track,
        ):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
