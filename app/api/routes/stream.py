import asyncio
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.utils.metrics import metrics_client

router = APIRouter(prefix="/stream", tags=["SSE"])


async def event_generator(device_ids: list[str], request: Request):
    # Incrementar conexiones activas al iniciar
    await metrics_client.increment_active_connections()

    try:
        while True:
            # Verificar si el cliente se ha desconectado
            if await request.is_disconnected():
                break

            # Aquí conectarías con el sistema en tiempo real (Kafka, Redis, etc.)
            # Simulación temporal:
            await asyncio.sleep(2)
            yield {
                "event": "update",
                "data": json.dumps(
                    {"device_id": device_ids[0], "lat": 19.4326, "lon": -99.1332}
                ),
            }
    finally:
        # Decrementar conexiones activas al desconectar
        await metrics_client.decrement_active_connections()


@router.get("/")
async def stream(device_ids: list[str], request: Request):
    generator = event_generator(device_ids, request)
    return EventSourceResponse(generator)
