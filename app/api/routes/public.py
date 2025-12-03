"""
Rutas públicas para compartir ubicaciones de dispositivos GPS.

Este módulo proporciona endpoints públicos que no requieren autenticación JWT
pero usan tokens PASETO para autorización temporal.
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, Request
from sse_starlette.sse import EventSourceResponse

from app.core.database import SessionLocal
from app.services.mqtt_client import mqtt_client
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

    Este endpoint valida un token PASETO v4.local emitido por siscom-admin-api,
    retorna información sobre su validez, expiración y la última ubicación del dispositivo.

    **Query Parameters:**
    - `token`: Token PASETO v4.local (requerido)

    **Ejemplo:**
    ```
    GET /api/v1/public/share-location/init?token=v4.local.xxx...
    ```

    **Responses:**
    - 200: Token válido con datos de ubicación
        ```json
        {
            "msg": "valid",
            "expires_at": "2024-12-31T23:59:59+00:00",
            "device_id": "867564050638581",
            "last_communication": {
                "device_id": "867564050638581",
                "latitude": 19.4326,
                "longitude": -99.1332,
                "speed": 45.5,
                "course": 180.0,
                "gps_datetime": "2024-01-15T10:30:00",
                "received_at": "2024-01-15T10:30:01",
                "engine_status": "ON",
                "fix_status": "VALID",
                "satellites": 12
            }
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
    - 404: Dispositivo sin comunicaciones
        ```json
        {
            "detail": "No communication found for device"
        }
        ```

    **Returns:**
    - Información de validez del token, fecha de expiración y última ubicación
    """
    try:
        # Validar el token
        payload = paseto_validator.validate(token)

        # Extraer información del payload
        expires_at = payload.get("exp")
        device_id = payload.get("device_id")

        if not device_id:
            raise HTTPException(
                status_code=403, detail="Invalid token: missing device_id"
            )

        logger.info(
            f"Token validado exitosamente. Device: {device_id}, Expira en: {expires_at}"
        )

        # Obtener la última comunicación del dispositivo
        async with SessionLocal() as db:
            try:
                results = await get_latest_communications(db, [device_id])

                if not results or len(results) == 0:
                    # Token válido pero sin datos de ubicación
                    return {
                        "msg": "valid",
                        "expires_at": expires_at,
                        "device_id": device_id,
                        "last_communication": None,
                    }

                # Formatear la última comunicación
                point = results[0]
                last_communication = {
                    "device_id": point.device_id,
                    "latitude": float(point.latitude) if point.latitude else None,
                    "longitude": float(point.longitude) if point.longitude else None,
                    "speed": float(point.speed) if point.speed else None,
                    "course": float(point.course) if point.course else None,
                    "gps_datetime": (
                        point.gps_datetime.isoformat() if point.gps_datetime else None
                    ),
                    "received_at": (
                        point.received_at.isoformat() if point.received_at else None
                    ),
                    "engine_status": point.engine_status,
                    "fix_status": point.fix_status,
                    "satellites": point.satellites,
                    "backup_battery_voltage": (
                        float(point.backup_battery_voltage)
                        if point.backup_battery_voltage
                        else None
                    ),
                    "main_battery_voltage": (
                        float(point.main_battery_voltage)
                        if point.main_battery_voltage
                        else None
                    ),
                    "odometer": point.odometer,
                }

                return {
                    "msg": "valid",
                    "expires_at": expires_at,
                    "device_id": device_id,
                    "last_communication": last_communication,
                }

            except Exception as db_error:
                logger.error(f"Error al obtener comunicación: {db_error}")
                # Token válido pero error al obtener datos
                return {
                    "msg": "valid",
                    "expires_at": expires_at,
                    "device_id": device_id,
                    "last_communication": None,
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
    request: Request,
    token: str = Query(..., description="Token PASETO para validar acceso"),
):
    """
    Stream SSE con la ubicación en tiempo real para un link compartido.

    Este endpoint establece una conexión de Server-Sent Events (SSE) que envía
    actualizaciones de ubicación en tiempo real desde MQTT para un dispositivo específico.
    El token se valida periódicamente durante el stream.

    **Query Parameters:**
    - `token`: Token PASETO v4.local (requerido)

    **Ejemplo:**
    ```
    GET /api/v1/public/share-location/stream?token=v4.local.xxx...
    ```

    **Eventos SSE:**
    - `message`: Datos de ubicación en tiempo real desde MQTT
    - `event: ping`: Heartbeat para mantener la conexión viva
    - `event: expired`: El token ha expirado, se cierra la conexión

    **Returns:**
    - EventSourceResponse con eventos SSE de ubicación en tiempo real
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

    if not device_id:
        raise HTTPException(status_code=403, detail="Invalid token: missing device_id")

    expires_at_str = payload.get("exp")
    if not expires_at_str:
        raise HTTPException(status_code=403, detail="Invalid token: missing exp")

    expires_at = datetime.fromisoformat(expires_at_str)

    logger.info(
        f"Iniciando stream público para device_id: {device_id}, expira: {expires_at}"
    )

    # 2. Crear generador SSE
    async def event_generator():
        try:
            while True:
                # a) Verificar si el cliente se ha desconectado
                if await request.is_disconnected():
                    logger.info(f"Cliente desconectado del stream público: {device_id}")
                    break

                # b) Validar expiración del token en cada ciclo
                now = datetime.now(UTC)
                if now >= expires_at:
                    logger.info(f"Token expirado durante stream público: {device_id}")
                    yield {
                        "event": "expired",
                        "data": json.dumps({"message": "Token expired"}),
                    }
                    break

                # c) Verificar conexión MQTT
                if not mqtt_client.is_connected():
                    logger.warning("Cliente MQTT no conectado. Esperando reconexión...")
                    await asyncio.sleep(1)
                    continue

                try:
                    # d) Esperar mensaje de MQTT con timeout
                    event = await asyncio.wait_for(
                        mqtt_client.get_message(), timeout=60.0
                    )

                    # e) Filtrar por device_id
                    message_device_id = event.get("data", {}).get("DEVICE_ID")

                    if not message_device_id or message_device_id != device_id:
                        # Mensaje no coincide con el filtro, continuar
                        continue

                    # f) Enviar evento al cliente
                    logger.debug(f"Enviando evento SSE público: {event}")
                    yield {
                        "event": "message",
                        "data": json.dumps(event),
                    }

                except TimeoutError:
                    # g) Enviar keep-alive cada 60 segundos
                    logger.debug("Enviando keep-alive SSE público")
                    yield {
                        "event": "ping",
                        "data": json.dumps({"type": "keep-alive"}),
                    }

                except Exception as e:
                    logger.error(
                        f"Error al procesar mensaje MQTT en stream público: {e}"
                    )
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error en generador SSE público: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": "Stream error"}),
            }

    return EventSourceResponse(event_generator(), ping=60)
