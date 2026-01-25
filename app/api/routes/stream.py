import asyncio
import logging
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.kafka_client import kafka_client
from app.utils.metrics import metrics_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Stream"])


# ============================================================================
# WebSocket Broker - Sistema de pub/sub interno de alta performance
# ============================================================================


class WebSocketBroker:
    """
    Broker interno para distribuir mensajes Kafka/Redpanda a múltiples conexiones WebSocket.

    Arquitectura:
    - Un único consumer Kafka global
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
        Publica un mensaje Kafka/Redpanda a todos los WebSockets suscritos al device_id.

        Args:
            message: Mensaje Kafka/Redpanda completo con estructura {"data": {"DEVICE_ID": "..."}}
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
# Kafka Listener - Conecta Kafka/Redpanda → WebSocket Broker
# ============================================================================


async def kafka_message_handler(message: dict):
    """
    Handler que recibe mensajes Kafka/Redpanda y los publica al broker interno.

    Esta función se registra como callback en kafka_client para recibir
    mensajes en tiempo real sin consumir de una cola.
    """
    try:
        await ws_broker.publish(message)
    except Exception as e:
        logger.error(f"Error al publicar mensaje al broker: {e}", exc_info=True)


def start_kafka_broker_bridge():
    """
    Inicia el puente entre Kafka/Redpanda y el WebSocket Broker.

    Registra el callback para que cada mensaje Kafka se publique
    automáticamente al broker interno. Esta es la arquitectura
    de alta performance: un solo flujo Kafka → muchos WebSockets.

    DEBE llamarse en el startup de la aplicación.
    """
    kafka_client.register_message_callback(kafka_message_handler)
    logger.info("✅ Kafka → WebSocket Broker bridge iniciado")


# ============================================================================
# Endpoint WebSocket - Alta Performance
# ============================================================================


async def validate_device_ids(
    websocket: WebSocket, device_ids: str | None
) -> list[str]:
    """
    Valida y parsea los device_ids del query parameter.

    Args:
        websocket: Conexión WebSocket
        device_ids: String con device_ids separados por comas

    Returns:
        Lista de device_ids validados

    Raises:
        WebSocketDisconnect: Si no se proporcionan device_ids válidos
    """
    device_list = device_ids.split(",") if device_ids else []

    if not device_list:
        logger.warning("WebSocket rechazado: no se especificaron device_ids")
        try:
            await websocket.send_json(
                {
                    "event": "error",
                    "data": {
                        "message": "Debe especificar al menos un device_id en los query params",
                        "example": "?device_ids=867564050638581,867564050638582",
                    },
                }
            )
        except Exception as e:
            logger.debug(f"Error al enviar mensaje de error al cliente: {e}")

        await websocket.close(code=1008)  # Policy Violation
        raise WebSocketDisconnect(code=1008, reason="Missing device_ids")

    return device_list


async def create_keepalive_task(
    websocket: WebSocket, connection_active: asyncio.Event
) -> asyncio.Task:
    """
    Crea el task de keep-alive para la conexión WebSocket.

    Args:
        websocket: Conexión WebSocket
        connection_active: Event que indica si la conexión está activa

    Returns:
        Task de keep-alive
    """

    async def send_keepalive():
        try:
            while connection_active.is_set():
                await asyncio.sleep(60)
                if not connection_active.is_set():
                    break
                try:
                    await websocket.send_json(
                        {"event": "ping", "data": {"type": "keep-alive"}}
                    )
                    logger.debug("Keep-alive enviado")
                except Exception as e:
                    logger.warning(f"Error al enviar keep-alive: {e}")
                    break
        except asyncio.CancelledError:
            logger.debug("Task de keep-alive cancelado")
        except Exception as e:
            logger.error(f"Error inesperado en keep-alive: {e}")

    task = asyncio.create_task(send_keepalive())
    return task


async def process_websocket_messages(
    websocket: WebSocket, queues: list[asyncio.Queue]
) -> None:
    """
    Procesa mensajes de las colas de WebSocket y los envía al cliente.

    Args:
        websocket: Conexión WebSocket
        queues: Lista de colas de mensajes
        device_list: Lista de device_ids suscritos

    Raises:
        WebSocketDisconnect: Cuando la conexión se cierra
    """
    while True:
        # Esperar mensaje de cualquiera de las colas suscritas
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

                # Enviar al cliente - verificar si la conexión está cerrada
                try:
                    await websocket.send_json(
                        {
                            "event": "message",
                            "data": event,
                        }
                    )

                    logger.debug(
                        f"Mensaje WebSocket enviado: {event.get('data', {}).get('DEVICE_ID')}"
                    )
                except Exception as send_error:
                    # Si no podemos enviar, la conexión probablemente está cerrada
                    logger.warning(
                        f"Error al enviar mensaje WebSocket (conexión cerrada): {send_error}"
                    )
                    raise WebSocketDisconnect(
                        code=1000, reason="Connection closed"
                    ) from send_error

            except WebSocketDisconnect:
                # Re-lanzar para que sea capturado por el handler principal
                raise
            except Exception as e:
                logger.error(f"Error al procesar mensaje de cola: {e}")


async def cleanup_websocket_connection(
    keepalive_task: asyncio.Task,
    device_list: list[str],
    queues: list[asyncio.Queue],
    connection_active: asyncio.Event,
) -> None:
    """
    Limpia recursos de la conexión WebSocket.

    Args:
        keepalive_task: Task de keep-alive a cancelar
        device_list: Lista de device_ids a desuscribir
        queues: Colas asociadas al WebSocket
        connection_active: Event de conexión activa
    """
    # Marcar conexión como inactiva para detener keepalive
    connection_active.clear()

    # Cancelar keepalive task
    keepalive_task.cancel()
    try:
        await keepalive_task
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.debug(f"Error al cancelar keepalive task: {e}")

    await ws_broker.unsubscribe(device_list, queues)
    await metrics_client.decrement_active_connections()


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

    try:
        # Validar y parsear device_ids
        device_list = await validate_device_ids(websocket, device_ids)

        # Suscribirse al broker
        queues = await ws_broker.subscribe(device_list)

        logger.info(
            f"✅ WebSocket conectado exitosamente - Device IDs: {device_list} - Cliente: {websocket.client}"
        )

        # Event para coordinar la cancelación entre el loop principal y keepalive
        connection_active = asyncio.Event()
        connection_active.set()

        # Crear task de keep-alive
        keepalive_task = await create_keepalive_task(websocket, connection_active)

        # Procesar mensajes hasta que la conexión se cierre
        await process_websocket_messages(websocket, queues)

    except WebSocketDisconnect as disconnect_error:
        logger.info(
            f"📴 WebSocket desconectado normalmente - Device IDs: {device_list if 'device_list' in locals() else 'N/A'} - Código: {disconnect_error.code} - Cliente: {websocket.client}"
        )
    except Exception as e:
        logger.error(
            f"💥 Error crítico en WebSocket - Device IDs: {device_list if 'device_list' in locals() else 'N/A'} - Cliente: {websocket.client} - Error: {e}",
            exc_info=True,
        )
    finally:
        # Cleanup de recursos
        if "keepalive_task" in locals():
            await cleanup_websocket_connection(
                keepalive_task,
                device_list if "device_list" in locals() else [],
                queues if "queues" in locals() else [],
                (
                    connection_active
                    if "connection_active" in locals()
                    else asyncio.Event()
                ),
            )

        # Cerrar WebSocket de forma segura
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
