import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.metrics import metrics_client

logger = logging.getLogger(__name__)

EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/favicon.ico"}


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para capturar métricas de peticiones y latencia."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"

        # Log de TODAS las peticiones (antes de filtrar)
        logger.info(
            f"📨 Request: {method} {path} | Client: {client_host} | "
            f"User-Agent: {request.headers.get('user-agent', 'N/A')[:50]}"
        )

        # Verificar si está excluida
        is_excluded = any(path.startswith(p) for p in EXCLUDED_PATHS)

        if is_excluded:
            logger.debug(f"⏭️  Ruta excluida de métricas: {path}")
            # Si la ruta está excluida, simplemente procesa la petición
            return await call_next(request)

        # NO está excluida - contar métrica
        logger.info(f"📊 Contando métrica para: {method} {path}")
        start_time = time.time()

        # Incrementar contador de peticiones
        await metrics_client.increment_requests()

        # Procesar la petición
        response = await call_next(request)

        # Calcular latencia
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"⏱️  Latencia: {method} {path} -> {duration_ms:.2f}ms | Status: {response.status_code}"
        )

        # Enviar latencia solo para rutas de streaming u otras relevantes
        if "/stream" in path:
            await metrics_client.timing_latency("stream", duration_ms)

        return response
