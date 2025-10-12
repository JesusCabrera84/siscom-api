# Guía Rápida: Configuración de Métricas con aio-statsd

## 🎯 Resumen

Se han agregado 3 métricas principales a siscom-api que se envían automáticamente a Telegraf mediante StatsD usando **aio-statsd** (librería asíncrona):

1. **Peticiones por minuto** - Contador de todas las peticiones HTTP
2. **Latencia del endpoint /stream** - Tiempo de respuesta en milisegundos  
3. **Conexiones SSE activas** - Número de conexiones Server-Sent Events activas

Todas las métricas incluyen el tag `app=siscom-api`.

## ⚡ Configuración Rápida

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará **aio-statsd**, una librería asíncrona optimizada para FastAPI.

### 2. Configurar variables de entorno

Agrega estas líneas a tu archivo `.env`:

```bash
STATSD_HOST=localhost
STATSD_PORT=8125
STATSD_PREFIX=siscom_api
```

**Importante:** Si Telegraf está en un container Docker, ajusta `STATSD_HOST`:

- Mismo `docker-compose`: `STATSD_HOST=telegraf`
- Containers separados: `STATSD_HOST=172.17.0.1` (IP del gateway Docker)
- Host network mode: `STATSD_HOST=localhost`

### 3. Configurar Telegraf

Usa el archivo de configuración incluido: `telegraf-statsd.conf`

Configura las variables de entorno para InfluxDB:

```bash
export INFLUX_TOKEN="tu-token-aqui"
export INFLUX_ORG="tu-organizacion"
export INFLUX_BUCKET="tu-bucket"
```

### 4. Iniciar Telegraf (si está en Docker)

```bash
docker run -d --name telegraf \
  -p 8125:8125/udp \
  -v $(pwd)/telegraf-statsd.conf:/etc/telegraf/telegraf.conf:ro \
  -e INFLUX_TOKEN="${INFLUX_TOKEN}" \
  -e INFLUX_ORG="${INFLUX_ORG}" \
  -e INFLUX_BUCKET="${INFLUX_BUCKET}" \
  telegraf:latest
```

### 5. Reiniciar la API

```bash
# Si usas uvicorn directamente
uvicorn app.main:app --reload

# Si usas Docker Compose
docker-compose restart siscom-api
```

## 📊 Verificación

### Ver métricas en InfluxDB

```bash
# Listar todas las métricas de siscom-api
influx query '
from(bucket:"tu-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement =~ /siscom_api/)
  |> filter(fn: (r) => r.app == "siscom-api")
'
```

### Consultas útiles

**Peticiones por minuto:**

```flux
from(bucket: "tu-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r.app == "siscom-api")
  |> derivative(unit: 1m, nonNegative: true)
```

**Latencia media del endpoint /stream:**

```flux
from(bucket: "tu-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
  |> filter(fn: (r) => r._field == "mean")
  |> filter(fn: (r) => r.app == "siscom-api")
```

**Conexiones SSE activas:**

```flux
from(bucket: "tu-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.sse.active_connections")
  |> filter(fn: (r) => r.app == "siscom-api")
  |> last()
```

## 🔍 Troubleshooting

### Las métricas no llegan a InfluxDB

1. **Verificar que Telegraf está corriendo:**

   ```bash
   docker ps | grep telegraf
   # o
   systemctl status telegraf
   ```

2. **Verificar logs de Telegraf:**

   ```bash
   docker logs telegraf
   # o
   journalctl -u telegraf -f
   ```

3. **Verificar que el puerto 8125/udp está abierto:**

   ```bash
   netstat -ulnp | grep 8125
   ```

4. **Probar conectividad UDP:**

   ```bash
   # Enviar métrica de prueba con tags en formato InfluxDB
   echo "siscom_api.test,app=siscom-api:1|c" | nc -u -w1 localhost 8125
   ```

5. **Verificar configuración de red:**
   - Si API y Telegraf están en containers diferentes, verifica que pueden comunicarse
   - Prueba hacer ping desde el container de la API al de Telegraf
   - Revisa que el puerto 8125/udp está expuesto en Telegraf

### Las métricas aparecen sin el tag "app"

**aio-statsd** usa el formato de tags de InfluxDB (`metric,tag1=value1:value|type`). Verifica:

1. Tu versión de Telegraf es 1.9.0 o superior
2. El plugin `[[inputs.statsd]]` está configurado en Telegraf
3. **IMPORTANTE:** En la configuración de Telegraf, asegúrate de que `parse_data_dog_tags = false` (o no está presente), ya que **aio-statsd** usa formato InfluxDB, no Datadog

### Error "Connection refused" al iniciar la API

Esto es normal si Telegraf no está corriendo. **aio-statsd** usa UDP, que no requiere conexión establecida. La API debería iniciar correctamente incluso si Telegraf no está disponible.

Si la API no inicia por otros motivos:

1. Verifica que instalaste `aio-statsd`: `pip show aio-statsd`
2. Verifica las variables de entorno en `.env`
3. Revisa los logs de la API para errores específicos

## ✨ Ventajas de aio-statsd

- **Asíncrono:** Completamente compatible con FastAPI y asyncio
- **No bloqueante:** No afecta el rendimiento de la API
- **Automático:** Conexión y desconexión manejadas automáticamente
- **Formato nativo:** Tags en formato InfluxDB (más eficiente)
- **Robusto:** Maneja errores de red sin impactar la aplicación

## 🎉 ¡Listo

Las métricas ahora se están enviando automáticamente a Telegraf cada vez que:

- ✅ Se recibe una petición HTTP (cualquier endpoint)
- ✅ Se procesa una petición al endpoint `/stream` (se mide la latencia)
- ✅ Un cliente se conecta o desconecta de un endpoint SSE

**No necesitas hacer nada más en tu código**, el middleware y los endpoints ya están instrumentados con **aio-statsd**.

## 📚 Documentación completa

Ver [METRICS.md](METRICS.md) para documentación detallada.

## 🔧 Diferencias con statsd (sincrónica)

Si vienes de la implementación con `statsd` sincrónica, estos son los cambios principales:

1. **Async/await:** Todos los métodos ahora usan `await`

   ```python
   # Antes (statsd)
   metrics_client.increment("requests")
   
   # Ahora (aio-statsd)
   await metrics_client.increment_requests()
   ```

2. **Lifecycle management:** Conexión y cierre manejados en `lifespan` de FastAPI

   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       await metrics_client.connect()
       yield
       await metrics_client.close()
   ```

3. **Formato de tags:** InfluxDB nativo en lugar de Datadog

   ```python
   # aio-statsd usa: metric,tag1=value1,tag2=value2:value|type
   # En lugar de: metric:value|type|#tag1:value1,tag2:value2
   ```

4. **Sin bloqueo del event loop:** Completamente asíncrono, no bloquea ninguna operación
