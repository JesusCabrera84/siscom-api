# 📘 Guía de Endpoints REST - SISCOM API v1

## 🎯 Resumen de Cambios

Los endpoints han sido migrados a seguir las **mejores prácticas REST**:

- ✅ Uso de **GET** en lugar de POST para consultas
- ✅ **Query parameters** en lugar de request body
- ✅ **Versionamiento** con `/api/v1/`
- ✅ Estructura **jerárquica** clara
- ✅ **Path parameters** para recursos específicos

---

## 📋 Tabla de Endpoints

| Endpoint                                                | Método | Auth   | Descripción                                |
| ------------------------------------------------------- | ------ | ------ | ------------------------------------------ |
| `GET /api/v1/communications`                            | GET    | ✅ JWT | Histórico de múltiples dispositivos        |
| `GET /api/v1/communications/latest`                     | GET    | ✅ JWT | Última comunicación de múltiples devices   |
| `GET /api/v1/devices/{device_id}/communications`        | GET    | ✅ JWT | Histórico de un solo dispositivo           |
| `GET /api/v1/devices/{device_id}/communications/latest` | GET    | ✅ JWT | Última comunicación de un solo dispositivo |
| `GET /api/v1/stream`                                    | GET    | ❌ No  | Stream SSE en tiempo real desde MQTT       |
| `GET /health`                                           | GET    | ❌ No  | Health check del servicio                  |

---

## 📡 Endpoints Detallados

### 1️⃣ GET /api/v1/communications

Obtener histórico de múltiples dispositivos GPS

#### Request - Múltiples Dispositivos

```http
GET /api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

#### Query Parameters

| Parámetro    | Tipo          | Requerido | Descripción                                     |
| ------------ | ------------- | --------- | ----------------------------------------------- |
| `device_ids` | array[string] | ✅ Sí     | Lista de IDs de dispositivos (mín: 1, máx: 100) |

#### Ejemplo con cURL

```bash
curl --location 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

#### Ejemplo con JavaScript

```javascript
const response = await fetch(
  "http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123",
  {
    headers: {
      Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
    },
  },
);

const data = await response.json();
```

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "device_id": "867564050638581",
    "latitude": 19.4326,
    "longitude": -99.1332,
    "speed": 45.5,
    "course": 180.0,
    "gps_datetime": "2024-01-15T10:30:00",
    "main_battery_voltage": 12.5,
    "backup_battery_voltage": 3.7,
    "odometer": 15000,
    "trip_distance": 500,
    "total_distance": 150000,
    "engine_status": "ON",
    "fix_status": "VALID",
    "alert_type": null
  },
  ...
]
```

---

### 2️⃣ GET /api/v1/devices/{device_id}/communications

Obtener histórico de UN solo dispositivo GPS

#### Request - Un Dispositivo

```http
GET /api/v1/devices/867564050638581/communications
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

#### Path Parameters

| Parámetro   | Tipo   | Requerido | Descripción            |
| ----------- | ------ | --------- | ---------------------- |
| `device_id` | string | ✅ Sí     | ID del dispositivo GPS |

#### Ejemplo con cURL

```bash
curl --location 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

#### Ejemplo con JavaScript

```javascript
const deviceId = "867564050638581";
const response = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications`,
  {
    headers: {
      Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
    },
  },
);

const data = await response.json();
```

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "device_id": "867564050638581",
    "latitude": 19.4326,
    ...
  }
]
```

---

### 3️⃣ GET /api/v1/communications/latest

Obtener la última comunicación de múltiples dispositivos GPS

#### Request - Última Comunicación de Múltiples Dispositivos

```http
GET /api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

#### Query Parameters

| Parámetro    | Tipo          | Requerido | Descripción                                     |
| ------------ | ------------- | --------- | ----------------------------------------------- |
| `device_ids` | array[string] | ✅ Sí     | Lista de IDs de dispositivos (mín: 1, máx: 100) |

#### Ejemplo con cURL

```bash
curl --location 'http://10.8.0.1:8000/api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

#### Ejemplo con JavaScript

```javascript
const response = await fetch(
  "http://10.8.0.1:8000/api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123",
  {
    headers: {
      Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
    },
  },
);

const data = await response.json();
```

#### Response (200 OK)

```json
[
  {
    "device_id": "867564050638581",
    "latitude": 19.4326,
    "longitude": -99.1332,
    "speed": 45.5,
    "course": 180.0,
    "gps_datetime": "2024-01-15T10:30:00",
    "gps_epoch": 1705318200,
    "main_battery_voltage": 12.5,
    "backup_battery_voltage": 3.7,
    "odometer": 15000,
    "engine_status": "ON",
    "fix_status": "VALID",
    "satellites": 12,
    "rx_lvl": -65,
    "network_status": "CONNECTED",
    "msg_class": "HEARTBEAT",
    "delivery_type": "GPRS",
    "received_epoch": 1705318201,
    "received_at": "2024-01-15T10:30:01",
    "alert_type": null
  },
  {
    "device_id": "DEVICE123",
    "latitude": 19.4327,
    "longitude": -99.1333,
    "speed": 50.0,
    "satellites": 10,
    ...
  }
]
```

**📝 Nota:** El endpoint `/latest` usa la tabla `communications_current_state`, por lo que:

- ❌ No incluye el campo `id` (device_id es la clave primaria)
- ✅ Incluye campos adicionales como `satellites`, `rx_lvl`, `gps_epoch`, etc.

**💡 Diferencias clave:**

- `GET /communications` → Retorna TODO el histórico (puede ser miles de registros)
- `GET /communications/latest` → Retorna SOLO la última comunicación de cada dispositivo
- `GET /api/v1/stream` → Conexión persistente con actualizaciones en tiempo real desde MQTT

**🎯 Caso de uso:** Ideal para dashboards que necesitan mostrar la posición/estado actual de múltiples dispositivos en un mapa sin cargar todo el histórico.

---

### 4️⃣ GET /api/v1/devices/{device_id}/communications/latest

Obtener la última comunicación de UN solo dispositivo GPS

#### Request - Última Comunicación de Un Dispositivo

```http
GET /api/v1/devices/867564050638581/communications/latest
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

#### Path Parameters

| Parámetro   | Tipo   | Requerido | Descripción            |
| ----------- | ------ | --------- | ---------------------- |
| `device_id` | string | ✅ Sí     | ID del dispositivo GPS |

#### Ejemplo con cURL

```bash
curl --location 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications/latest' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

#### Ejemplo con JavaScript

```javascript
const deviceId = "867564050638581";
const response = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications/latest`,
  {
    headers: {
      Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
    },
  },
);

const data = await response.json();
```

#### Response (200 OK)

```json
{
  "device_id": "867564050638581",
  "latitude": 19.4326,
  "longitude": -99.1332,
  "speed": 45.5,
  "course": 180.0,
  "gps_datetime": "2024-01-15T10:30:00",
  "gps_epoch": 1705318200,
  "main_battery_voltage": 12.5,
  "backup_battery_voltage": 3.7,
  "odometer": 15000,
  "engine_status": "ON",
  "fix_status": "VALID",
  "satellites": 12,
  "rx_lvl": -65,
  "network_status": "CONNECTED",
  "msg_class": "HEARTBEAT",
  "delivery_type": "GPRS",
  "received_epoch": 1705318201,
  "received_at": "2024-01-15T10:30:01",
  "alert_type": null
}
```

**📝 Nota:** Sin campo `id`, incluye `satellites` y otros campos adicionales.

#### Response (404 Not Found)

```json
{
  "detail": "No se encontró comunicación para el dispositivo 867564050638581"
}
```

**💡 Diferencias clave:**

- `GET /devices/{id}/communications` → Retorna TODO el histórico del dispositivo
- `GET /devices/{id}/communications/latest` → Retorna SOLO la última comunicación
- `GET /api/v1/stream?device_ids={id}` → Stream en tiempo real desde MQTT

**🎯 Caso de uso:** Ideal para consultar rápidamente el estado actual de un dispositivo específico (última posición, batería, velocidad, etc.).

---

### 5️⃣ GET /api/v1/stream

Stream SSE en tiempo real desde MQTT (Mosquitto)

**⚡ Este endpoint consume mensajes en tiempo real desde el broker MQTT y los transmite vía Server-Sent Events.**

#### Request

```http
GET /api/v1/stream?device_ids=867564050638581,DEVICE123
Accept: text/event-stream
```

#### Query Parameters

| Parámetro    | Tipo   | Requerido | Descripción                                               |
| ------------ | ------ | --------- | --------------------------------------------------------- |
| `device_ids` | string | ❌ No     | IDs de dispositivos separados por comas (filtro opcional) |

**Nota:** Si no se especifica `device_ids`, se recibirán eventos de **todos** los dispositivos.

#### Ejemplo con cURL

```bash
# Todos los dispositivos
curl -N 'http://10.8.0.1:8000/api/v1/stream'

# Filtrar por device_ids específicos
curl -N 'http://10.8.0.1:8000/api/v1/stream?device_ids=867564050638581,DEVICE123'
```

#### Ejemplo con JavaScript (EventSource)

```javascript
// Todos los dispositivos
const eventSource = new EventSource("http://10.8.0.1:8000/api/v1/stream");

// O filtrar por device_ids
const deviceIds = "867564050638581,DEVICE123";
const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/stream?device_ids=${deviceIds}`,
);

eventSource.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  console.log("Evento MQTT recibido:", data);
  // Estructura completa del mensaje de Mosquitto:
  // {
  //   "data": {
  //     "DEVICE_ID": "0848086072",
  //     "LATITUD": "+20.652472",
  //     "LONGITUD": "-100.391423",
  //     "SPEED": "0.00",
  //     "GPS_DATETIME": "2025-10-18 00:51:16",
  //     ...
  //   },
  //   "decoded": {...},
  //   "metadata": {...},
  //   "raw": "...",
  //   "uuid": "..."
  // }
});

eventSource.addEventListener("ping", (event) => {
  console.log("Keep-alive recibido");
});

eventSource.onerror = (error) => {
  console.error("Error en SSE:", error);
  eventSource.close();
};
```

#### Response (Stream SSE)

```plaintext
event: message
data: {"data":{"DEVICE_ID":"0848086072","LATITUD":"+20.652472","LONGITUD":"-100.391423","SPEED":"0.00",...},"decoded":{...},"metadata":{...}}

event: ping
data: {"type":"keep-alive"}

event: message
data: {"data":{"DEVICE_ID":"0848086073","LATITUD":"+20.653000","LONGITUD":"-100.392000","SPEED":"15.50",...},"decoded":{...},"metadata":{...}}
```

#### Características

- ✅ **Tiempo Real**: Consume mensajes directamente de Mosquitto MQTT
- ✅ **Filtrado**: Soporta filtro opcional por `device_ids`
- ✅ **Keep-alive**: Envía eventos `ping` cada 30 segundos para mantener la conexión
- ✅ **Sin Autenticación**: No requiere JWT (ajustable según necesidad)
- ✅ **Formato Completo**: Incluye toda la información del mensaje MQTT (data, decoded, metadata, raw)

Ver documentación completa en [MQTT_INTEGRATION.md](../MQTT_INTEGRATION.md)

---

## 🔄 Migración desde Endpoints Antiguos

### Antes (Deprecated)

```bash
# POST con body JSON
curl -X POST http://10.8.0.1:8000/communications/history \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_ids": ["867564050638581"]}'
```

### Ahora (REST Compliant)

```bash
# GET con query parameters
curl http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581 \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Comparación de Enfoques

| Aspecto            | Antes (POST) | Ahora (GET)     |
| ------------------ | ------------ | --------------- |
| **Método HTTP**    | POST         | GET ✅          |
| **Parámetros**     | Request Body | Query Params ✅ |
| **Versionamiento** | ❌ No        | `/api/v1/` ✅   |
| **REST Compliant** | ❌ No        | ✅ Sí           |
| **Cacheable**      | ❌ No        | ✅ Sí (HTTP)    |
| **Bookmarkable**   | ❌ No        | ✅ Sí           |
| **SEO Friendly**   | ❌ No        | ✅ Sí           |

---

## 🎯 Mejores Prácticas Implementadas

### ✅ 1. Uso Correcto de Métodos HTTP

- **GET** para lectura (no modifica datos)
- **POST** para creación
- **PUT/PATCH** para actualización
- **DELETE** para eliminación

### ✅ 2. Versionamiento de API

- URLs con `/api/v1/` permiten evolucionar la API sin romper clientes
- Futuras versiones: `/api/v2/`, `/api/v3/`, etc.

### ✅ 3. Estructura Jerárquica

```plaintext
/api/v1/
  ├── communications/              (colección)
  │   ├── GET         → histórico completo de múltiples
  │   └── latest/     → última comunicación de múltiples
  │
  └── devices/
      └── {device_id}/             (recurso individual)
          └── communications/
              ├── GET         → histórico completo del dispositivo
              └── latest/     → última comunicación del dispositivo

/api/v1/
  └── stream/                        (MQTT tiempo real)
      └── GET         → stream SSE desde Mosquitto (opcional: ?device_ids=X,Y)
```

### ✅ 4. Query Parameters para Filtros

GET permite usar query parameters:

```plaintext
?device_ids=X&device_ids=Y&start_date=...&end_date=...&limit=100
```

### ✅ 5. Path Parameters para Recursos Específicos

```plaintext
/devices/{device_id}/communications
```

Claridad semántica: "las comunicaciones del dispositivo X"

---

## 🎯 Casos de Uso - ¿Cuál endpoint usar?

### 📊 Histórico (`/communications`)

**Cuándo usar:**

- Necesitas analizar datos históricos completos
- Generar reportes de trayectorias
- Análisis de comportamiento del dispositivo
- Exportar datos para auditoría

```javascript
// Ejemplo: Obtener todo el historial de un vehículo
const history = await fetch("/api/v1/devices/867564050638581/communications");
```

### 📍 Estado Actual (`/communications/latest`)

**Cuándo usar:**

- Mostrar posiciones actuales en un mapa/dashboard
- Ver el estado actual de múltiples dispositivos
- Consultas rápidas sin cargar todo el histórico
- Widgets de estado/resumen

```javascript
// Ejemplo: Mostrar posición actual de todos los vehículos en un mapa
const currentPositions = await fetch(
  "/api/v1/communications/latest?device_ids=X&device_ids=Y",
);
// Retorna SOLO la última posición de cada uno
```

### 🔴 Tiempo Real (`/api/v1/stream` - MQTT)

**Cuándo usar:**

- Monitoreo en vivo/tiempo real desde Mosquitto
- Seguimiento activo de vehículos en operación
- Alertas instantáneas basadas en eventos MQTT
- Dashboards de control en vivo
- Recibir todos los campos del mensaje MQTT (data, decoded, metadata, raw)

```javascript
// Ejemplo: Seguimiento en tiempo real desde MQTT
const eventSource = new EventSource(
  "/api/v1/stream?device_ids=867564050638581,DEVICE123",
);
eventSource.addEventListener("message", (e) => {
  const data = JSON.parse(e.data);
  // Actualiza la UI automáticamente con cada mensaje MQTT
  console.log(data.data.DEVICE_ID, data.data.LATITUD, data.data.LONGITUD);
});
```

### 📊 Comparación Rápida

| Característica  | `/communications`      | `/communications/latest` | `/api/v1/stream` (MQTT)  |
| --------------- | ---------------------- | ------------------------ | ------------------------ |
| Tipo            | Histórico completo     | Snapshot actual          | Tiempo real desde MQTT   |
| Origen          | `suntech` + `queclink` | `current_state`          | Mosquitto (MQTT broker)  |
| Datos           | Todos los registros    | Solo el más reciente     | Stream mensajes MQTT     |
| Incluye `id`    | ✅ Sí                  | ❌ No (PK: `device_id`)  | ✅ Mensaje completo      |
| Formato         | REST JSON              | REST JSON                | SSE (Server-Sent Events) |
| Frecuencia      | Bajo demanda           | Bajo demanda             | Tiempo real              |
| Rendimiento     | Lento (muchos datos)   | ⚡ Rápido (pocos datos)  | ⚡ Eventos instantáneos  |
| Uso recomendado | Reportes, análisis     | Dashboards, mapas        | Monitoreo en tiempo real |

---

## 🔐 Autenticación

### Endpoints con JWT

- `GET /api/v1/communications`
- `GET /api/v1/communications/latest`
- `GET /api/v1/devices/{device_id}/communications`
- `GET /api/v1/devices/{device_id}/communications/latest`

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### Endpoints sin JWT (públicos)

- `GET /api/v1/stream`

⚠️ **Nota:** El endpoint de stream MQTT no requiere autenticación actualmente. Ajusta según tus necesidades de seguridad.

---

## ❌ Errores Comunes

### Error 422: Query parameter requerido

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "device_ids"],
      "msg": "Field required"
    }
  ]
}
```

**Solución:** Incluye al menos un `device_ids` en la URL:

```plaintext
?device_ids=867564050638581
```

### Error 401: Token inválido

```json
{
  "detail": "Invalid token"
}
```

**Solución:** Verifica que el token JWT sea válido y no haya expirado.

---

## 📚 Documentación Interactiva

Abre tu navegador en:

```plaintext
http://10.8.0.1:8000/api/docs
```

Verás:

- Todos los endpoints con ejemplos
- Botón "Try it out" para probar
- Schemas de request/response
- Códigos de error

---

## 🚀 Ejemplos de Integración Frontend (Svelte)

### 1. Obtener Última Posición (Latest)

```svelte
<script>
  import { onMount } from 'svelte';

  let currentPositions = [];
  let loading = false;

  async function fetchLatestPositions(deviceIds) {
    loading = true;

    try {
      const params = new URLSearchParams();
      deviceIds.forEach(id => params.append('device_ids', id));

      const response = await fetch(
        `http://10.8.0.1:8000/api/v1/communications/latest?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${$authToken}`
          }
        }
      );

      if (!response.ok) throw new Error('Error al cargar posiciones');

      currentPositions = await response.json();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    // Obtener posición actual de todos los vehículos
    fetchLatestPositions(['867564050638581', 'DEVICE123']);

    // Actualizar cada 30 segundos
    const interval = setInterval(() => {
      fetchLatestPositions(['867564050638581', 'DEVICE123']);
    }, 30000);

    return () => clearInterval(interval);
  });
</script>

{#if loading}
  <p>Cargando posiciones...</p>
{:else}
  <div class="map-view">
    {#each currentPositions as pos}
      <div class="marker" data-device="{pos.device_id}">
        📍 {pos.device_id}
        <br>
        Lat: {pos.latitude}, Lon: {pos.longitude}
        <br>
        Velocidad: {pos.speed} km/h
        <br>
        <small>{pos.gps_datetime}</small>
      </div>
    {/each}
  </div>
{/if}
```

### 2. Histórico de Dispositivos

```svelte
<script>
  import { onMount } from 'svelte';

  let communications = [];
  let loading = false;
  let error = null;

  async function fetchCommunications(deviceIds) {
    loading = true;
    error = null;

    try {
      const params = new URLSearchParams();
      deviceIds.forEach(id => params.append('device_ids', id));

      const response = await fetch(
        `http://10.8.0.1:8000/api/v1/communications?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${$authToken}` // tu store de Svelte
          }
        }
      );

      if (!response.ok) throw new Error('Error al cargar datos');

      communications = await response.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchCommunications(['867564050638581', 'DEVICE123']);
  });
</script>

{#if loading}
  <p>Cargando...</p>
{:else if error}
  <p>Error: {error}</p>
{:else}
  <ul>
    {#each communications as comm}
      <li>
        {comm.device_id}: {comm.latitude}, {comm.longitude}
      </li>
    {/each}
  </ul>
{/if}
```

### 3. Stream en Tiempo Real

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';

  let liveData = {};
  let eventSource;

  onMount(() => {
    const deviceIds = ['867564050638581', 'DEVICE123'];
    const params = new URLSearchParams();
    deviceIds.forEach(id => params.append('device_ids', id));

    eventSource = new EventSource(
      `http://10.8.0.1:8000/api/v1/stream?device_ids=${deviceIds.join(',')}`
    );

    eventSource.addEventListener('update', (event) => {
      const data = JSON.parse(event.data);
      liveData[data.device_id] = data;
      liveData = { ...liveData }; // reactivity
    });

    eventSource.onerror = () => {
      console.error('Error en SSE');
    };
  });

  onDestroy(() => {
    eventSource?.close();
  });
</script>

<div>
  {#each Object.entries(liveData) as [deviceId, data]}
    <div class="device-card">
      <h3>{deviceId}</h3>
      <p>Lat: {data.latitude}, Lon: {data.longitude}</p>
      <p>Velocidad: {data.speed} km/h</p>
      <small>{data.timestamp}</small>
    </div>
  {/each}
</div>
```

---

## ✅ Checklist de Migración

- [x] Endpoints con versionamiento `/api/v1/`
- [x] GET para consultas (no POST)
- [x] Query parameters para filtros
- [x] Path parameters para recursos específicos
- [x] Response models tipados
- [x] Documentación automática
- [x] Validación automática
- [ ] Tests actualizados (pendiente)
- [ ] Frontend actualizado (pendiente)

---

**¡Listo!** 🎉 Tus endpoints ahora siguen las mejores prácticas REST.
