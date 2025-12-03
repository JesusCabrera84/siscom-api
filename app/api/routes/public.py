"""
Rutas públicas para compartir ubicaciones de dispositivos GPS.

Este módulo proporciona endpoints públicos que no requieren autenticación JWT
pero usan tokens PASETO para autorización temporal.
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.core.database import SessionLocal
from app.services.repository import get_latest_communications
from app.utils.paseto_validator import ExpiredToken, InvalidToken, paseto_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/public/share-location", tags=["Public"])


@router.get("/init")
async def init_share_location(
    token: str = Query(..., description="Token PASETO para validar acceso")
):
    """
    Inicializa una sesión de compartición de ubicación validando el token PASETO.

    Este endpoint valida un token PASETO v4.local emitido por siscom-admin-api
    y retorna información sobre su validez y expiración.

    **Query Parameters:**
    - `token`: Token PASETO v4.local (requerido)

    **Ejemplo:**
    ```
    GET /api/v1/public/share-location/init?token=v4.local.xxx...
    ```

    **Responses:**
    - 200: Token válido
        ```json
        {
            "msg": "valid",
            "expires_at": "2024-12-31T23:59:59+00:00"
        }
        ```
    - 401: Token expirado
        ```json
        {
            "detail": "Token expired"
        }
        ```
    - 403: Token inválido
        ```json
        {
            "detail": "Invalid token"
        }
        ```

    **Returns:**
    - Información de validez del token con fecha de expiración
    """
    try:
        # Validar el token
        payload = paseto_validator.validate(token)

        # Extraer la fecha de expiración del payload
        expires_at = payload.get("exp")

        logger.info(f"Token validado exitosamente. Expira en: {expires_at}")

        return {
            "msg": "valid",
            "expires_at": expires_at,
        }

    except ExpiredToken:
        logger.warning("Intento de acceso con token expirado")
        raise HTTPException(status_code=401, detail="Token expired") from None

    except InvalidToken as e:
        logger.warning(f"Intento de acceso con token inválido: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid token") from None

    except Exception as e:
        logger.error(f"Error inesperado al validar token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/stream")
async def stream_shared_location(
    token: str = Query(..., description="Token PASETO para validar acceso"),
):
    """
    Stream SSE con la ubicación en tiempo real para un link compartido.

    Este endpoint establece una conexión de Server-Sent Events (SSE) que envía
    actualizaciones de ubicación en tiempo real para un dispositivo específico.
    El token se valida periódicamente durante el stream.

    **Query Parameters:**
    - `token`: Token PASETO v4.local (requerido)

    **Ejemplo:**
    ```
    GET /api/v1/public/share-location/stream?token=v4.local.xxx...
    ```

    **Eventos SSE:**
    - `data`: Ubicación actual del dispositivo
        ```json
        {
            "device_id": "867564050638581",
            "latitude": 19.4326,
            "longitude": -99.1332,
            "speed": 45.5,
            "course": 180.0,
            "gps_datetime": "2024-01-15T10:30:00",
            "timestamp": "2024-01-15T10:30:01"
        }
        ```
    - `event: ping`: Heartbeat para mantener la conexión viva
    - `event: expired`: El token ha expirado, se cierra la conexión
    - `event: no_data`: No hay datos disponibles para el dispositivo

    **Returns:**
    - StreamingResponse con eventos SSE de ubicación en tiempo real
    """
    # 1. Validar token inicialmente
    try:
        payload = paseto_validator.validate(token)
    except ExpiredToken:
        logger.warning("Intento de stream con token expirado")
        raise HTTPException(status_code=401, detail="Token expired") from None
    except InvalidToken as e:
        logger.warning(f"Intento de stream con token inválido: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid token") from None

    device_id = payload.get("device_id")
    expires_at = payload.get("exp")

    if not device_id:
        raise HTTPException(status_code=403, detail="Invalid token: missing device_id")

    logger.info(
        f"Iniciando stream de ubicación para device_id: {device_id}, expira: {expires_at}"
    )

    # 2. Crear generador SSE
    async def event_generator():
        try:
            while True:
                # a) Validar expiración en cada ciclo
                now = datetime.now(UTC)
                exp = datetime.fromisoformat(expires_at)

                if now >= exp:
                    logger.info(
                        f"Token expirado durante el stream para device: {device_id}"
                    )
                    yield "event: expired\ndata: Token expired\n\n"
                    break

                # b) Obtener última posición del dispositivo
                # Crear una nueva sesión para cada consulta
                async with SessionLocal() as db:
                    try:
                        results = await get_latest_communications(db, [device_id])

                        if results and len(results) > 0:
                            point = results[0]
                            data = {
                                "device_id": point.device_id,
                                "latitude": (
                                    float(point.latitude) if point.latitude else None
                                ),
                                "longitude": (
                                    float(point.longitude) if point.longitude else None
                                ),
                                "speed": float(point.speed) if point.speed else None,
                                "course": float(point.course) if point.course else None,
                                "gps_datetime": (
                                    point.gps_datetime.isoformat()
                                    if point.gps_datetime
                                    else None
                                ),
                                "received_at": (
                                    point.received_at.isoformat()
                                    if point.received_at
                                    else None
                                ),
                                "engine_status": point.engine_status,
                                "fix_status": point.fix_status,
                                "satellites": point.satellites,
                                "speed_kmh": (
                                    float(point.speed) if point.speed else None
                                ),  # Alias para compatibilidad
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                        else:
                            # No hay datos disponibles
                            yield "event: no_data\ndata: No location data available\n\n"

                    except Exception as e:
                        logger.error(f"Error al obtener ubicación: {e}")
                        yield "event: error\ndata: Error retrieving location\n\n"

                # c) Heartbeat (importante para mantener SSE vivo)
                yield "event: ping\ndata: ok\n\n"

                # d) Esperar próximo ciclo (5 segundos)
                await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error en generador SSE: {e}")
            yield "event: error\ndata: Stream error\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
