# Métricas de siscom-api

Este documento describe las métricas que la API envía a Telegraf mediante el protocolo StatsD para su posterior envío a InfluxDB.

## Configuración

### Variables de entorno

Agrega las siguientes variables a tu archivo `.env`:

```bash
# Configuración de StatsD (Telegraf)
STATSD_HOST=localhost
STATSD_PORT=8125
STATSD_PREFIX=siscom_api
```

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

La implementación usa **aio-statsd**, una librería asíncrona de StatsD que se integra perfectamente con FastAPI y asyncio.

## Métricas disponibles

Todas las métricas incluyen el tag `app=siscom-api` para identificar la aplicación de origen.

### 1. Peticiones por minuto

**Métrica:** `siscom_api.requests`  
**Tipo:** Counter  
**Descripción:** Contador incremental de todas las peticiones HTTP recibidas por la API.  
**Tag:** `app=siscom-api`

**Cómo calcular peticiones por minuto en InfluxDB:**

```flux
from(bucket: "your-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r.app == "siscom-api")
  |> derivative(unit: 1m, nonNegative: true)
```

### 2. Latencia del endpoint /stream

**Métrica:** `siscom_api.latency.stream`  
**Tipo:** Timing  
**Descripción:** Tiempo de respuesta del endpoint `/stream` en milisegundos.  
**Tag:** `app=siscom-api`

Esta métrica genera automáticamente las siguientes sub-métricas en Telegraf:

- `siscom_api.latency.stream.mean` - Latencia media
- `siscom_api.latency.stream.median` - Percentil 50
- `siscom_api.latency.stream.p90` - Percentil 90
- `siscom_api.latency.stream.p95` - Percentil 95
- `siscom_api.latency.stream.p99` - Percentil 99

**Consulta en InfluxDB (latencia media):**

```flux
from(bucket: "your-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
  |> filter(fn: (r) => r._field == "mean")
  |> filter(fn: (r) => r.app == "siscom-api")
```

### 3. Conexiones SSE activas

**Métrica:** `siscom_api.sse.active_connections`  
**Tipo:** Counter (usado como gauge)  
**Descripción:** Número actual de conexiones Server-Sent Events activas.  
**Tag:** `app=siscom-api`

Esta métrica se incrementa cuando un cliente se conecta a cualquier endpoint SSE y se decrementa cuando se desconecta.

**Endpoints SSE monitoreados:**

- `/stream?device_ids=...`
- `/api/v1/communications/stream?device_ids=...`
- `/api/v1/devices/{device_id}/communications/stream`

**Consulta en InfluxDB:**

```flux
from(bucket: "your-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.sse.active_connections")
  |> filter(fn: (r) => r.app == "siscom-api")
```

## Arquitectura

La implementación usa **aio-statsd**, una librería asíncrona que:

- ✅ Es completamente asíncrona (compatible con FastAPI y asyncio)
- ✅ No bloquea el event loop
- ✅ Usa UDP para no afectar el rendimiento
- ✅ Soporta tags en formato InfluxDB
- ✅ Maneja la conexión y desconexión automáticamente

### Componentes

1. **`app/utils/metrics.py`** - Cliente asíncrono de métricas
   - Instancia global `metrics_client`
   - Métodos asíncronos para enviar métricas
   - Conexión automática en startup
   - Cierre automático en shutdown

2. **`app/core/middleware.py`** - Middleware de métricas
   - Captura todas las peticiones HTTP
   - Mide latencia de endpoints `/stream`
   - Todo asíncrono con `await`

3. **`app/main.py`** - Inicialización
   - Usa `lifespan` de FastAPI
   - Conecta cliente en startup
   - Cierra cliente en shutdown

4. **Endpoints SSE** - Instrumentación directa
   - Incrementa contador al conectar
   - Decrementa contador al desconectar
   - Detecta desconexiones con `request.is_disconnected()`

## Configuración de Telegraf

### Opción 1: Telegraf en el mismo host

Si Telegraf está corriendo en el mismo servidor que la API (como container en la misma EC2), usa la configuración por defecto:

```bash
STATSD_HOST=localhost
STATSD_PORT=8125
```

### Opción 2: Telegraf en Docker

Si Telegraf está en un container Docker, asegúrate de que puede recibir tráfico UDP en el puerto 8125:

**docker-compose.yml de Telegraf:**

```yaml
services:
  telegraf:
    image: telegraf:latest
    ports:
      - "8125:8125/udp" # Puerto StatsD
    volumes:
      - ./telegraf-statsd.conf:/etc/telegraf/telegraf.conf:ro
    environment:
      - INFLUX_TOKEN=${INFLUX_TOKEN}
      - INFLUX_ORG=${INFLUX_ORG}
      - INFLUX_BUCKET=${INFLUX_BUCKET}
```

Luego configura la API para apuntar al host correcto:

```bash
# Si estás usando docker-compose para ambos servicios
STATSD_HOST=telegraf

# Si están en containers separados pero en el mismo host
STATSD_HOST=172.17.0.1  # IP del gateway de Docker
```

### Opción 3: Network host mode

Si usas `network_mode: host` en tu container, usa:

```bash
STATSD_HOST=localhost
STATSD_PORT=8125
```

## Verificación

### 1. Verificar que la API está enviando métricas

Inicia la API y haz algunas peticiones. Las métricas se envían automáticamente.

### 2. Verificar que Telegraf está recibiendo métricas

Revisa los logs de Telegraf:

```bash
docker logs telegraf
```

### 3. Consultar métricas en InfluxDB

Usa el Data Explorer de InfluxDB o la CLI:

```bash
influx query 'from(bucket:"your-bucket") |> range(start: -1h) |> filter(fn: (r) => r._measurement =~ /siscom_api/)'
```

## Dashboards recomendados

### Grafana

Puedes crear un dashboard en Grafana con los siguientes paneles:

1. **Peticiones por minuto** - Gráfico de líneas

   ```flux
   from(bucket: "your-bucket")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r._measurement == "siscom_api.requests")
     |> filter(fn: (r) => r.app == "siscom-api")
     |> derivative(unit: 1m, nonNegative: true)
   ```

2. **Latencia media del endpoint /stream** - Gráfico de líneas

   ```flux
   from(bucket: "your-bucket")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
     |> filter(fn: (r) => r._field == "mean")
     |> filter(fn: (r) => r.app == "siscom-api")
   ```

3. **Conexiones SSE activas** - Gauge o gráfico de líneas

   ```flux
   from(bucket: "your-bucket")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r._measurement == "siscom_api.sse.active_connections")
     |> filter(fn: (r) => r.app == "siscom-api")
     |> last()
   ```

4. **Percentiles de latencia** (P50, P90, P95, P99) - Gráfico de líneas múltiples

   ```flux
   from(bucket: "your-bucket")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
     |> filter(fn: (r) => r._field =~ /p50|p90|p95|p99/)
     |> filter(fn: (r) => r.app == "siscom-api")
   ```

## Troubleshooting

### Las métricas no aparecen en InfluxDB

1. Verifica que Telegraf está corriendo: `docker ps | grep telegraf`
2. Verifica que el puerto 8125/udp está abierto: `netstat -ulnp | grep 8125`
3. Verifica los logs de Telegraf: `docker logs telegraf`
4. Verifica la configuración de red entre la API y Telegraf
5. Prueba enviar métricas manualmente:

   ```bash
   echo "siscom_api.test,app=siscom-api:1|c" | nc -u -w1 localhost 8125
   ```

### Las métricas aparecen pero sin el tag "app"

**aio-statsd** envía tags en formato InfluxDB (`metric,tag1=value1,tag2=value2:value|type`). Verifica que:

1. Tu versión de Telegraf es 1.9.0 o superior
2. El plugin `[[inputs.statsd]]` está configurado correctamente en Telegraf
3. La configuración de Telegraf **NO** tiene `parse_data_dog_tags = true` (ya que usamos formato InfluxDB, no Datadog)

### Errores de conexión

Si ves errores tipo "Connection refused" o "Network unreachable":

1. Verifica que `STATSD_HOST` apunta al host correcto
2. Si estás en Docker, verifica que los containers pueden comunicarse
3. Verifica que el puerto 8125/udp no está bloqueado por firewall
4. Prueba con `telnet` o `nc`:

   ```bash
   # Desde el container/host de la API
   nc -u -v -z localhost 8125
   ```

### La API no inicia

Si la API no puede iniciar después de agregar las métricas:

1. Verifica que instalaste `aio-statsd`: `pip install -r requirements.txt`
2. Verifica que las variables de entorno están configuradas
3. Revisa los logs de la API para errores específicos
4. El cliente de métricas no debería bloquear el inicio incluso si Telegraf no está disponible

## Ventajas de aio-statsd

- ✅ **Asíncrono:** No bloquea el event loop de FastAPI
- ✅ **Sin overhead:** Usa UDP, no impacta el rendimiento
- ✅ **Automático:** Se conecta y desconecta automáticamente
- ✅ **Compatible:** Formato de tags compatible con Telegraf
- ✅ **Robusto:** Maneja errores de red sin afectar la API

## Notas adicionales

- Las métricas usan UDP, por lo que no bloquean la API si Telegraf no está disponible
- UDP no garantiza entrega, algunas métricas podrían perderse en redes saturadas
- Los contadores son incrementales, útiles para calcular tasas (rate)
- Los timings generan múltiples estadísticas automáticamente (mean, median, percentiles)
- **aio-statsd** maneja buffers internos para optimizar el envío de métricas
- La conexión se mantiene abierta durante toda la vida de la aplicación
