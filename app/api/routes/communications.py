import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db
from app.schemas.communications import (
    CommunicationLatestResponse,
    CommunicationResponse,
)
from app.services.repository import get_communications, get_latest_communications
from app.utils.metrics import metrics_client

router = APIRouter(prefix="/api/v1", tags=["Communications"])


# ============================================================================
# Endpoints de Comunicaciones - Histórico
# ============================================================================


@router.get("/communications", response_model=list[CommunicationResponse])
async def get_communications_history(  # noqa: B008
    device_ids: list[str] = Query(
        ...,
        description="Lista de IDs de dispositivos GPS a consultar",
        min_length=1,
        max_length=100,
        example=["867564050638581", "DEVICE123"],
    ),
    db=Depends(get_db),
):
    """
    Obtiene el histórico de comunicaciones de múltiples dispositivos GPS.

    **Método REST:** GET con query parameters

    **Query Parameters:**
    - `device_ids`: Lista de IDs de dispositivos (requerido, mínimo 1, máximo 100)

    **Ejemplo:**
    ```
    GET /api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123
    ```

    **Returns:**
    - Lista de comunicaciones de los dispositivos especificados
    """
    return await get_communications(db, device_ids)


@router.get(
    "/devices/{device_id}/communications", response_model=list[CommunicationResponse]
)
async def get_device_communications(
    device_id: str,
    db=Depends(get_db),
):
    """
    Obtiene el histórico de comunicaciones de UN solo dispositivo GPS.

    **Método REST:** GET con path parameter

    **Path Parameters:**
    - `device_id`: ID del dispositivo GPS

    **Ejemplo:**
    ```
    GET /api/v1/devices/867564050638581/communications
    ```

    **Returns:**
    - Lista de comunicaciones del dispositivo especificado
    """
    return await get_communications(db, [device_id])


# ============================================================================
# Endpoints de Comunicaciones - Estado Actual (Latest)
# ============================================================================


@router.get("/communications/latest", response_model=list[CommunicationLatestResponse])
async def get_latest_communications_endpoint(  # noqa: B008
    device_ids: list[str] = Query(
        ...,
        description="Lista de IDs de dispositivos GPS a consultar",
        min_length=1,
        max_length=100,
        example=["867564050638581", "DEVICE123"],
    ),
    db=Depends(get_db),
):
    """
    Obtiene la última comunicación registrada de múltiples dispositivos GPS.

    **Método REST:** GET con query parameters

    **Query Parameters:**
    - `device_ids`: Lista de IDs de dispositivos (requerido, mínimo 1, máximo 100)

    **Ejemplo:**
    ```
    GET /api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123
    ```

    **Diferencias:**
    - `GET /communications`: Retorna TODO el histórico de comunicaciones
    - `GET /communications/latest`: Retorna SOLO la última comunicación de cada dispositivo
    - `GET /communications/stream`: Conexión persistente con actualizaciones continuas (SSE)

    **Caso de uso:** Ideal para dashboards que necesitan mostrar la posición/estado
    actual de múltiples dispositivos sin cargar todo el histórico.

    **Returns:**
    - Lista con la última comunicación de cada dispositivo especificado
    """
    return await get_latest_communications(db, device_ids)


@router.get(
    "/devices/{device_id}/communications/latest",
    response_model=CommunicationLatestResponse,
)
async def get_device_latest_communication(
    device_id: str,
    db=Depends(get_db),
):
    """
    Obtiene la última comunicación de UN solo dispositivo GPS.

    **Método REST:** GET con path parameter

    **Path Parameters:**
    - `device_id`: ID del dispositivo GPS

    **Ejemplo:**
    ```
    GET /api/v1/devices/867564050638581/communications/latest
    ```

    **Diferencias:**
    - `GET /devices/{id}/communications`: Retorna TODO el histórico del dispositivo
    - `GET /devices/{id}/communications/latest`: Retorna SOLO la última comunicación
    - `GET /devices/{id}/communications/stream`: Stream en tiempo real del dispositivo

    **Caso de uso:** Ideal para consultar el estado actual de un dispositivo específico.

    **Returns:**
    - Última comunicación del dispositivo especificado
    - Error 404 si el dispositivo no existe o no tiene comunicaciones
    """
    result = await get_latest_communications(db, [device_id])

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró comunicación para el dispositivo {device_id}",
        )

    return result[0]


# ============================================================================
# Endpoints de Server-Sent Events (SSE) - Tiempo Real
# ============================================================================


async def event_generator(device_ids: list[str], request: Request):
    """
    Generador de eventos SSE para actualizaciones en tiempo real.

    En producción, esto se conectaría a Kafka, Redis Pub/Sub, o similar.
    """
    # Incrementar conexiones activas al iniciar
    await metrics_client.increment_active_connections()

    try:
        while True:
            # Verificar si el cliente se ha desconectado
            if await request.is_disconnected():
                break

            # TODO: Conectar con sistema de mensajería en tiempo real (Kafka, Redis, etc.)
            # Simulación temporal:
            await asyncio.sleep(2)
            for device_id in device_ids:
                yield {
                    "event": "update",
                    "data": json.dumps(
                        {
                            "device_id": device_id,
                            "latitude": 19.4326,
                            "longitude": -99.1332,
                            "speed": 45.5,
                            "timestamp": "2024-01-15T10:30:00",
                        }
                    ),
                }
    finally:
        # Decrementar conexiones activas al desconectar
        await metrics_client.decrement_active_connections()


@router.get("/communications/stream")
async def stream_communications(
    request: Request,
    device_ids: list[str] = Query(
        ...,
        description="Lista de IDs de dispositivos GPS a monitorear en tiempo real",
        min_length=1,
        max_length=50,
        example=["867564050638581", "DEVICE123"],
    ),
):
    """
    Suscripción SSE para recibir actualizaciones en tiempo real de múltiples dispositivos.

    **Método REST:** GET con Server-Sent Events (SSE)

    **Query Parameters:**
    - `device_ids`: Lista de IDs de dispositivos (requerido, mínimo 1, máximo 50)

    **Ejemplo:**
    ```
    GET /api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123
    ```

    **Headers requeridos:**
    - `Accept: text/event-stream`

    **Respuesta:** Stream continuo de eventos en formato SSE

    **Nota:** Este endpoint NO requiere autenticación JWT (ajustar según necesidad)
    """
    generator = event_generator(device_ids, request)
    return EventSourceResponse(generator)


@router.get("/devices/{device_id}/communications/stream")
async def stream_device_communications(
    device_id: str,
    request: Request,
):
    """
    Suscripción SSE para recibir actualizaciones en tiempo real de UN solo dispositivo.

    **Método REST:** GET con Server-Sent Events (SSE)

    **Path Parameters:**
    - `device_id`: ID del dispositivo GPS

    **Ejemplo:**
    ```
    GET /api/v1/devices/867564050638581/communications/stream
    ```

    **Headers requeridos:**
    - `Accept: text/event-stream`

    **Respuesta:** Stream continuo de eventos en formato SSE

    **Nota:** Este endpoint NO requiere autenticación JWT (ajustar según necesidad)
    """
    generator = event_generator([device_id], request)
    return EventSourceResponse(generator)
