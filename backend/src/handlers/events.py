"""Recurso /api/events — progresso em tempo real via SSE."""
import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.services.instance import queue

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("")
async def events():
    q = queue.subscribe()

    async def stream():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15)
                    if data is None:  # servidor encerrando
                        break
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            queue.unsubscribe(q)

    return StreamingResponse(stream(), media_type="text/event-stream")
