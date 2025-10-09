# Changelog - Implementación de Métricas con aio-statsd

## Resumen

Se ha implementado un sistema completo de métricas que envía automáticamente estadísticas de la API a Telegraf mediante el protocolo StatsD usando **aio-statsd**, una librería asíncrona optimizada para FastAPI.

## ✅ Cambios Implementados

### Archivos Nuevos Creados

1. **`app/utils/metrics.py`**
   - Cliente **aio-statsd** configurado (asíncrono)
   - Métodos async para incrementar contadores, registrar latencias y actualizar gauges
   - Tag `app=siscom-api` incluido en todas las métricas
   - Conexión y desconexión manejadas automáticamente

2. **`app/core/middleware.py`**
   - Middleware asíncrono que captura automáticamente:
     - Todas las peticiones HTTP (incrementa contador con `await`)
     - Latencia específica del endpoint `/stream` (en milisegundos)

3. **`telegraf-statsd.conf`**
   - Archivo de configuración de ejemplo para Telegraf
   - Configurado para recibir métricas StatsD en puerto 8125
   - Configurado para enviar métricas a InfluxDB v2
   - **Importante:** Configurado para formato de tags InfluxDB (no Datadog)
   - Incluye documentación de las métricas generadas

4. **`METRICS.md`**
   - Documentación completa del sistema de métricas
   - Guía de configuración detallada
   - Ejemplos de consultas en InfluxDB (Flux)
   - Sección de troubleshooting específica para aio-statsd
   - Explicación de las ventajas de aio-statsd vs statsd sincrónica

5. **`QUICKSTART_METRICS.md`**
   - Guía rápida de configuración paso a paso
   - Instrucciones para diferentes escenarios de deployment
   - Comandos de verificación y troubleshooting
   - Sección de diferencias con statsd sincrónica

6. **`test_metrics.py`**
   - Script asíncrono de prueba para verificar que las métricas funcionan
   - Usa `asyncio.run()` para ejecutar tests async
   - Envía métricas de ejemplo a Telegraf
   - Útil para validar la conectividad

### Archivos Modificados

1. **`requirements.txt`**
   - ✅ Agregada dependencia: `aio-statsd` (librería asíncrona)

2. **`app/core/config.py`**
   - ✅ Agregadas variables de configuración:
     - `STATSD_HOST` (default: localhost)
     - `STATSD_PORT` (default: 8125)
     - `STATSD_PREFIX` (default: siscom_api)

3. **`app/main.py`**
   - ✅ Importado `MetricsMiddleware`
   - ✅ Agregado middleware de métricas a la aplicación
   - ✅ **Implementado `lifespan` context manager:**
     - Conecta el cliente de métricas en startup
     - Cierra el cliente de métricas en shutdown
   - ✅ Uso de `asynccontextmanager` para manejo del ciclo de vida

4. **`app/api/routes/stream.py`**
   - ✅ Importado `metrics_client` y `Request`
   - ✅ Modificado `event_generator` para:
     - Recibir parámetro `request: Request`
     - `await metrics_client.increment_active_connections()` al conectar
     - `await metrics_client.decrement_active_connections()` al desconectar
     - Detectar desconexiones del cliente con `await request.is_disconnected()`
   - ✅ Agregado parámetro `Request` al endpoint

5. **`app/api/routes/communications.py`**
   - ✅ Importados `Request` y `metrics_client`
   - ✅ Modificado `event_generator` para:
     - Recibir parámetro `request: Request`
     - `await metrics_client.increment_active_connections()` al conectar
     - `await metrics_client.decrement_active_connections()` al desconectar
     - Detectar desconexiones del cliente con `await request.is_disconnected()`
   - ✅ Agregado parámetro `Request` a ambos endpoints SSE:
     - `/api/v1/communications/stream`
     - `/api/v1/devices/{device_id}/communications/stream`

6. **`README.md`**
   - ✅ Agregada característica "Métricas StatsD con aio-statsd" en la lista principal
   - ✅ Agregadas variables de StatsD en la configuración de ejemplo
   - ✅ Nueva sección completa "📊 Métricas y Monitoreo"
   - ✅ Sección explicando ventajas de aio-statsd
   - ✅ Actualizada arquitectura del proyecto
   - ✅ Marcadas métricas como implementadas en "Mejoras Sugeridas"

## 📊 Métricas Implementadas

### 1. Peticiones por minuto
- **Métrica:** `siscom_api.requests`
- **Tipo:** Counter
- **Descripción:** Cuenta todas las peticiones HTTP recibidas
- **Tag:** `app=siscom-api`
- **Captura:** Middleware automático asíncrono en todas las peticiones

### 2. Latencia del endpoint /stream
- **Métrica:** `siscom_api.latency.stream`
- **Tipo:** Timing
- **Descripción:** Tiempo de respuesta del endpoint /stream en milisegundos
- **Tag:** `app=siscom-api`
- **Captura:** Middleware automático asíncrono en peticiones a `/stream`
- **Sub-métricas generadas por Telegraf:**
  - `siscom_api.latency.stream.mean` (media)
  - `siscom_api.latency.stream.median` (p50)
  - `siscom_api.latency.stream.p90`
  - `siscom_api.latency.stream.p95`
  - `siscom_api.latency.stream.p99`

### 3. Conexiones SSE activas
- **Métrica:** `siscom_api.sse.active_connections`
- **Tipo:** Counter (usado como gauge)
- **Descripción:** Número actual de conexiones Server-Sent Events
- **Tag:** `app=siscom-api`
- **Captura:** Endpoints SSE instrumentados directamente con async/await
- **Endpoints monitoreados:**
  - `/stream`
  - `/api/v1/communications/stream`
  - `/api/v1/devices/{device_id}/communications/stream`

## 🔧 Configuración Requerida

### Variables de Entorno (.env)

```bash
# Agregar estas líneas a tu .env
STATSD_HOST=localhost
STATSD_PORT=8125
STATSD_PREFIX=siscom_api
```

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará **aio-statsd**, una librería asíncrona específicamente diseñada para asyncio.

## 🚀 Cómo Usar

### Paso 1: Configurar Telegraf

Si Telegraf ya está corriendo en tu EC2:

```bash
# Copiar o fusionar la configuración
cp telegraf-statsd.conf /path/to/telegraf/telegraf.conf

# Reiniciar Telegraf
docker restart telegraf
# o
systemctl restart telegraf
```

**IMPORTANTE:** Asegúrate de que en la configuración de Telegraf:
- `parse_data_dog_tags = false` (o no esté presente)
- Porque aio-statsd usa formato InfluxDB, no Datadog

### Paso 2: Actualizar variables de entorno

```bash
# Editar .env
nano .env

# Agregar:
STATSD_HOST=localhost  # o IP del container de Telegraf
STATSD_PORT=8125
STATSD_PREFIX=siscom_api
```

### Paso 3: Instalar dependencias y reiniciar API

```bash
# Instalar nueva dependencia
pip install -r requirements.txt

# Reiniciar la API
docker-compose restart siscom-api
# o
systemctl restart siscom-api
```

### Paso 4: Verificar

```bash
# Probar envío de métricas
python test_metrics.py

# Verificar en InfluxDB
# Ver METRICS.md para consultas de ejemplo
```

## 🎯 Ventajas de aio-statsd

### Comparación con statsd (sincrónica)

| Característica | statsd (sincrónica) | aio-statsd (asíncrona) |
|----------------|---------------------|------------------------|
| Compatibilidad asyncio | ❌ No | ✅ Sí |
| Bloquea event loop | ⚠️ Posible | ✅ No |
| Formato de tags | Datadog | InfluxDB (nativo) |
| Gestión de conexión | Manual | Automática |
| Rendimiento en FastAPI | ⚠️ Aceptable | ✅ Óptimo |
| Buffer interno | Básico | Optimizado |

### Características clave de aio-statsd

1. **Totalmente asíncrono:** Todos los métodos usan `await`, no bloquean el event loop
2. **Lifecycle automático:** Se conecta en startup y cierra en shutdown
3. **Tags nativos InfluxDB:** Formato `metric,tag1=value1,tag2=value2:value|type`
4. **Buffer optimizado:** Agrupa métricas para reducir paquetes UDP
5. **Error handling:** Maneja errores de red sin impactar la aplicación

## 🔄 Diferencias de Implementación

### Antes (statsd sincrónica)
```python
from statsd import StatsClient

client = StatsClient(host="localhost", port=8125, prefix="siscom_api")
client.incr("requests", tags=["app:siscom-api"])  # Sincrónico
```

### Ahora (aio-statsd asíncrona)
```python
import aiostatsd

client = aiostatsd.Client(host="localhost", port=8125, prefix="siscom_api")
await client.increment("requests,app=siscom-api")  # Asíncrono con await
```

### Lifecycle Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await metrics_client.connect()
    yield
    # Shutdown
    await metrics_client.close()

app = FastAPI(lifespan=lifespan)
```

## 📚 Documentación

- **Guía rápida:** `QUICKSTART_METRICS.md`
- **Documentación completa:** `METRICS.md`
- **Configuración Telegraf:** `telegraf-statsd.conf`
- **Script de prueba:** `test_metrics.py`

## ⚠️ Consideraciones

1. **Red:** Asegúrate de que la API puede alcanzar Telegraf en el puerto 8125/udp
2. **Firewall:** El puerto 8125/udp debe estar abierto
3. **Formato de tags:** aio-statsd usa formato InfluxDB (`metric,tag1=value1`), no Datadog
4. **UDP:** Algunas métricas podrían perderse en redes muy saturadas (por diseño de UDP)
5. **Async/await:** Todos los métodos de métricas deben llamarse con `await`

## 🐛 Troubleshooting

### Error: "coroutine was never awaited"

Si ves este error, significa que olvidaste usar `await` al llamar a los métodos de métricas:

```python
# ❌ Incorrecto
metrics_client.increment_requests()

# ✅ Correcto
await metrics_client.increment_requests()
```

### Tags no aparecen en InfluxDB

Verifica en la configuración de Telegraf:
```toml
[[inputs.statsd]]
  parse_data_dog_tags = false  # O elimina esta línea
```

**aio-statsd** usa formato InfluxDB por defecto, no Datadog.

Ver más troubleshooting en `METRICS.md`

## ✨ Próximos Pasos (Opcional)

1. Crear dashboards en Grafana para visualizar las métricas
2. Configurar alertas en InfluxDB para latencias altas o caídas de conexiones
3. Agregar más métricas según necesidades (ej: errores por tipo, peticiones por endpoint, etc.)
4. Implementar sampling para reducir volumen en ambientes de alto tráfico

---

**Fecha de implementación:** 8 de octubre de 2025  
**Versión:** Compatible con siscom-api v0.1.0+  
**Librería:** aio-statsd (asíncrona para asyncio/FastAPI)

