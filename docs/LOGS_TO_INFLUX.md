# 📝 Enviar Logs a InfluxDB con Telegraf

Guía para configurar el envío de logs de siscom-api a InfluxDB usando Telegraf.

## 🎯 Opción Recomendada: `docker_log` Input

Similar a tu aplicación Rust `siscom-test`, usa el plugin `docker_log` de Telegraf.

### ✅ Ventajas
- ✅ Consistente con tu setup actual (siscom-test)
- ✅ No requiere montar volúmenes
- ✅ Captura automáticamente stdout/stderr del contenedor
- ✅ Fácil de mantener
- ✅ Sin archivos de log en disco

### 📝 Configuración en telegraf.conf

Agrega esto a tu `telegraf.conf` junto al input de `siscom-test`:

```toml
# ====================
# Input: Docker Logs de siscom-api
# ====================
[[inputs.docker_log]]
  endpoint = "unix:///var/run/docker.sock"
  from_beginning = false
  container_name_include = ["siscom-api"]  # Nombre del contenedor
  
  [inputs.docker_log.tags]
    source = "siscom-api"
    app = "siscom-api"
```

### 🔧 Procesador de Logs (Opcional pero Recomendado)

Si quieres parsear los logs para extraer nivel (INFO, ERROR, etc.):

```toml
# Procesador para siscom-api logs
[[processors.regex]]
  namepass = ["docker_log"]  # Solo aplica a docker_log
  
  [[processors.regex.tags]]
    key = "source"
    pattern = "^siscom-api$"  # Solo logs de siscom-api
  
  [[processors.regex.fields]]
    key = "message"
    # Parsea logs de FastAPI/Uvicorn:
    # 2024-10-12 15:30:45 - app.core.middleware - INFO - 📨 Request: GET /health
    pattern = '^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+-\s+(?P<logger>\S+)\s+-\s+(?P<level>INFO|ERROR|WARNING|DEBUG)\s+-\s+(?P<msg>.*)$'
    result_key = "parsed"
```

### 🔍 Formato de Logs en InfluxDB

Los logs llegarán con esta estructura:

```
Measurement: docker_log
Tags:
  - source: siscom-api
  - container_name: siscom-api
  - container_image: siscom-api:latest
Fields:
  - message: "2024-10-12 - INFO - 📨 Request: GET /health"
  - container_id: "abc123..."
```

Con el procesador opcional:
```
Fields adicionales:
  - timestamp: "2024-10-12 15:30:45"
  - logger: "app.core.middleware"
  - level: "INFO"
  - msg: "📨 Request: GET /health"
```

---

## 🗂️ Opción 2: `tail` Input (Alternativa)

Similar a tu `/siscom/siscom.log` de Rust, pero requiere más configuración.

### ⚠️ Desventajas
- ❌ Requiere montar volumen para logs
- ❌ Requiere configurar logging a archivo en Python
- ❌ Más complejo de mantener
- ❌ Ocupa espacio en disco

### 📝 Si prefieres esta opción:

**1. Crear directorio de logs en docker-compose.yml:**

```yaml
services:
  siscom-api:
    # ... resto de config
    volumes:
      - ./logs:/app/logs:rw  # Montar carpeta de logs
```

**2. Configurar logging a archivo en Python:**

Editar `app/main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging a archivo Y consola
file_handler = RotatingFileHandler(
    "/app/logs/siscom-api.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
```

**3. Configurar Telegraf:**

```toml
[[inputs.tail]]
  files = ["/app/logs/siscom-api.log"]
  from_beginning = false
  name_override = "siscom_api_logs"
  
  # Parsear formato de Python logging
  data_format = "grok"
  grok_patterns = [
    "%{TIMESTAMP_ISO8601:timestamp} - %{DATA:logger} - %{LOGLEVEL:level} - %{GREEDYDATA:message}"
  ]
  grok_timezone = "UTC"
  
  [inputs.tail.tags]
    source = "siscom-api"
```

**4. Montar el log en Telegraf:**

```yaml
telegraf:
  volumes:
    - ./logs:/app/logs:ro  # Read-only
```

---

## 🎨 Comparación de Opciones

| Aspecto | docker_log ✅ | tail |
|---------|---------------|------|
| **Simplicidad** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Mantenimiento** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Espacio en disco** | ⭐⭐⭐⭐⭐ (no usa) | ⭐⭐ (usa disco) |
| **Setup inicial** | ⭐⭐⭐⭐⭐ (1 minuto) | ⭐⭐ (10+ minutos) |
| **Rotación de logs** | ⭐⭐⭐⭐⭐ (automático) | ⭐⭐⭐ (manual) |
| **Consistencia** | ⭐⭐⭐⭐⭐ (igual que rust) | ⭐⭐⭐ (diferente) |

---

## 🚀 Configuración Recomendada Completa

Agrega esto a tu `telegraf.conf` existente:

```toml
# ====================
# Input: Docker Logs de siscom-api (FastAPI/Python)
# ====================
[[inputs.docker_log]]
  endpoint = "unix:///var/run/docker.sock"
  from_beginning = false
  container_name_include = ["siscom-api"]
  
  [inputs.docker_log.tags]
    source = "siscom-api"
    language = "python"
    framework = "fastapi"

# ====================
# Procesador: Parsear logs de siscom-api
# ====================
[[processors.regex]]
  order = 1
  namepass = ["docker_log"]
  
  # Solo aplicar a logs de siscom-api
  [[processors.regex.tagpass]]
    source = ["siscom-api"]
  
  # Parsear logs de Python logging con emojis
  [[processors.regex.fields]]
    key = "message"
    # Formato: 2024-10-12 15:30:45 - app.core.middleware - INFO - 📨 Request: GET /health
    pattern = '^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+-\s+(\S+)\s+-\s+(INFO|ERROR|WARNING|DEBUG)\s+-\s+(.*)$'
    result_key = "parsed_log"
  
  # Extraer nivel de log como tag (para facilitar filtrado en Grafana)
  [[processors.regex.tags]]
    key = "message"
    pattern = '.*(INFO|ERROR|WARNING|DEBUG).*'
    replacement = '${1}'
    result_key = "log_level"
```

### 🔧 Asegurar que Docker Socket esté Montado

Verifica que tu `docker-compose.yml` de Telegraf tenga:

```yaml
telegraf:
  image: telegraf:latest
  volumes:
    - ./telegraf.conf:/etc/telegraf/telegraf.conf:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro  # ⚠️ IMPORTANTE
  # ... resto de config
```

---

## 📊 Queries de Grafana para Logs

### 1. Ver Logs Recientes

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "docker_log")
  |> filter(fn: (r) => r.source == "siscom-api")
  |> filter(fn: (r) => r._field == "message")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 100)
```

### 2. Filtrar Solo Errores

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "docker_log")
  |> filter(fn: (r) => r.source == "siscom-api")
  |> filter(fn: (r) => r.log_level == "ERROR")
  |> filter(fn: (r) => r._field == "message")
```

### 3. Contar Errores por Minuto

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "docker_log")
  |> filter(fn: (r) => r.source == "siscom-api")
  |> filter(fn: (r) => r.log_level == "ERROR")
  |> aggregateWindow(every: 1m, fn: count)
```

### 4. Panel de Logs en Grafana

Panel tipo: **Logs**

Query:
```flux
from(bucket: "siscom")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "docker_log")
  |> filter(fn: (r) => r.source == "siscom-api")
  |> filter(fn: (r) => r._field == "message")
```

---

## 🎯 Resumen: Qué Hacer

### Paso 1: Actualizar telegraf.conf

Agrega el bloque `[[inputs.docker_log]]` para `siscom-api` (ver arriba).

### Paso 2: Verificar Docker Socket

Asegúrate que Telegraf tenga acceso a `/var/run/docker.sock`.

### Paso 3: Reiniciar Telegraf

```bash
docker restart telegraf
```

### Paso 4: Verificar en InfluxDB

```bash
# Listar measurements
influx query 'from(bucket: "siscom") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "docker_log")'
```

### Paso 5: Crear Panel en Grafana

Usa las queries de arriba para crear paneles de logs.

---

## 🔍 Troubleshooting

### No veo logs en InfluxDB

1. **Verificar que Telegraf tenga acceso al socket:**
   ```bash
   docker exec telegraf ls -la /var/run/docker.sock
   ```

2. **Ver logs de Telegraf:**
   ```bash
   docker logs telegraf | grep docker_log
   ```

3. **Verificar nombre del contenedor:**
   ```bash
   docker ps --format "{{.Names}}"
   # Debe aparecer "siscom-api"
   ```

### Logs no se parsean

1. **Verificar formato de logs:**
   ```bash
   docker logs siscom-api --tail 10
   ```

2. **Ajustar regex en el procesador** según el formato real de tus logs.

---

## 📝 Ejemplo de Telegraf Config Completo

```toml
# Logs de siscom-test (Rust) - YA LO TIENES
[[inputs.docker_log]]
  endpoint = "unix:///var/run/docker.sock"
  from_beginning = false
  container_name_include = ["siscom-test"]
  [inputs.docker_log.tags]
    source = "siscom-test"

# Logs de siscom-api (Python/FastAPI) - NUEVO
[[inputs.docker_log]]
  endpoint = "unix:///var/run/docker.sock"
  from_beginning = false
  container_name_include = ["siscom-api"]
  [inputs.docker_log.tags]
    source = "siscom-api"

# Procesador para ambos (opcional)
[[processors.regex]]
  namepass = ["docker_log"]
  
  [[processors.regex.tags]]
    key = "message"
    pattern = '.*(INFO|ERROR|WARNING|DEBUG|WARN).*'
    replacement = '${1}'
    result_key = "log_level"
```

---

## ✅ Checklist

- [ ] Agregar `[[inputs.docker_log]]` para siscom-api en telegraf.conf
- [ ] Verificar que `/var/run/docker.sock` esté montado en Telegraf
- [ ] Agregar tags `source = "siscom-api"`
- [ ] Opcional: Agregar procesador regex para parsear logs
- [ ] Reiniciar Telegraf
- [ ] Verificar en InfluxDB que llegan los logs
- [ ] Crear panel de logs en Grafana
- [ ] Crear alerta para errores (opcional)

---

## 🔗 Referencias

- Plugin docker_log de Telegraf: https://github.com/influxdata/telegraf/tree/master/plugins/inputs/docker_log
- Processors de Telegraf: https://github.com/influxdata/telegraf/tree/master/plugins/processors/regex
- Logs Panel en Grafana: https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/logs/

