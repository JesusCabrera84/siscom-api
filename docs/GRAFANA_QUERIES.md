# 📊 Queries de Grafana para siscom-api

Guía para crear dashboards y queries en Grafana con las métricas de siscom-api.

## 🎯 Tipos de Métricas

### 1. **COUNTER**: `siscom_api.requests`

**¿Qué es?** Un contador acumulativo que se incrementa cada vez que llega una petición.

**¿Para qué sirve?** Ver el total de peticiones en períodos de tiempo definidos.

**Tipo en StatsD:** Counter (se resetea cada flush)

---

### 2. **TIMING**: `siscom_api.latency.stream`

**¿Qué es?** Tiempo de respuesta en milisegundos.

**¿Para qué sirve?** Medir performance y detectar latencias altas.

**Tipo en StatsD:** Timer (genera automáticamente percentiles y promedios)

---

### 3. **GAUGE**: `siscom_api.sse.active_connections`

**¿Qué es?** El número ACTUAL de conexiones SSE activas en este momento.

**¿Para qué sirve?** Monitorear la carga en tiempo real.

**Tipo en StatsD:** Gauge (reporta valor absoluto)

---

## 📈 Queries para Grafana

### 1. Requests por Minuto (Rate)

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r._field == "count")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> derivative(unit: 1m, nonNegative: true)
```

**Explicación:**

- `aggregateWindow(every: 1m)` - Agrupa por minuto

- `derivative(unit: 1m)` - Calcula la tasa de cambio por minuto
- `nonNegative: true` - Ignora valores negativos

**Panel recomendado:** Graph (línea)

---

### 2. Total de Requests en el Último Día

```flux
from(bucket: "siscom")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r._field == "count")
  |> sum()
```

**Panel recomendado:** Stat (número grande)

---

### 3. Latencia Media del Endpoint /stream

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
  |> filter(fn: (r) => r._field == "mean")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

**Panel recomendado:** Graph (línea con umbral)

**Umbrales sugeridos:**

- Verde: < 100ms
- Amarillo: 100-500ms
- Rojo: > 500ms

---

### 4. Latencia p95 (percentil 95)

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.latency.stream")
  |> filter(fn: (r) => r._field == "95_percentile")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

**Explicación:** El 95% de las peticiones están por debajo de este tiempo.

---

### 5. Conexiones SSE Activas (Tiempo Real)

```flux
from(bucket: "siscom")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "siscom_api.sse.active_connections")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 30s, fn: last, createEmpty: false)
```

**Panel recomendado:** Graph (área) o Stat (número actual)

---

### 6. Comparación de Requests: Hoy vs Ayer

```flux
today = from(bucket: "siscom")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r._field == "count")
  |> aggregateWindow(every: 1h, fn: sum)

yesterday = from(bucket: "siscom")
  |> range(start: -48h, stop: -24h)
  |> filter(fn: (r) => r._measurement == "siscom_api.requests")
  |> filter(fn: (r) => r._field == "count")
  |> aggregateWindow(every: 1h, fn: sum)
  |> timeShift(duration: 24h)

union(tables: [today, yesterday])
```

**Panel recomendado:** Graph (2 líneas)

---

## 🎨 Dashboard Recomendado

### Fila 1: Overview (Números Grandes)

1. **Total Requests (24h)** - Stat panel
2. **Requests por Minuto (actual)** - Stat panel con sparkline
3. **Conexiones SSE Activas** - Gauge panel
4. **Latencia Media** - Stat panel con umbrales

### Fila 2: Gráficos de Tiempo

1. **Requests por Minuto** - Graph (línea)
2. **Latencia (mean, p95, p99)** - Graph (multi-línea)

### Fila 3: Análisis Detallado

1. **Conexiones SSE en el Tiempo** - Graph (área)
2. **Distribución de Latencia** - Heatmap (si tienes histogramas)

---

## 🔧 Configuración de Telegraf

Asegúrate de que tu `telegraf.conf` tenga:

```toml
[[inputs.statsd]]
  service_address = ":8126"
  protocol = "udp"

  # Configuración para counters y timings
  metric_separator = "."
  datadog_extensions = false

  # Percentiles para latencias
  percentiles = [50, 90, 95, 99]

  # IMPORTANTE: No borrar gauges
  delete_gauges = false
  delete_counters = false
  delete_timings = true  # Se convierten a estadísticas

  [inputs.statsd.tags]
    source = "siscom-api"
```

---

## 📊 Tipos de Agregación por Métrica

| Métrica                             | Tipo StatsD | Campo InfluxDB                | Agregación Recomendada            |
| ----------------------------------- | ----------- | ----------------------------- | --------------------------------- |
| `siscom_api.requests`               | Counter     | `count`                       | `sum()`, `derivative()` para rate |
| `siscom_api.latency.stream`         | Timer       | `mean`, `95_percentile`, etc. | `mean()`, `max()`                 |
| `siscom_api.sse.active_connections` | Gauge       | `value`                       | `last()`, `mean()`, `max()`       |

---

## 🚨 Alertas Sugeridas

### 1. Latencia Alta

```plaintext
Alert: Latencia > 500ms durante 5 minutos
Query: mean(siscom_api.latency.stream.mean) > 500
```

### 2. Caída de Tráfico

```plaintext
Alert: Requests/min < 1 durante 10 minutos (puede indicar problema)
Query: derivative(siscom_api.requests) < 1
```

### 3. Conexiones SSE Altas

```plaintext
Alert: Conexiones activas > 100
Query: last(siscom_api.sse.active_connections) > 100
```

---

## 🎓 Conceptos Clave

### ¿Qué es un Counter?

Un contador que **siempre incrementa**. Se resetea cada vez que Telegraf hace flush (cada 10s por defecto).

**Ejemplo:**

```plaintext
t=0s:  count=0
t=10s: count=5   (5 requests en 10s)
t=20s: count=3   (3 requests en los siguientes 10s)
t=30s: count=7   (7 requests en los siguientes 10s)
```

Para ver "requests por minuto", usas `derivative()` o `rate()`.

### ¿Qué es un Gauge?

Un valor que puede subir o bajar, representa el **valor actual**.

**Ejemplo:**

```plaintext
t=0s:  active_connections=0
t=10s: active_connections=5   (5 clientes conectados)
t=20s: active_connections=3   (2 se desconectaron)
t=30s: active_connections=8   (5 nuevos clientes)
```

No necesitas `derivative()`, solo muestras el último valor o el promedio.

### ¿Qué es un Timer?

Mide duraciones y genera automáticamente:

- `mean` (promedio)
- `median` (p50)
- `95_percentile` (p95)
- `99_percentile` (p99)
- `upper` (máximo)
- `lower` (mínimo)
- `sum`, `count`

---

## 📝 Variables en Grafana

Puedes crear variables para filtrar por:

### Variable: time_range

```plaintext
1m, 5m, 15m, 1h, 6h, 24h, 7d
```

### Variable: percentile

```plaintext
50, 90, 95, 99
```

Luego en tu query:

```flux
|> filter(fn: (r) => r._field == "${percentile}_percentile")
```

---

## 🔗 Referencias

- Documentación de Flux: <https://docs.influxdata.com/flux/>
- Telegraf StatsD Input: <https://github.com/influxdata/telegraf/tree/master/plugins/inputs/statsd>
- Grafana Variables: <https://grafana.com/docs/grafana/latest/variables/>

---

## ✅ Checklist para Dashboard Completo

- [ ] Panel de requests/min (rate)
- [ ] Panel de requests totales (sum)
- [ ] Panel de latencia media
- [ ] Panel de latencia p95
- [ ] Panel de conexiones SSE activas
- [ ] Alertas configuradas para latencia alta
- [ ] Alertas configuradas para caída de tráfico
- [ ] Variables para cambiar time range
- [ ] Comparación con día anterior (opcional)
