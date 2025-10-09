from contextlib import asynccontextmanager
from typing import Optional

from aio_statsd import StatsdClient

from app.core.config import settings


class MetricsClient:
    """Cliente asíncrono para enviar métricas a StatsD/Telegraf."""

    def __init__(self):
        self.client: Optional[StatsdClient] = None
        self.prefix = settings.STATSD_PREFIX or "siscom_api"

    async def connect(self):
        """Conecta al servidor StatsD."""
        if self.client is None:
            self.client = StatsdClient(
                host=settings.STATSD_HOST,
                port=settings.STATSD_PORT,
            )

    async def close(self):
        """Cierra la conexión con StatsD."""
        if self.client:
            await self.client.close()
            self.client = None

    async def increment_requests(self, endpoint: str = None):
        """Incrementa el contador de peticiones por minuto."""
        if self.client:
            await self.client.increment(f"{self.prefix}.requests", 1)

    async def timing_latency(self, endpoint: str, duration_ms: float):
        """Registra la latencia de un endpoint en milisegundos."""
        if self.client:
            await self.client.timing(f"{self.prefix}.latency.{endpoint}", duration_ms)

    async def increment_active_connections(self):
        """Incrementa el contador de conexiones SSE activas."""
        if self.client:
            await self.client.increment(f"{self.prefix}.sse.active_connections", 1)

    async def decrement_active_connections(self):
        """Decrementa el contador de conexiones SSE activas."""
        if self.client:
            await self.client.decrement(f"{self.prefix}.sse.active_connections", 1)


# Instancia global del cliente de métricas
metrics_client = MetricsClient()


@asynccontextmanager
async def get_metrics_client():
    """Context manager para obtener el cliente de métricas."""
    await metrics_client.connect()
    try:
        yield metrics_client
    finally:
        pass  # No cerramos aquí, se cierra en el shutdown de la app
