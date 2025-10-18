# app/utils/metrics.py
from contextlib import asynccontextmanager

from aio_statsd import StatsdClient

from app.core.config import settings


class MetricsClient:
    """Cliente asíncrono robusto para enviar métricas a StatsD/Telegraf."""

    def __init__(self):
        self.client: StatsdClient | None = None
        self.prefix = settings.STATSD_PREFIX or "siscom_api"
        self._active_connections = 0  # Contador interno para gauge de SSE

    async def ensure_connected(self):
        """Reconecta el cliente si está cerrado o no inicializado."""
        if self.client is None or getattr(self.client, "_closed", False):
            self.client = StatsdClient(
                host=settings.STATSD_HOST,
                port=settings.STATSD_PORT,
            )
            await self.client.connect()

    async def close(self):
        """Cierra la conexión con StatsD."""
        if self.client and not getattr(self.client, "_closed", False):
            await self.client.close()
            self.client = None

    async def increment_requests(self, endpoint: str | None = None):
        """Incrementa el contador de peticiones (COUNTER - acumulativo).

        Perfecto para ver requests totales en períodos de tiempo en Grafana.
        Ej: requests por minuto, requests totales por hora, etc.
        """
        try:
            await self.ensure_connected()
            metric = f"{self.prefix}.requests"
            if endpoint:
                metric += f".{endpoint}"
            assert self.client is not None
            self.client.counter(metric, 1)  # Counter para métricas acumulativas
        except Exception as e:
            # Evita que un error en métricas rompa la app
            print(f"[Metrics] Error incrementing: {e}")

    async def timing_latency(self, endpoint: str, duration_ms: float):
        """Registra la latencia."""
        try:
            await self.ensure_connected()
            metric = f"{self.prefix}.latency.{endpoint}"
            assert self.client is not None
            self.client.timer(metric, duration_ms)  # Enviar métrica de timing
        except Exception as e:
            print(f"[Metrics] Error timing: {e}")

    async def increment_active_connections(self):
        """Incrementa conexiones SSE activas (GAUGE - valor actual).

        Usa gauge para reportar el número ACTUAL de conexiones en tiempo real.
        Perfecto para monitorear carga actual en Grafana.
        """
        try:
            await self.ensure_connected()
            assert self.client is not None
            self._active_connections += 1
            self.client.gauge(
                f"{self.prefix}.sse.active_connections", self._active_connections
            )
        except Exception as e:
            print(f"[Metrics] Error incrementing SSE: {e}")

    async def decrement_active_connections(self):
        """Decrementa conexiones SSE activas (GAUGE - valor actual)."""
        try:
            await self.ensure_connected()
            assert self.client is not None
            self._active_connections = max(0, self._active_connections - 1)
            self.client.gauge(
                f"{self.prefix}.sse.active_connections", self._active_connections
            )
        except Exception as e:
            print(f"[Metrics] Error decrementing SSE: {e}")


metrics_client = MetricsClient()


@asynccontextmanager
async def get_metrics_client():
    await metrics_client.ensure_connected()
    try:
        yield metrics_client
    finally:
        pass  # Se cierra globalmente en shutdown si se desea
