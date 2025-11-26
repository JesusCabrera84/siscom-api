import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import communications, stream
from app.core.config import settings
from app.core.database import engine
from app.core.middleware import MetricsMiddleware
from app.services.mqtt_client import mqtt_client
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

    # Startup: Conectar cliente MQTT
    try:
        mqtt_client.connect()
        logging.info("Cliente MQTT inicializado")
    except Exception as e:
        logging.error(f"Error al inicializar cliente MQTT: {e}")

    yield

    # Shutdown: Cerrar cliente MQTT
    try:
        mqtt_client.disconnect()
        logging.info("Cliente MQTT desconectado")
    except Exception as e:
        logging.error(f"Error al desconectar cliente MQTT: {e}")

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
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Incluir routers API v1
app.include_router(communications.router)
app.include_router(stream.router)
