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

| Endpoint                                                | Método | Auth   | Descripción                                              |
| ------------------------------------------------------- | ------ | ------ | -------------------------------------------------------- |
| `GET /api/v1/communications`                            | GET    | ❌ No  | Histórico de múltiples dispositivos                      |
| `GET /api/v1/communications/latest`                     | GET    | ❌ No  | Última comunicación de múltiples devices                 |
| `GET /api/v1/devices/{device_id}/communications`        | GET    | ❌ No  | Histórico de un dispositivo (soporta `?received_at=`)    |
| `GET /api/v1/devices/{device_id}/communications/latest` | GET    | ❌ No  | Última comunicación de un solo dispositivo               |
| `WS /api/v1/stream`                                     | WS     | ❌ No  | WebSocket en tiempo real desde MQTT                      |
| `GET /api/v1/stream/stats`                              | GET    | ❌ No  | Estadísticas del broker WebSocket                        |
| `GET /health`                                           | GET    | ❌ No  | Health check del servicio                                |

> ⚠️ **Nota:** Actualmente ningún endpoint requiere autenticación. El código de JWT existe en `app/core/security.py` pero no está activo en las rutas.

---

## 📡 Endpoints Detallados

### 1️⃣ GET /api/v1/communications

Obtener histórico de múltiples dispositivos GPS

#### Request - Múltiples Dispositivos

```http
GET /api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123
```

#### Query Parameters

| Parámetro    | Tipo          | Requerido | Descripción                                     |
| ------------ | ------------- | --------- | ----------------------------------------------- |
| `device_ids` | array[string] | ✅ Sí     | Lista de IDs de dispositivos (mín: 1, máx: 100) |

#### Ejemplo con cURL

```bash
curl 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123'
```

#### Ejemplo con JavaScript

```javascript
const response = await fetch(
  "http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123"
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

Obtener histórico de comunicaciones de UN solo dispositivo GPS.

**Soporta filtro por fecha** con el parámetro `received_at`. Si se proporciona, devuelve **todos los campos disponibles**.

#### Request - Un Dispositivo

```http
GET /api/v1/devices/867564050638581/communications
GET /api/v1/devices/867564050638581/communications?received_at=2024-12-14
```

#### Path Parameters

| Parámetro   | Tipo   | Requerido | Descripción            |
| ----------- | ------ | --------- | ---------------------- |
| `device_id` | string | ✅ Sí     | ID del dispositivo GPS |

#### Query Parameters

| Parámetro     | Tipo   | Requerido | Descripción                                                                 |
| ------------- | ------ | --------- | --------------------------------------------------------------------------- |
| `received_at` | date   | ❌ No     | Fecha para filtrar (YYYY-MM-DD). Si se usa, devuelve **todos los campos**. |

#### Ejemplo con cURL

```bash
# Sin filtro (campos básicos)
curl 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications'

# Con filtro de fecha (TODOS los campos)
curl 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications?received_at=2024-12-14'
```

#### Ejemplo con JavaScript

```javascript
const deviceId = "867564050638581";

// Sin filtro
const response = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications`
);

// Con filtro de fecha
const responseFiltered = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications?received_at=2024-12-14`
);

const data = await response.json();
```

#### Response SIN filtro (200 OK) - Campos básicos

```json
[
  {
    "id": 1,
    "device_id": "867564050638581",
    "latitude": 19.4326,
    "longitude": -99.1332,
    "speed": 45.5,
    "course": 180.0,
    "gps_datetime": "2024-12-14T10:30:00",
    "main_battery_voltage": 12.5,
    "backup_battery_voltage": 3.7,
    "odometer": 15000,
    "trip_distance": 500,
    "total_distance": 150000,
    "engine_status": "ON",
    "fix_status": "VALID",
    "alert_type": null
  }
]
```

#### Response CON filtro `received_at` (200 OK) - Todos los campos

```json
[
  {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "device_id": "867564050638581",
    "backup_battery_voltage": 3.7,
    "main_battery_voltage": 12.5,
    "cell_id": "12345",
    "lac": "1234",
    "mcc": "334",
    "mnc": "020",
    "rx_lvl": -65,
    "network_status": "CONNECTED",
    "course": 180.0,
    "fix_status": "VALID",
    "gps_datetime": "2024-12-14T10:30:00",
    "gps_epoch": 1734176400,
    "latitude": 19.4326,
    "longitude": -99.1332,
    "satellites": 12,
    "speed": 45.5,
    "delivery_type": "GPRS",
    "engine_status": "ON",
    "firmware": "1.0.0",
    "model": "ST300",
    "msg_class": "STATUS",
    "msg_counter": 100,
    "odometer": 15000,
    "total_distance": 150000,
    "trip_distance": 500,
    "idle_time": 0,
    "speed_time": 3600,
    "trip_hourmeter": 100,
    "bytes_count": 256,
    "client_ip": "192.168.1.1",
    "client_port": 8080,
    "decoded_epoch": 1734176400,
    "received_epoch": 1734176401,
    "received_at": "2024-12-14T10:30:01",
    "created_at": "2024-12-14T10:30:01",
    "raw_message": null,
    "alert_type": null
  }
]
```

**💡 Nota:** Cuando se usa `received_at`, se devuelven todos los registros de esa fecha ordenados por hora descendente (más recientes primero).

---

### 3️⃣ GET /api/v1/communications/latest

Obtener la última comunicación de múltiples dispositivos GPS

#### Request - Última Comunicación de Múltiples Dispositivos

```http
GET /api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123
```

#### Query Parameters

| Parámetro    | Tipo          | Requerido | Descripción                                     |
| ------------ | ------------- | --------- | ----------------------------------------------- |
| `device_ids` | array[string] | ✅ Sí     | Lista de IDs de dispositivos (mín: 1, máx: 100) |

#### Ejemplo con cURL

```bash
curl 'http://10.8.0.1:8000/api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123'
```

#### Ejemplo con JavaScript

```javascript
const response = await fetch(
  "http://10.8.0.1:8000/api/v1/communications/latest?device_ids=867564050638581&device_ids=DEVICE123"
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
- `WS /api/v1/stream` → Conexión WebSocket con actualizaciones en tiempo real desde MQTT

**🎯 Caso de uso:** Ideal para dashboards que necesitan mostrar la posición/estado actual de múltiples dispositivos en un mapa sin cargar todo el histórico.

---

### 4️⃣ GET /api/v1/devices/{device_id}/communications/latest

Obtener la última comunicación de UN solo dispositivo GPS

#### Request - Última Comunicación de Un Dispositivo

```http
GET /api/v1/devices/867564050638581/communications/latest
```

#### Path Parameters

| Parámetro   | Tipo   | Requerido | Descripción            |
| ----------- | ------ | --------- | ---------------------- |
| `device_id` | string | ✅ Sí     | ID del dispositivo GPS |

#### Ejemplo con cURL

```bash
curl 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications/latest'
```

#### Ejemplo con JavaScript

```javascript
const deviceId = "867564050638581";
const response = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications/latest`
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
- `WS /api/v1/stream?device_ids={id}` → WebSocket en tiempo real desde MQTT

**🎯 Caso de uso:** Ideal para consultar rápidamente el estado actual de un dispositivo específico (última posición, batería, velocidad, etc.).

---

### 5️⃣ WS /api/v1/stream (WebSocket)

Stream WebSocket en tiempo real desde MQTT (Mosquitto)

**⚡ Este endpoint consume mensajes en tiempo real desde el broker MQTT y los transmite vía WebSocket.**

#### URL de Conexión

```
ws://localhost:8000/api/v1/stream?device_ids=867564050638581,DEVICE123
```

#### Query Parameters

| Parámetro    | Tipo   | Requerido | Descripción                                     |
| ------------ | ------ | --------- | ----------------------------------------------- |
| `device_ids` | string | ✅ Sí     | IDs de dispositivos separados por comas         |

**Nota:** El parámetro `device_ids` es **obligatorio**. Si no se especifica, la conexión se cerrará con código 1008.

#### Ejemplo con JavaScript (WebSocket)

```javascript
// Conectar al WebSocket
const deviceIds = "867564050638581,DEVICE123";
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/stream?device_ids=${deviceIds}`
);

ws.onopen = () => {
  console.log("✅ WebSocket conectado");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.event === "message") {
    // Datos del dispositivo
    console.log("📡 Evento MQTT recibido:", message.data);
    // Estructura:
    // {
    //   "event": "message",
    //   "data": {
    //     "data": {
    //       "DEVICE_ID": "0848086072",
    //       "LATITUD": "+20.652472",
    //       "LONGITUD": "-100.391423",
    //       "SPEED": "0.00",
    //       ...
    //     },
    //     "decoded": {...},
    //     "metadata": {...}
    //   }
    // }
  } else if (message.event === "ping") {
    console.log("💓 Keep-alive recibido");
  }
};

ws.onerror = (error) => {
  console.error("❌ Error en WebSocket:", error);
};

ws.onclose = (event) => {
  console.log("🔌 WebSocket cerrado:", event.code, event.reason);
};
```

#### Formato de Mensajes

**Mensaje de datos:**

```json
{
  "event": "message",
  "data": {
    "data": {
      "DEVICE_ID": "0848086072",
      "LATITUD": "+20.652472",
      "LONGITUD": "-100.391423",
      "SPEED": "0.00"
    },
    "decoded": {},
    "metadata": {}
  }
}
```

**Keep-alive (cada 60 segundos):**

```json
{
  "event": "ping",
  "data": {
    "type": "keep-alive"
  }
}
```

#### Características

- ✅ **Tiempo Real**: Consume mensajes directamente de Mosquitto MQTT
- ✅ **WebSocket**: Full-duplex, sin problemas de buffering en ALB/nginx
- ✅ **Filtrado Obligatorio**: Requiere especificar `device_ids`
- ✅ **Keep-alive**: Envía eventos `ping` cada 60 segundos
- ✅ **Sin Autenticación**: No requiere token
- ✅ **Backpressure**: Control automático de flujo si el cliente es lento

Ver documentación completa en [WEBSOCKET_STREAMING.md](./WEBSOCKET_STREAMING.md)

---

## 🔄 Migración desde Endpoints Antiguos

### Antes (Deprecated)

```bash
# POST con body JSON
curl -X POST http://10.8.0.1:8000/communications/history \
  -H "Content-Type: application/json" \
  -d '{"device_ids": ["867564050638581"]}'
```

### Ahora (REST Compliant)

```bash
# GET con query parameters
curl 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581'
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
  ├── devices/
  │   └── {device_id}/             (recurso individual)
  │       └── communications/
  │           ├── GET         → histórico completo del dispositivo
  │           └── latest/     → última comunicación del dispositivo
  │
  ├── stream/                      (WebSocket tiempo real)
  │   ├── WS          → WebSocket desde MQTT (requiere: ?device_ids=X,Y)
  │   └── stats/      → estadísticas del broker
  │
  └── public/share-location/       (enlaces públicos con PASETO)
      ├── init/       → validar token y obtener última ubicación
      └── stream/     → WebSocket público con token PASETO
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

### 🔴 Tiempo Real (`/api/v1/stream` - WebSocket)

**Cuándo usar:**

- Monitoreo en vivo/tiempo real desde Mosquitto
- Seguimiento activo de vehículos en operación
- Alertas instantáneas basadas en eventos MQTT
- Dashboards de control en vivo
- Recibir todos los campos del mensaje MQTT (data, decoded, metadata)

```javascript
// Ejemplo: Seguimiento en tiempo real desde MQTT vía WebSocket
const ws = new WebSocket(
  "ws://localhost:8000/api/v1/stream?device_ids=867564050638581,DEVICE123"
);
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === "message") {
    const data = message.data;
    // Actualiza la UI automáticamente con cada mensaje MQTT
    console.log(data.data.DEVICE_ID, data.data.LATITUD, data.data.LONGITUD);
  }
};
```

### 📊 Comparación Rápida

| Característica  | `/communications`      | `/communications/latest` | `/api/v1/stream` (WebSocket) |
| --------------- | ---------------------- | ------------------------ | ---------------------------- |
| Tipo            | Histórico completo     | Snapshot actual          | Tiempo real desde MQTT       |
| Origen          | `suntech` + `queclink` | `current_state`          | Mosquitto (MQTT broker)      |
| Datos           | Todos los registros    | Solo el más reciente     | Stream mensajes MQTT         |
| Incluye `id`    | ✅ Sí                  | ❌ No (PK: `device_id`)  | ✅ Mensaje completo          |
| Formato         | REST JSON              | REST JSON                | WebSocket (JSON)             |
| Frecuencia      | Bajo demanda           | Bajo demanda             | Tiempo real                  |
| Rendimiento     | Lento (muchos datos)   | ⚡ Rápido (pocos datos)  | ⚡ Eventos instantáneos      |
| Uso recomendado | Reportes, análisis     | Dashboards, mapas        | Monitoreo en tiempo real     |

---

## 🔐 Autenticación

### Estado Actual

> ⚠️ **Nota importante:** Actualmente **NINGÚN endpoint requiere autenticación**.
>
> El código de JWT existe en `app/core/security.py` con las funciones `create_access_token()`, `verify_token()` y `get_current_user()`, pero **no están activas** en ninguna ruta.

### Endpoints Públicos (sin autenticación)

- `GET /api/v1/communications`
- `GET /api/v1/communications/latest`
- `GET /api/v1/devices/{device_id}/communications`
- `GET /api/v1/devices/{device_id}/communications/latest`
- `WS /api/v1/stream`
- `GET /api/v1/stream/stats`

### Endpoints con Token PASETO

Los siguientes endpoints usan **tokens PASETO v4.local** (emitidos por `siscom-admin-api`) para autorización temporal:

- `GET /api/v1/public/share-location/init?token=v4.local.xxx...`
- `WS /api/v1/public/share-location/stream?token=v4.local.xxx...`

Estos tokens se usan para **compartir ubicaciones públicamente** con usuarios externos sin cuenta.

### Agregar Autenticación JWT (opcional)

Si necesitas proteger los endpoints con JWT, agrega `Depends(get_current_user)` a las rutas:

```python
from app.core.security import get_current_user

@router.get("/communications")
async def get_communications(
    device_ids: list[str] = Query(...),
    db=Depends(get_db),
    user=Depends(get_current_user),  # ← Agregar esto
):
    ...
```

Luego el cliente debe enviar:

```bash
Authorization: Bearer <jwt_token>
```

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

### Error 401: Token inválido (solo si JWT está activo)

```json
{
  "detail": "Invalid token"
}
```

**Solución:** Verifica que el token JWT sea válido y no haya expirado.

> 📝 **Nota:** Este error solo ocurre si implementas autenticación JWT en las rutas.

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
        `http://10.8.0.1:8000/api/v1/communications/latest?${params}`
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
        `http://10.8.0.1:8000/api/v1/communications?${params}`
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

### 3. Stream en Tiempo Real (WebSocket)

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';

  let liveData = {};
  let ws;
  let connected = false;

  onMount(() => {
    const deviceIds = ['867564050638581', 'DEVICE123'];

    ws = new WebSocket(
      `ws://10.8.0.1:8000/api/v1/stream?device_ids=${deviceIds.join(',')}`
    );

    ws.onopen = () => {
      console.log('✅ WebSocket conectado');
      connected = true;
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.event === 'message') {
        const data = message.data.data;
        const deviceId = data.DEVICE_ID;
        liveData[deviceId] = {
          latitude: data.LATITUD,
          longitude: data.LONGITUD,
          speed: data.SPEED,
          timestamp: data.GPS_DATETIME
        };
        liveData = { ...liveData }; // reactivity
      }
    };

    ws.onerror = () => {
      console.error('❌ Error en WebSocket');
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket cerrado');
      connected = false;
    };
  });

  onDestroy(() => {
    ws?.close();
  });
</script>

<div>
  <p>Estado: {connected ? '🟢 Conectado' : '🔴 Desconectado'}</p>
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
