import asyncio
import json
import logging
import threading

from kafka import KafkaConsumer

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaClient:
    """Cliente Kafka/Redpanda para recibir mensajes en tiempo real."""

    def __init__(self):
        self.consumer: KafkaConsumer | None = None
        self.connected = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._reconnect_attempts = 0
        self._running = False
        self._consumer_thread: threading.Thread | None = None
        # Sistema de callbacks para WebSocket Broker (alta performance)
        self._message_callbacks: list = []

    def _create_consumer(self) -> KafkaConsumer:
        """Crear una nueva instancia del consumidor Kafka."""
        # Configuración básica del consumidor
        consumer_config = {
            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group_id": settings.KAFKA_GROUP_ID,
            "auto_offset_reset": settings.KAFKA_AUTO_OFFSET_RESET,
            "enable_auto_commit": True,
            "auto_commit_interval_ms": 1000,
            "session_timeout_ms": 30000,
            "heartbeat_interval_ms": 3000,
            "consumer_timeout_ms": 1000,  # Timeout para poll()
            "value_deserializer": lambda x: json.loads(x.decode("utf-8")),
        }

        # Agregar autenticación SASL si está configurada
        if settings.KAFKA_USERNAME and settings.KAFKA_PASSWORD:
            consumer_config.update(
                {
                    "security_protocol": settings.KAFKA_SECURITY_PROTOCOL,
                    "sasl_mechanism": settings.KAFKA_SASL_MECHANISM,
                    "sasl_plain_username": settings.KAFKA_USERNAME,
                    "sasl_plain_password": settings.KAFKA_PASSWORD,
                }
            )
            logger.info(f"Autenticación SASL Kafka configurada: {settings.KAFKA_SASL_MECHANISM} con protocolo {settings.KAFKA_SECURITY_PROTOCOL}")

        return KafkaConsumer(settings.KAFKA_TOPIC, **consumer_config)

    def _handle_consumer_unavailable(self):
        """Maneja el caso cuando el consumer no está disponible."""
        logger.warning("Consumer no disponible, esperando...")
        if self._loop:
            asyncio.run_coroutine_threadsafe(asyncio.sleep(1), self._loop)
        else:
            logger.error("Event loop no disponible")

    def _process_message(self, message):
        """Procesa un mensaje individual de Kafka."""
        try:
            payload = message.value
            logger.debug(f"Mensaje recibido del topic {message.topic}: {payload}")

            # Llamar callbacks registrados (WebSocket Broker)
            if self._loop and self._message_callbacks:
                for callback in self._message_callbacks:
                    asyncio.run_coroutine_threadsafe(callback(payload), self._loop)

        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar mensaje JSON: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje Kafka: {e}")

    def _handle_consumer_error(self, error):
        """Maneja errores del consumer Kafka."""
        logger.error(f"Error en el loop de consumo Kafka: {error}")
        self.connected = False
        self._reconnect_attempts += 1

        if not self._running:
            return

        logger.info(f"Intentando reconexión... (Intento {self._reconnect_attempts})")
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                asyncio.sleep(min(30, 2**self._reconnect_attempts)), self._loop
            )
            self._reconnect()
        else:
            logger.error("Event loop no disponible para reconexión")

    def _consume_messages(self):
        """Thread worker para consumir mensajes de Kafka."""
        logger.info(f"Iniciando consumo de mensajes del topic: {settings.KAFKA_TOPIC}")

        while self._running:
            try:
                if not self.consumer:
                    self._handle_consumer_unavailable()
                    continue

                # Poll por mensajes con timeout
                message_batch = self.consumer.poll(timeout_ms=1000)

                if not message_batch:
                    continue

                # Procesar cada mensaje en el batch
                for _topic_partition, messages in message_batch.items():
                    for message in messages:
                        self._process_message(message)

            except Exception as e:
                self._handle_consumer_error(e)

    def _reconnect(self):
        """Intentar reconectar el consumidor Kafka."""
        try:
            if self.consumer:
                self.consumer.close()
                self.consumer = None

            self.consumer = self._create_consumer()
            # Intentar hacer poll para verificar conexión
            self.consumer.poll(timeout_ms=1000)

            self.connected = True
            self._reconnect_attempts = 0
            logger.info(
                f"Conectado exitosamente a Kafka/Redpanda {settings.KAFKA_BOOTSTRAP_SERVERS}"
            )

        except Exception as e:
            logger.error(f"Error al reconectar consumidor Kafka: {e}")
            self.connected = False

    def connect(self):
        """Inicializar y conectar el cliente Kafka."""
        try:
            # Obtener el event loop actual
            self._loop = asyncio.get_event_loop()

            # Crear el consumidor
            self.consumer = self._create_consumer()

            # Marcar como corriendo
            self._running = True

            # Iniciar thread de consumo
            self._consumer_thread = threading.Thread(
                target=self._consume_messages, name="kafka-consumer-thread", daemon=True
            )
            self._consumer_thread.start()

            # Intentar primera conexión
            self._reconnect()

            logger.info("Cliente Kafka inicializado correctamente")

        except Exception as e:
            logger.error(f"Error al inicializar cliente Kafka: {e}")
            self.connected = False
            self._running = False

    def disconnect(self):
        """Desconectar el cliente Kafka."""
        if not self._running:
            return

        logger.info("Desconectando cliente Kafka...")

        # Detener el loop de consumo
        self._running = False

        # Esperar que el thread termine
        if self._consumer_thread and self._consumer_thread.is_alive():
            self._consumer_thread.join(timeout=5)

        # Cerrar el consumidor
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Consumidor Kafka cerrado")
            except Exception as e:
                logger.error(f"Error al cerrar consumidor Kafka: {e}")

        self.connected = False

    def is_connected(self) -> bool:
        """Verificar si el cliente está conectado."""
        return self.connected

    def register_message_callback(self, callback):
        """
        Registra un callback para recibir mensajes Kafka en tiempo real.

        El callback debe ser una coroutine async que acepte un dict (mensaje Kafka).

        Args:
            callback: Coroutine async(message: dict) -> None
        """
        if callback not in self._message_callbacks:
            self._message_callbacks.append(callback)
            logger.info(
                f"Callback registrado. Total callbacks: {len(self._message_callbacks)}"
            )

    def unregister_message_callback(self, callback):
        """
        Desregistra un callback de mensajes Kafka.

        Args:
            callback: Coroutine a desregistrar
        """
        if callback in self._message_callbacks:
            self._message_callbacks.remove(callback)
            logger.info(
                f"Callback desregistrado. Total callbacks: {len(self._message_callbacks)}"
            )


# Instancia global del cliente Kafka
kafka_client = KafkaClient()
