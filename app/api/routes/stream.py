import asyncio
import json
import logging
from contextlib import suppress

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from app.services.mqtt_client import mqtt_client
from app.utils.metrics import metrics_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Stream"])


# ============================================================================
# WebSocket Broker - Sistema de pub/sub interno de alta performance
# ============================================================================


class WebSocketBroker:
    """
    Broker interno para distribuir mensajes MQTT a múltiples conexiones WebSocket.

    Arquitectura:
    - Un único consumer MQTT global
    - Cada WebSocket se suscribe a device_ids específicos
    - Los mensajes se distribuyen solo a los WebSockets interesados
    - Usa asyncio.Queue para comunicación lock-free y alta performance
    """

    def __init__(self):
        # dict[device_id -> set[asyncio.Queue]]
        self.subscribers: dict[str, set[asyncio.Queue]] = {}
        self.lock = asyncio.Lock()
        self._stats_total_messages = 0
        self._stats_total_subscribers = 0

    async def subscribe(self, device_ids: list[str]) -> list[asyncio.Queue]:
        """
        Suscribe un WebSocket a una lista de device_ids.

        Args:
            device_ids: Lista de device_ids a monitorear

        Returns:
            Lista de colas (una por device_id) para recibir mensajes
        """
        queues = []
        async with self.lock:
            for dev in device_ids:
                # Crear una cola con límite para evitar memory leaks
                q = asyncio.Queue(maxsize=100)
                queues.append(q)

                if dev not in self.subscribers:
                    self.subscribers[dev] = set()

                self.subscribers[dev].add(q)
                self._stats_total_subscribers += 1

            logger.info(
                f"WebSocket suscrito a {len(device_ids)} devices. "
                f"Total subscribers activos: {self._stats_total_subscribers}"
            )

        return queues

    async def unsubscribe(self, device_ids: list[str], queues: list[asyncio.Queue]):
        """
        Desuscribe un WebSocket de sus device_ids.

        Args:
            device_ids: Lista de device_ids a desuscribir
            queues: Colas asociadas al WebSocket
        """
        async with self.lock:
            for dev in device_ids:
                if dev in self.subscribers:
                    for q in queues:
                        self.subscribers[dev].discard(q)
                        self._stats_total_subscribers -= 1

                    # Limpiar entrada si no hay más subscribers
                    if not self.subscribers[dev]:
                        del self.subscribers[dev]

            logger.info(
                f"WebSocket desuscrito de {len(device_ids)} devices. "
                f"Total subscribers activos: {self._stats_total_subscribers}"
            )

    async def publish(self, message: dict):
        """
        Publica un mensaje MQTT a todos los WebSockets suscritos al device_id.

        Args:
            message: Mensaje MQTT completo con estructura {"data": {"DEVICE_ID": "..."}}
        """
        dev = message.get("data", {}).get("DEVICE_ID")
        if not dev:
            logger.warning(f"Mensaje sin DEVICE_ID recibido: {message}")
            return

        self._stats_total_messages += 1

        async with self.lock:
            if dev not in self.subscribers:
                # No hay nadie escuchando este device_id
                return

            # Distribuir a todas las colas suscritas
            dead_queues = []
            for q in self.subscribers[dev]:
                try:
                    # Usar put_nowait para evitar bloqueos
                    # Si la cola está llena, aplicamos backpressure (descartamos)
                    if q.full():
                        logger.warning(
                            f"Cola llena para device_id {dev}. "
                            f"Aplicando backpressure (mensaje descartado)"
                        )
                        continue

                    q.put_nowait(message)
                except asyncio.QueueFull:
                    # Backpressure: cliente muy lento
                    logger.warning(f"Backpressure aplicado para device_id {dev}")
                except Exception as e:
                    logger.error(f"Error al publicar mensaje: {e}")
                    dead_queues.append(q)

            # Limpiar colas muertas
            for q in dead_queues:
                self.subscribers[dev].discard(q)

    def get_stats(self) -> dict:
        """Retorna estadísticas del broker."""
        return {
            "total_messages_processed": self._stats_total_messages,
            "active_subscribers": self._stats_total_subscribers,
            "devices_being_monitored": len(self.subscribers),
        }


# Instancia global del broker
ws_broker = WebSocketBroker()


# ============================================================================
# MQTT Listener - Conecta MQTT → WebSocket Broker
# ============================================================================


async def mqtt_message_handler(message: dict):
    """
    Handler que recibe mensajes MQTT y los publica al broker interno.

    Esta función se registra como callback en mqtt_client para recibir
    mensajes en tiempo real sin consumir de una cola.
    """
    try:
        await ws_broker.publish(message)
    except Exception as e:
        logger.error(f"Error al publicar mensaje al broker: {e}", exc_info=True)


def start_mqtt_broker_bridge():
    """
    Inicia el puente entre MQTT y el WebSocket Broker.

    Registra el callback para que cada mensaje MQTT se publique
    automáticamente al broker interno. Esta es la arquitectura
    de alta performance: un solo flujo MQTT → muchos WebSockets.

    DEBE llamarse en el startup de la aplicación.
    """
    mqtt_client.register_message_callback(mqtt_message_handler)
    logger.info("✅ MQTT → WebSocket Broker bridge iniciado")


# ============================================================================
# Endpoint WebSocket - Alta Performance
# ============================================================================


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket, device_ids: str | None = None):
    """
    Endpoint WebSocket para recibir eventos de dispositivos en tiempo real.

    **Ventajas sobre SSE:**
    - ✅ Full-duplex (bidireccional)
    - ✅ Sin problemas de buffering en ALB/nginx
    - ✅ Menor overhead de red
    - ✅ Mejor soporte en móviles
    - ✅ Backpressure natural

    **Query Parameters:**
    - `device_ids`: String con device_ids separados por comas para filtrar (opcional)
                   Ejemplo: "0848086072,0848086073"

    **Protocolo:**
    - Cliente se conecta vía WebSocket
    - Servidor envía mensajes JSON cuando hay eventos
    - Formato: {"event": "message", "data": {...}}
    - Keep-alive automático cada 60 segundos: {"event": "ping", "data": {"type": "keep-alive"}}

    **Ejemplo de uso en JavaScript:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/stream?device_ids=0848086072');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Mensaje recibido:', data);
    };
    ```
    """
    await websocket.accept()
    await metrics_client.increment_active_connections()

    # Parse device_ids
    device_list = device_ids.split(",") if device_ids else []

    # Si no se especificaron device_ids, no podemos filtrar eficientemente
    # En este caso, podrías decidir rechazar la conexión o permitir todos
    if not device_list:
        logger.warning("WebSocket conectado sin filtro de device_ids")
        await websocket.send_json({
            "event": "error",
            "data": {
                "message": "Debe especificar al menos un device_id en los query params"
            }
        })
        await websocket.close(code=1008)  # Policy Violation
        await metrics_client.decrement_active_connections()
        return

    # Suscribirse al broker
    queues = await ws_broker.subscribe(device_list)

    logger.info(f"WebSocket conectado. Device filter: {device_list}")

    # Task para enviar keep-alive
    async def send_keepalive():
        try:
            while True:
                await asyncio.sleep(60)
                await websocket.send_json({
                    "event": "ping",
                    "data": {"type": "keep-alive"}
                })
        except Exception:
            pass

    keepalive_task = asyncio.create_task(send_keepalive())

    try:
        while True:
            # Esperar mensaje de cualquiera de las colas suscritas
            # Usamos wait con FIRST_COMPLETED para alta performance
            if not queues:
                await asyncio.sleep(1)
                continue

            done, pending = await asyncio.wait(
                [asyncio.create_task(q.get()) for q in queues],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancelar tasks pendientes
            for task in pending:
                task.cancel()

            # Procesar mensaje recibido
            for task in done:
                try:
                    event = task.result()

                    # Enviar al cliente
                    await websocket.send_json({
                        "event": "message",
                        "data": event,
                    })

                    logger.debug(f"Mensaje WebSocket enviado: {event.get('data', {}).get('DEVICE_ID')}")

                except Exception as e:
                    logger.error(f"Error al procesar mensaje de cola: {e}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado. Devices: {device_list}")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}", exc_info=True)
    finally:
        # Cleanup
        keepalive_task.cancel()
        await ws_broker.unsubscribe(device_list, queues)
        await metrics_client.decrement_active_connections()
        with suppress(Exception):
            await websocket.close()


# ============================================================================
# Endpoint de Estadísticas - Monitoreo del Broker
# ============================================================================


@router.get("/stream/stats")
async def get_broker_stats():
    """
    Obtiene estadísticas en tiempo real del WebSocket Broker.

    **Returns:**
    - `total_messages_processed`: Total de mensajes procesados desde el inicio
    - `active_subscribers`: Número de suscripciones activas (total de colas)
    - `devices_being_monitored`: Número de device_ids únicos siendo monitoreados

    **Ejemplo de uso:**
    ```bash
    curl http://localhost:8000/api/v1/stream/stats
    ```

    **Respuesta:**
    ```json
    {
        "total_messages_processed": 15234,
        "active_subscribers": 45,
        "devices_being_monitored": 23
    }
    ```
    """
    return ws_broker.get_stats()


# ============================================================================
# Endpoint SSE (Legacy - Mantener por retrocompatibilidad temporal)
# ============================================================================


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
