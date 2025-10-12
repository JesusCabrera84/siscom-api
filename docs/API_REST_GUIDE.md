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

| Endpoint                                                | Método | Auth   | Descripción                          |
| ------------------------------------------------------- | ------ | ------ | ------------------------------------ |
| `GET /api/v1/communications`                            | GET    | ✅ JWT | Histórico de múltiples dispositivos  |
| `GET /api/v1/communications/stream`                     | GET    | ❌ No  | Stream SSE de múltiples dispositivos |
| `GET /api/v1/devices/{device_id}/communications`        | GET    | ✅ JWT | Histórico de un solo dispositivo     |
| `GET /api/v1/devices/{device_id}/communications/stream` | GET    | ❌ No  | Stream SSE de un solo dispositivo    |

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

### 3️⃣ GET /api/v1/communications/stream

Suscripción SSE para múltiples dispositivos en tiempo real

#### Request - Stream Múltiples

```http
GET /api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123
Accept: text/event-stream
```

#### Query Parameters

| Parámetro    | Tipo          | Requerido | Descripción                                    |
| ------------ | ------------- | --------- | ---------------------------------------------- |
| `device_ids` | array[string] | ✅ Sí     | Lista de IDs de dispositivos (mín: 1, máx: 50) |

#### Ejemplo con cURL

```bash
curl -N --location 'http://10.8.0.1:8000/api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123' \
--header 'Accept: text/event-stream'
```

#### Ejemplo con JavaScript (EventSource)

```javascript
const deviceIds = ["867564050638581", "DEVICE123"];
const params = new URLSearchParams();
deviceIds.forEach((id) => params.append("device_ids", id));

const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/communications/stream?${params}`,
);

eventSource.addEventListener("update", (event) => {
  const data = JSON.parse(event.data);
  console.log("Nueva actualización:", data);
  // {
  //   device_id: "867564050638581",
  //   latitude: 19.4326,
  //   longitude: -99.1332,
  //   speed: 45.5,
  //   timestamp: "2024-01-15T10:30:00"
  // }
});

eventSource.onerror = (error) => {
  console.error("Error en SSE:", error);
  eventSource.close();
};
```

#### Response (Stream SSE)

```plaintext
event: update
data: {"device_id": "867564050638581", "latitude": 19.4326, "longitude": -99.1332, "speed": 45.5, "timestamp": "2024-01-15T10:30:00"}

event: update
data: {"device_id": "DEVICE123", "latitude": 19.4327, "longitude": -99.1333, "speed": 50.0, "timestamp": "2024-01-15T10:30:02"}
```

---

### 4️⃣ GET /api/v1/devices/{device_id}/communications/stream

Suscripción SSE para UN solo dispositivo en tiempo real

#### Request - Stream Un Dispositivo

```http
GET /api/v1/devices/867564050638581/communications/stream
Accept: text/event-stream
```

#### Path Parameters

| Parámetro   | Tipo   | Requerido | Descripción            |
| ----------- | ------ | --------- | ---------------------- |
| `device_id` | string | ✅ Sí     | ID del dispositivo GPS |

#### Ejemplo con cURL

```bash
curl -N --location 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications/stream' \
--header 'Accept: text/event-stream'
```

#### Ejemplo con JavaScript (EventSource)

```javascript
const deviceId = "867564050638581";
const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications/stream`,
);

eventSource.addEventListener("update", (event) => {
  const data = JSON.parse(event.data);
  console.log(`Actualización de ${deviceId}:`, data);
});
```

#### Response (Stream SSE)

```plaintext
event: update
data: {"device_id": "867564050638581", "latitude": 19.4326, "longitude": -99.1332, "speed": 45.5, "timestamp": "2024-01-15T10:30:00"}

event: update
data: {"device_id": "867564050638581", "latitude": 19.4327, "longitude": -99.1333, "speed": 46.0, "timestamp": "2024-01-15T10:30:02"}
```

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
  │   ├── GET  → lista múltiples
  │   └── stream/  → stream múltiples
  │
  └── devices/
      └── {device_id}/             (recurso individual)
          └── communications/
              ├── GET  → lista uno
              └── stream/  → stream uno
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

## 🔐 Autenticación

### Endpoints con JWT

- `GET /api/v1/communications`
- `GET /api/v1/devices/{device_id}/communications`

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### Endpoints sin JWT (públicos)

- `GET /api/v1/communications/stream`
- `GET /api/v1/devices/{device_id}/communications/stream`

⚠️ **Nota:** Los endpoints de stream no requieren autenticación actualmente. Ajusta según tus necesidades de seguridad.

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

### Histórico de Dispositivos

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

### Stream en Tiempo Real

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
      `http://10.8.0.1:8000/api/v1/communications/stream?${params}`
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
