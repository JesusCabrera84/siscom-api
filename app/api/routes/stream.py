import asyncio
import json
import logging

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.services.mqtt_client import mqtt_client
from app.utils.metrics import metrics_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["SSE"])


async def sse_generator(device_ids: str | None, request: Request):
    """
    Generador de eventos SSE que consume mensajes de MQTT.

    Args:
        device_ids: String con device_ids separados por comas para filtrar (opcional)
        request: Request de FastAPI para detectar desconexiones
    """
    # Incrementar conexiones activas al iniciar
    await metrics_client.increment_active_connections()

    # Convertir device_ids a lista si existe
    device_list = device_ids.split(",") if device_ids else None

    logger.info(f"Nueva conexión SSE establecida. Filtro device_ids: {device_list}")

    try:
        while True:
            # Verificar si el cliente se ha desconectado
            if await request.is_disconnected():
                logger.info("Cliente SSE desconectado")
                break

            # Verificar si el cliente MQTT está conectado
            if not mqtt_client.is_connected():
                logger.warning("Cliente MQTT no conectado. Esperando reconexión...")
                await asyncio.sleep(1)
                continue

            try:
                # Esperar mensaje de MQTT con timeout
                event = await asyncio.wait_for(mqtt_client.get_message(), timeout=60.0)

                # Filtrar por device_ids si se especificó
                if device_list:
                    # Obtener DEVICE_ID del mensaje
                    device_id = event.get("data", {}).get("DEVICE_ID")

                    if not device_id or device_id not in device_list:
                        # Mensaje no coincide con el filtro, continuar
                        continue

                # Enviar evento al cliente
                logger.debug(f"Enviando evento SSE: {event}")
                yield {
                    "event": "message",
                    "data": json.dumps(event),
                }

            except TimeoutError:
                # Enviar keep-alive cada 60 segundos
                logger.debug("Enviando keep-alive SSE")
                yield {
                    "event": "ping",
                    "data": json.dumps({"type": "keep-alive"}),
                }

            except Exception as e:
                logger.error(f"Error al procesar mensaje MQTT: {e}")
                await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error en generador SSE: {e}")
    finally:
        # Decrementar conexiones activas al desconectar
        await metrics_client.decrement_active_connections()
        logger.info("Conexión SSE cerrada")


@router.get("/stream")
async def stream(request: Request, device_ids: str | None = None):
    """
    Endpoint de streaming SSE para recibir eventos de dispositivos en tiempo real.

    Args:
        request: Request de FastAPI
        device_ids: String con device_ids separados por comas para filtrar (opcional)
                   Ejemplo: "0848086072,0848086073"

    Returns:
        EventSourceResponse con eventos de dispositivos
    """
    generator = sse_generator(device_ids, request)
    return EventSourceResponse(
        generator,
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",  # Para nginx
            "Connection": "keep-alive",
        },
        ping=60,
    )  # Pings cada 60 segundos
