# app/utils/metrics.py
import logging
from contextlib import asynccontextmanager

from aio_statsd import StatsdClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class MetricsClient:
    """Cliente asíncrono robusto para enviar métricas a StatsD/Telegraf."""

    def __init__(self):
        self.client: StatsdClient | None = None
        self.prefix = settings.STATSD_PREFIX or "siscom_api"
        self._active_connections = 0  # Contador interno para gauge de SSE
        self._enabled = settings.STATSD_ENABLED

    async def ensure_connected(self):
        """Reconecta el cliente si está cerrado o no inicializado."""
        if not self._enabled:
            return  # StatsD deshabilitado, no hacer nada

        if self.client is None or getattr(self.client, "_closed", False):
            try:
                self.client = StatsdClient(
                    host=settings.STATSD_HOST,
                    port=settings.STATSD_PORT,
                )
                await self.client.connect()
                logger.info(f"✓ Cliente StatsD conectado a {settings.STATSD_HOST}:{settings.STATSD_PORT}")
            except Exception as e:
                logger.warning(f"No se pudo conectar a StatsD: {e}")
                self._enabled = False  # Deshabilitar para evitar reintentos constantes

    async def close(self):
        """Cierra la conexión con StatsD."""
        if self.client and not getattr(self.client, "_closed", False):
            try:
                await self.client.close()
                self.client = None
                logger.info("Cliente StatsD cerrado")
            except Exception as e:
                logger.warning(f"Error al cerrar StatsD: {e}")

    async def increment_requests(self, endpoint: str | None = None):
        """Incrementa el contador de peticiones (COUNTER - acumulativo).

        Perfecto para ver requests totales en períodos de tiempo en Grafana.
        Ej: requests por minuto, requests totales por hora, etc.
        """
        if not self._enabled:
            return  # StatsD deshabilitado

        try:
            await self.ensure_connected()
            if not self.client:
                return
            metric = f"{self.prefix}.requests"
            if endpoint:
                metric += f".{endpoint}"
            self.client.counter(metric, 1)  # Counter para métricas acumulativas
        except Exception as e:
            # Evita que un error en métricas rompa la app
            logger.debug(f"Error en métricas (increment): {e}")

    async def timing_latency(self, endpoint: str, duration_ms: float):
        """Registra la latencia."""
        if not self._enabled:
            return  # StatsD deshabilitado

        try:
            await self.ensure_connected()
            if not self.client:
                return
            metric = f"{self.prefix}.latency.{endpoint}"
            self.client.timer(metric, duration_ms)  # Enviar métrica de timing
        except Exception as e:
            logger.debug(f"Error en métricas (timing): {e}")

    async def increment_active_connections(self):
        """Incrementa conexiones SSE activas (GAUGE - valor actual).

        Usa gauge para reportar el número ACTUAL de conexiones en tiempo real.
        Perfecto para monitorear carga actual en Grafana.
        """
        if not self._enabled:
            self._active_connections += 1  # Mantener el contador interno
            return  # StatsD deshabilitado

        try:
            await self.ensure_connected()
            if not self.client:
                return
            self._active_connections += 1
            self.client.gauge(
                f"{self.prefix}.sse.active_connections", self._active_connections
            )
        except Exception as e:
            logger.debug(f"Error en métricas (increment SSE): {e}")

    async def decrement_active_connections(self):
        """Decrementa conexiones SSE activas (GAUGE - valor actual)."""
        if not self._enabled:
            self._active_connections = max(0, self._active_connections - 1)  # Mantener el contador interno
            return  # StatsD deshabilitado

        try:
            await self.ensure_connected()
            if not self.client:
                return
            self._active_connections = max(0, self._active_connections - 1)
            self.client.gauge(
                f"{self.prefix}.sse.active_connections", self._active_connections
            )
        except Exception as e:
            logger.debug(f"Error en métricas (decrement SSE): {e}")


metrics_client = MetricsClient()


@asynccontextmanager
async def get_metrics_client():
    await metrics_client.ensure_connected()
    try:
        yield metrics_client
    finally:
        pass  # Se cierra globalmente en shutdown si se desea
