# 📝 Cómo Agregar siscom-api a tu Telegraf Existente

## 🎯 Objetivo

Agregar soporte para las métricas de siscom-api **SIN modificar** tu configuración actual de Telegraf que ya funciona con otros proyectos.

## ✅ Solución: Puerto Dedicado

- **Puerto 8125** → Se mantiene para tus proyectos existentes (con `datadog_extensions = true`)
- **Puerto 8126** → Nuevo puerto dedicado para siscom-api (con `datadog_extensions = false`)

De esta forma, ambos formatos coexisten sin conflictos.

## 📋 Pasos a Seguir

### 1. Editar tu archivo telegraf.conf

```bash
# Abre tu configuración actual
nano /path/to/telegraf.conf
# o
vi /path/to/telegraf.conf
```

### 2. Agregar el nuevo bloque al FINAL

Busca tu sección actual `[[inputs.statsd]]` (que usa puerto 8125) y **DESPUÉS** de ella, agrega:

```toml
# ====================
# Input: StatsD para siscom-api en puerto 8126
# ====================
[[inputs.statsd]]
  # Puerto DEDICADO para siscom-api (no interfiere con 8125)
  service_address = ":8126"
  protocol = "udp"
  
  # Configuración para aio-statsd (formato InfluxDB)
  metric_separator = "."
  datadog_extensions = false        # aio-statsd usa formato InfluxDB
  
  # Percentiles para latencias
  percentiles = [50, 90, 95, 99]
  
  # Buffers
  allowed_pending_messages = 10000
  percentile_limit = 1000
  
  # Retención
  delete_gauges = false
  delete_counters = false
  delete_sets = false
  delete_timings = true
  
  # Tag para identificar origen
  [inputs.statsd.tags]
    source = "siscom-api"
```

### 3. Verificar que el output está configurado

Tu output `[[outputs.influxdb_v2]]` actual ya debería funcionar para ambos inputs. Si no tienes timeout, considera agregarlo:

```toml
[[outputs.influxdb_v2]]
  urls = ["${INFLUX_URL}"]
  token = "${INFLUX_TOKEN}"
  organization = "${INFLUX_ORG}"
  bucket = "${INFLUX_BUCKET}"
  timeout = "5s"  # Recomendado
```

### 4. Guardar y reiniciar Telegraf

```bash
# Guardar el archivo
# Luego reiniciar Telegraf

# Si usas Docker:
docker restart telegraf

# Si usas systemd:
systemctl restart telegraf

# Verificar logs
docker logs telegraf --tail 50
# o
journalctl -u telegraf -n 50
```

### 5. Verificar que ambos puertos están escuchando

```bash
netstat -ulnp | grep telegraf

# Deberías ver:
# *:8125 (tu configuración original)
# *:8126 (nueva configuración para siscom-api)
```

## 📊 Tu Configuración Final

Después de este cambio, tu telegraf.conf tendrá algo así:

```toml
[agent]
  interval = "10s"
  # ... tu config actual ...

# Tu input de StatsD ORIGINAL (se mantiene sin cambios)
[[inputs.statsd]]
  service_address = ":8125"
  protocol = "udp"
  metric_separator = "_"
  datadog_extensions = true        # Para tus otros proyectos
  # ... resto de tu config ...

# NUEVO: Input para siscom-api
[[inputs.statsd]]
  service_address = ":8126"
  protocol = "udp"
  metric_separator = "."
  datadog_extensions = false       # Para aio-statsd
  percentiles = [50, 90, 95, 99]
  allowed_pending_messages = 10000
  percentile_limit = 1000
  delete_gauges = false
  delete_counters = false
  delete_sets = false
  delete_timings = true
  
  [inputs.statsd.tags]
    source = "siscom-api"

# Tus inputs existentes (se mantienen sin cambios)
[[inputs.tail]]
  # ... tu config ...

[[inputs.docker_log]]
  # ... tu config ...

[[processors.regex]]
  # ... tu config ...

# Tu output (se mantiene sin cambios, recibe de AMBOS inputs)
[[outputs.influxdb_v2]]
  urls = ["${INFLUX_URL}"]
  token = "${INFLUX_TOKEN}"
  organization = "${INFLUX_ORG}"
  bucket = "${INFLUX_BUCKET}"
```

## 🔍 Verificación

### 1. Prueba el puerto original (8125)

```bash
# Tus proyectos existentes deben seguir funcionando
echo "test:1|c" | nc -u -w1 localhost 8125
```

### 2. Prueba el nuevo puerto (8126)

```bash
# Prueba con siscom-api
echo "siscom_api.test,app=siscom-api:1|c" | nc -u -w1 localhost 8126
```

### 3. Verifica en InfluxDB

```bash
# Ver métricas de siscom-api
influx query 'from(bucket:"siscom") 
  |> range(start: -10m) 
  |> filter(fn: (r) => r.source == "siscom-api")
  |> limit(n: 10)'
```

## 🚀 Configurar siscom-api

En GitHub, asegúrate de configurar las variables con el **puerto 8126**:

```
STATSD_HOST = localhost    (o la IP de tu servidor Telegraf)
STATSD_PORT = 8126         ← IMPORTANTE: 8126, no 8125
STATSD_PREFIX = siscom_api
```

Ver [GITHUB_VARIABLES.md](GITHUB_VARIABLES.md) para más detalles.

## ✨ Ventajas de Este Enfoque

1. ✅ **No modificas** tu configuración existente que ya funciona
2. ✅ **Tus otros proyectos** siguen usando 8125 sin cambios
3. ✅ **siscom-api** tiene su propio puerto (8126) con la configuración correcta
4. ✅ **Ambos formatos** (Datadog e InfluxDB) coexisten sin conflictos
5. ✅ **Fácil de identificar** métricas por el tag `source=siscom-api`

## 📦 Archivo de Referencia

También puedes usar el archivo [`telegraf-siscom-addon.conf`](../telegraf-siscom-addon.conf) como referencia que contiene solo el bloque a agregar.

## 🆘 Troubleshooting

### No veo el puerto 8126

**Verificar:**
```bash
netstat -ulnp | grep 8126
```

**Si no aparece:**
1. Verifica que agregaste el bloque correctamente
2. Reinicia Telegraf: `docker restart telegraf`
3. Revisa logs: `docker logs telegraf`

### Las métricas no llegan

**Verificar conectividad:**
```bash
# Desde el servidor de la API
nc -u -v -z $STATSD_HOST 8126
```

**Verificar configuración de siscom-api:**
```bash
# SSH a tu EC2
cat ~/siscom-api/.env | grep STATSD
```

### Las métricas llegan pero sin tags

**Verificar en el bloque que agregaste:**
```toml
datadog_extensions = false  # ← Debe ser false
```

**Verificar formato de envío:**
```bash
# aio-statsd envía:
metric,tag1=value1:value|type

# NO debe enviar:
metric:value|type|#tag1:value1
```

## 📚 Documentación Relacionada

- [METRICS.md](METRICS.md) - Documentación completa de métricas
- [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md) - Guía rápida de configuración
- [GITHUB_VARIABLES.md](GITHUB_VARIABLES.md) - Variables de GitHub

---

**Última actualización:** Octubre 2024

