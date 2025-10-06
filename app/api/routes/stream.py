import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/stream", tags=["SSE"])


async def event_generator(device_ids: list[str]):
    while True:
        # Aquí conectarías con el sistema en tiempo real (Kafka, Redis, etc.)
        # Simulación temporal:
        await asyncio.sleep(2)
        yield {
            "event": "update",
            "data": json.dumps(
                {"device_id": device_ids[0], "lat": 19.4326, "lon": -99.1332}
            ),
        }


@router.get("/")
async def stream(device_ids: list[str]):
    generator = event_generator(device_ids)
    return EventSourceResponse(generator)
