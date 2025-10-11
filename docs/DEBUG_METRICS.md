# 🐛 Debug de Métricas

Guía para debuggear y entender qué peticiones están incrementando tus métricas de StatsD.

## 📊 Problema Común

Si ves incrementos en la métrica `siscom_api.requests` pero no estás haciendo peticiones a la API, puede deberse a:

1. **Health checks automáticos** de Docker (cada 30s por defecto)
2. **Monitoring externo** (AWS, Datadog, etc.)
3. **Bots y crawlers** buscando vulnerabilidades
4. **Reconexiones SSE** automáticas del cliente

## 🔍 Cómo Investigar

### 1. Revisar Logs en Producción (EC2)

```bash
# Ver los últimos 100 logs
docker logs siscom-api --tail 100

# Seguir logs en tiempo real
docker logs siscom-api -f

# Filtrar solo peticiones contadas
docker logs siscom-api | grep "📊 Contando métrica"

# Ver todas las peticiones (incluyendo excluidas)
docker logs siscom-api | grep "📨 Request"
```

### 2. Entender los Logs

El middleware genera estos logs:

```
📨 Request: GET /health | Client: 172.17.0.1 | User-Agent: python-requests/2.28.0
⏭️  Ruta excluida de métricas: /health
```
☝️ **NO se cuenta** en métricas

```
📨 Request: GET /api/v1/communications | Client: 203.0.113.5 | User-Agent: Mozilla/5.0...
📊 Contando métrica para: GET /api/v1/communications
⏱️  Latencia: GET /api/v1/communications -> 125.45ms | Status: 200
```
☝️ **SÍ se cuenta** en métricas

### 3. Rutas Excluidas (NO se cuentan)

Estas rutas están configuradas en `EXCLUDED_PATHS` y **NO** incrementan la métrica:

- `/health` - Health check de Docker
- `/docs` - Documentación Swagger
- `/openapi.json` - Schema OpenAPI
- `/favicon.ico` - Icono del navegador

Ver: `app/core/middleware.py` línea 11

### 4. Probar Localmente

```bash
# Ejecutar el script de prueba
./scripts/test_middleware_logging.sh

# O hacer peticiones manualmente
curl http://localhost:8000/health          # ❌ NO cuenta
curl http://localhost:8000/docs            # ❌ NO cuenta
curl http://localhost:8000/api/v1/communications  # ✅ SÍ cuenta
```

## 🔧 Agregar Más Rutas Excluidas

Si descubres que alguna ruta está generando mucho tráfico y no quieres contarla:

**Edita `app/core/middleware.py`:**

```python
EXCLUDED_PATHS = {
    "/health", 
    "/docs", 
    "/openapi.json", 
    "/favicon.ico",
    "/metrics",        # 👈 Agregar aquí
    "/static",         # 👈 Excluir archivos estáticos
}
```

## 📈 Verificar Métricas en InfluxDB

```bash
# Consulta en InfluxDB para ver incrementos por minuto
flux query '
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> aggregateWindow(every: 1m, fn: sum)
'
```

## 🚨 Casos Comunes

### Caso 1: Health Checks de Docker

**Síntoma:** Incremento cada ~30 segundos

**Solución:** Ya está excluido `/health`. Si persiste, verifica que el health check en `docker-compose.yml` use esa ruta.

### Caso 2: Bots y Crawlers

**Síntoma:** Peticiones aleatorias a rutas como `/`, `/.env`, `/admin`, etc.

**Log esperado:**
```
📨 Request: GET /.env | Client: 185.220.101.45 | User-Agent: python-requests
📊 Contando métrica para: GET /.env
⏱️  Latencia: GET /.env -> 12.34ms | Status: 404
```

**Solución:** 
- Es normal, son bots buscando vulnerabilidades
- Considera agregar rate limiting si es excesivo
- Puedes excluir rutas comunes de bots si no te interesan en métricas

### Caso 3: Cliente SSE Reconectando

**Síntoma:** Múltiples peticiones a `/stream` o `/api/v1/communications/stream`

**Log esperado:**
```
📨 Request: GET /api/v1/communications/stream | Client: 203.0.113.5
📊 Contando métrica para: GET /api/v1/communications/stream
INFO: Incrementando conexiones SSE activas
```

**Solución:** Es comportamiento normal. El cliente SSE reconecta automáticamente si se pierde la conexión.

## 🛠️ Configuración de Logging

Si quieres **más o menos detalle** en los logs:

**Edita `app/main.py` o crea `app/core/logging_config.py`:**

```python
import logging

# Nivel de log para el middleware
logging.getLogger("app.core.middleware").setLevel(logging.INFO)  # INFO, DEBUG, WARNING

# Nivel general de la app
logging.basicConfig(level=logging.INFO)
```

## 📝 Checklist de Debug

- [ ] Verificar logs con `docker logs siscom-api | grep "📊"`
- [ ] Identificar qué rutas están siendo contadas
- [ ] Verificar el `User-Agent` y `Client IP` en los logs
- [ ] Confirmar que las rutas esperadas estén en `EXCLUDED_PATHS`
- [ ] Probar localmente con `test_middleware_logging.sh`
- [ ] Revisar métricas en InfluxDB/Grafana
- [ ] Si es necesario, agregar más rutas a `EXCLUDED_PATHS`

## 🔗 Referencias

- [app/core/middleware.py](../app/core/middleware.py) - Código del middleware
- [METRICS.md](./METRICS.md) - Documentación de métricas
- [docker-compose.yml](../docker-compose.yml) - Configuración de health checks

