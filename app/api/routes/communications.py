from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.schemas.communications import (
    CommunicationLatestResponse,
    CommunicationResponse,
)
from app.services.repository import get_communications, get_latest_communications

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
async def get_device_latest_communication(  # noqa: B008
    device_id: str,
    class_: str = Query(
        "STATUS",
        alias="class",
        description="Filtro por tipo de clase de mensaje (ALERT o STATUS)",
        example="STATUS",
    ),
    db=Depends(get_db),
):
    """
    Obtiene la última comunicación de UN solo dispositivo GPS.

    **Método REST:** GET con path parameter

    **Path Parameters:**
    - `device_id`: ID del dispositivo GPS

    **Query Parameters:**
    - `class`: Tipo de clase de mensaje para filtrar (ALERT o STATUS). Default: STATUS

    **Ejemplos:**
    ```
    GET /api/v1/devices/867564050638581/communications/latest
    GET /api/v1/devices/867564050638581/communications/latest?class=STATUS
    GET /api/v1/devices/867564050638581/communications/latest?class=ALERT
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
    result = await get_latest_communications(db, [device_id], msg_class=class_)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró comunicación para el dispositivo {device_id}",
        )

    return result[0]
