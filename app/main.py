import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import communications, public, stream
from app.api.routes.stream import start_kafka_broker_bridge
from app.core.config import settings
from app.core.database import engine
from app.core.middleware import MetricsMiddleware
from app.services.kafka_client import kafka_client
from app.utils.metrics import metrics_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Asegurar que el middleware tenga logging activado
logging.getLogger("app.core.middleware").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manejo del ciclo de vida de la aplicación."""
    # Startup: Verificar conexión a la base de datos
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logging.info("✓ Conexión a base de datos exitosa")
    except Exception as e:
        logging.error("✗ Error al conectar con la base de datos")
        logging.error(f"✗ Detalles: {e}")

    # Startup: Conectar cliente de métricas
    await metrics_client.ensure_connected()

    # Startup: Conectar cliente Kafka
    try:
        kafka_client.connect()
        logging.info("Cliente Kafka inicializado")
    except Exception as e:
        logging.error(f"Error al inicializar cliente Kafka: {e}")

    # Startup: Iniciar bridge Kafka → WebSocket Broker (alta performance)
    try:
        start_kafka_broker_bridge()
        logging.info("✅ Bridge Kafka → WebSocket activo")
    except Exception as e:
        logging.error(f"Error al iniciar Kafka bridge: {e}")

    # Tarea periódica para reportar el estado del circuit breaker de Kafka como métrica
    async def report_kafka_circuit_breaker():
        while True:
            await metrics_client.kafka_circuit_breaker_gauge(
                kafka_client.circuit_breaker_status()["open"]
            )
            await asyncio.sleep(10)

    task = None
    if settings.STATSD_ENABLED:
        task = asyncio.create_task(report_kafka_circuit_breaker())

    yield

    if task:
        task.cancel()
        with contextlib.suppress(Exception):
            await task

    # Shutdown: Cerrar cliente Kafka
    try:
        kafka_client.disconnect()
        logging.info("Cliente Kafka desconectado")
    except Exception as e:
        logging.error(f"Error al desconectar cliente Kafka: {e}")

    # Shutdown: Cerrar cliente de métricas
    await metrics_client.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configurar middleware de métricas
app.add_middleware(MetricsMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint


@app.get("/health", tags=["Health"])
async def health_check():
    kafka_status = kafka_client.circuit_breaker_status()
    return {
        "status": "healthy" if not kafka_status["open"] else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "kafka_circuit_breaker": kafka_status,
    }


# Incluir routers API v1
app.include_router(communications.router)
app.include_router(stream.router)

# Incluir routers públicos
app.include_router(public.router)
