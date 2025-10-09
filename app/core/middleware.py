import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.metrics import metrics_client


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para capturar métricas de peticiones y latencia."""

    async def dispatch(self, request: Request, call_next):
        # Registrar el inicio de la petición
        start_time = time.time()

        # Incrementar contador de peticiones
        await metrics_client.increment_requests()

        # Procesar la petición
        response = await call_next(request)

        # Calcular latencia
        duration_ms = (time.time() - start_time) * 1000

        # Enviar latencia específica para endpoints que contengan /stream
        if "/stream" in request.url.path:
            await metrics_client.timing_latency("stream", duration_ms)

        return response
