import asyncio
import json
import logging

import paho.mqtt.client as mqtt

from app.core.config import settings

logger = logging.getLogger(__name__)


class MQTTClient:
    """Cliente MQTT para recibir mensajes de Mosquitto en tiempo real."""

    def __init__(self):
        self.client: mqtt.Client | None = None
        self.connected = False
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None

    def _on_connect(self, client, _userdata, _flags, rc):
        """Callback cuando se conecta al broker MQTT."""
        if rc == 0:
            self.connected = True
            logger.info(f"Conectado exitosamente al broker MQTT {settings.BROKER_HOST}")
            # Suscribirse al topic configurado
            client.subscribe(settings.BROKER_TOPIC)
            logger.info(f"Suscrito al topic: {settings.BROKER_TOPIC}")
        else:
            self.connected = False
            logger.error(f"Error al conectar al broker MQTT. Código de retorno: {rc}")

    def _on_disconnect(self, _client, _userdata, rc):
        """Callback cuando se desconecta del broker MQTT."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Desconexión inesperada del broker MQTT. Código: {rc}")
        else:
            logger.info("Desconectado del broker MQTT")

    def _on_message(self, _client, _userdata, msg):
        """Callback cuando se recibe un mensaje del broker MQTT."""
        try:
            # Decodificar el payload como JSON
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.debug(f"Mensaje recibido del topic {msg.topic}: {payload}")

            # Poner el mensaje en la cola de forma thread-safe
            if self._loop:
                asyncio.run_coroutine_threadsafe(
                    self.message_queue.put(payload), self._loop
                )
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar mensaje JSON: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje MQTT: {e}")

    def connect(self):
        """Inicializar y conectar el cliente MQTT."""
        try:
            # Obtener el event loop actual
            self._loop = asyncio.get_event_loop()

            # Crear cliente MQTT
            self.client = mqtt.Client(
                client_id=f"siscom-api-{settings.APP_NAME}",
                clean_session=True,
            )

            # Configurar callbacks
            if self.client:
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message

            # Configurar credenciales si están disponibles
            if self.client and settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(
                    settings.MQTT_USERNAME, settings.MQTT_PASSWORD
                )
                logger.info("Credenciales MQTT configuradas")
            else:
                logger.warning("Credenciales MQTT NO configuradas")

            # Parsear host y puerto
            broker_parts = settings.BROKER_HOST.split(":")
            host = broker_parts[0]
            port = int(broker_parts[1]) if len(broker_parts) > 1 else 1883

            # Conectar al broker
            if self.client:
                logger.info(f"Conectando al broker MQTT en {host}:{port}...")
                self.client.connect(host, port, keepalive=60)

                # Iniciar el loop en un thread separado
                self.client.loop_start()

            logger.info("Cliente MQTT inicializado correctamente")

        except Exception as e:
            logger.error(f"Error al inicializar cliente MQTT: {e}")
            self.connected = False

    def disconnect(self):
        """Desconectar el cliente MQTT."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Cliente MQTT desconectado")
            except Exception as e:
                logger.error(f"Error al desconectar cliente MQTT: {e}")

    async def get_message(self) -> dict:
        """Obtener el siguiente mensaje de la cola."""
        return await self.message_queue.get()

    def is_connected(self) -> bool:
        """Verificar si el cliente está conectado."""
        return self.connected


# Instancia global del cliente MQTT
mqtt_client = MQTTClient()
