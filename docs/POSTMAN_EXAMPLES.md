# 📮 Ejemplos de Uso - SISCOM API v1 (REST)

## 🎯 Endpoints REST Actualizados

Los endpoints han sido migrados a seguir las **mejores prácticas REST**.

⚠️ **IMPORTANTE:** Los endpoints ahora usan:

- ✅ **GET** en lugar de POST
- ✅ **Query parameters** en lugar de body JSON
- ✅ **Versionamiento** `/api/v1/`

---

## 📋 Tabla de Endpoints

| Endpoint                                                | Método | Auth   | Descripción                          |
| ------------------------------------------------------- | ------ | ------ | ------------------------------------ |
| `GET /api/v1/communications`                            | GET    | ✅ JWT | Histórico de múltiples dispositivos  |
| `GET /api/v1/communications/stream`                     | GET    | ❌ No  | Stream SSE de múltiples dispositivos |
| `GET /api/v1/devices/{device_id}/communications`        | GET    | ✅ JWT | Histórico de un solo dispositivo     |
| `GET /api/v1/devices/{device_id}/communications/stream` | GET    | ❌ No  | Stream SSE de un solo dispositivo    |

---

## 🧪 Ejemplos con cURL

### 1️⃣ Histórico de Múltiples Dispositivos

```bash
curl --location 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

**Un solo dispositivo:**

```bash
curl 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ"
```

---

### 2️⃣ Histórico de UN Solo Dispositivo (Path Parameter)

```bash
curl --location 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ'
```

---

### 3️⃣ Stream SSE - Múltiples Dispositivos

```bash
curl -N 'http://10.8.0.1:8000/api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123' \
--header 'Accept: text/event-stream'
```

**Nota:** El flag `-N` desactiva el buffering para ver los eventos en tiempo real.

---

### 4️⃣ Stream SSE - Un Solo Dispositivo

```bash
curl -N 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications/stream' \
--header 'Accept: text/event-stream'
```

---

## 📮 En Postman

### Importar Colección

1. Importa el archivo: `SISCOM-API-v1.postman_collection.json`
2. Configura las variables:
   - `base_url` = `http://10.8.0.1:8000`
   - `token` = `eyJhbGciOiJIUzI1NiJ9...`

### 1️⃣ Histórico de Múltiples Dispositivos

**Request:**

```plaintext
GET {{base_url}}/api/v1/communications
```

**Params (Query):**

| Key          | Value             |
| ------------ | ----------------- |
| `device_ids` | `867564050638581` |
| `device_ids` | `DEVICE123`       |

**Headers:**

```plaintext
Authorization: Bearer {{token}}
```

**Captura en Postman:**

```plaintext
┌──────────────────────────────────────────────────┐
│ GET ▼ │ {{base_url}}/api/v1/communications     │
├──────────────────────────────────────────────────┤
│ Params  Authorization  Headers  Body             │
│                                                   │
│ Query Params:                                    │
│  device_ids   867564050638581                    │
│  device_ids   DEVICE123                          │
│                                                   │
│ Headers:                                         │
│  Authorization   Bearer {{token}}                │
└──────────────────────────────────────────────────┘
```

---

### 2️⃣ Histórico de Un Solo Dispositivo

**Request:**

```plaintext
GET {{base_url}}/api/v1/devices/867564050638581/communications
```

**Headers:**

```plaintext
Authorization: Bearer {{token}}
```

---

### 3️⃣ Stream SSE - Múltiples Dispositivos

**Request:**

```plaintext
GET {{base_url}}/api/v1/communications/stream
```

**Params (Query):**

| Key          | Value             |
| ------------ | ----------------- |
| `device_ids` | `867564050638581` |
| `device_ids` | `DEVICE123`       |

**Headers:**

```plaintext
Accept: text/event-stream
```

⚠️ **Nota:** Postman tiene soporte limitado para SSE. Mejor usa cURL o EventSource en JavaScript.

---

## 🌐 En JavaScript/TypeScript (Frontend)

### 1️⃣ Histórico de Múltiples Dispositivos

```javascript
// Usando Fetch API
const deviceIds = ["867564050638581", "DEVICE123", "GPS001"];
const params = new URLSearchParams();
deviceIds.forEach((id) => params.append("device_ids", id));

const response = await fetch(
  `http://10.8.0.1:8000/api/v1/communications?${params}`,
  {
    headers: {
      Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
    },
  },
);

const data = await response.json();
console.log(data);
```

```javascript
// Usando Axios
import axios from "axios";

const response = await axios.get("http://10.8.0.1:8000/api/v1/communications", {
  params: {
    device_ids: ["867564050638581", "DEVICE123", "GPS001"],
  },
  headers: {
    Authorization: "Bearer eyJhbGciOiJIUzI1NiJ9...",
  },
});

console.log(response.data);
```

---

### 2️⃣ Histórico de Un Solo Dispositivo

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
console.log(data);
```

---

### 3️⃣ Stream SSE - Múltiples Dispositivos

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

// Cerrar conexión cuando sea necesario
// eventSource.close();
```

---

### 4️⃣ Stream SSE - Un Solo Dispositivo

```javascript
const deviceId = "867564050638581";

const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications/stream`,
);

eventSource.addEventListener("update", (event) => {
  const data = JSON.parse(event.data);
  console.log(`Actualización de ${deviceId}:`, data);
});

eventSource.onerror = () => {
  console.error("Error en stream");
  eventSource.close();
};
```

---

## 💻 En Python

### Con Requests

```python
import requests

# 1. Histórico de múltiples dispositivos
url = "http://10.8.0.1:8000/api/v1/communications"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9..."
}

params = {
    "device_ids": ["867564050638581", "DEVICE123"]
}

response = requests.get(url, params=params, headers=headers)
print(response.json())
```

```python
# 2. Histórico de un solo dispositivo
device_id = "867564050638581"
url = f"http://10.8.0.1:8000/api/v1/devices/{device_id}/communications"

response = requests.get(url, headers=headers)
print(response.json())
```

---

## 🎨 En Svelte (Frontend Completo)

### Componente para Histórico

```svelte
<script>
  import { onMount } from 'svelte';

  let communications = [];
  let loading = false;
  let error = null;
  let token = ''; // Obtener de tu store de autenticación

  async function fetchCommunications(deviceIds) {
    loading = true;
    error = null;

    try {
      // Construir query parameters
      const params = new URLSearchParams();
      deviceIds.forEach(id => params.append('device_ids', id));

      const response = await fetch(
        `http://10.8.0.1:8000/api/v1/communications?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      communications = await response.json();
    } catch (e) {
      error = e.message;
      console.error('Error al cargar comunicaciones:', e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchCommunications(['867564050638581', 'DEVICE123']);
  });
</script>

<div class="communications-container">
  <h2>Histórico de Comunicaciones</h2>

  {#if loading}
    <p class="loading">Cargando...</p>
  {:else if error}
    <p class="error">Error: {error}</p>
  {:else if communications.length === 0}
    <p class="empty">No hay comunicaciones disponibles</p>
  {:else}
    <div class="communications-list">
      {#each communications as comm}
        <div class="communication-card">
          <h3>Dispositivo: {comm.device_id}</h3>
          <p>📍 Lat: {comm.latitude}, Lon: {comm.longitude}</p>
          <p>🚗 Velocidad: {comm.speed} km/h</p>
          <p>🔋 Batería: {comm.main_battery_voltage}V</p>
          <p>🕐 {new Date(comm.gps_datetime).toLocaleString()}</p>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .communications-container {
    padding: 20px;
  }

  .communications-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .communication-card {
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    background: white;
  }

  .loading {
    color: #666;
  }

  .error {
    color: #d32f2f;
  }
</style>
```

---

### Componente para Stream en Tiempo Real

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';

  let liveData = {};
  let eventSource;
  let connected = false;
  let error = null;

  function connectStream(deviceIds) {
    // Construir query parameters
    const params = new URLSearchParams();
    deviceIds.forEach(id => params.append('device_ids', id));

    eventSource = new EventSource(
      `http://10.8.0.1:8000/api/v1/communications/stream?${params}`
    );

    eventSource.addEventListener('open', () => {
      connected = true;
      error = null;
      console.log('Conectado al stream SSE');
    });

    eventSource.addEventListener('update', (event) => {
      const data = JSON.parse(event.data);
      liveData[data.device_id] = data;
      liveData = { ...liveData }; // Trigger reactivity
    });

    eventSource.addEventListener('error', (e) => {
      connected = false;
      error = 'Error de conexión';
      console.error('Error en SSE:', e);
    });
  }

  onMount(() => {
    connectStream(['867564050638581', 'DEVICE123']);
  });

  onDestroy(() => {
    eventSource?.close();
  });
</script>

<div class="stream-container">
  <h2>Monitoreo en Tiempo Real</h2>

  <div class="status">
    {#if connected}
      <span class="badge success">🟢 Conectado</span>
    {:else if error}
      <span class="badge error">🔴 {error}</span>
    {:else}
      <span class="badge pending">🟡 Conectando...</span>
    {/if}
  </div>

  <div class="devices-grid">
    {#each Object.entries(liveData) as [deviceId, data]}
      <div class="device-card live">
        <h3>{deviceId}</h3>
        <div class="data">
          <p>📍 {data.latitude}, {data.longitude}</p>
          <p>🚗 {data.speed} km/h</p>
          <p>🕐 {data.timestamp}</p>
        </div>
        <span class="pulse"></span>
      </div>
    {:else}
      <p>Esperando actualizaciones...</p>
    {/each}
  </div>
</div>

<style>
  .stream-container {
    padding: 20px;
  }

  .status {
    margin-bottom: 20px;
  }

  .badge {
    padding: 5px 10px;
    border-radius: 4px;
    font-weight: bold;
  }

  .badge.success {
    background: #4caf50;
    color: white;
  }

  .badge.error {
    background: #f44336;
    color: white;
  }

  .devices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .device-card {
    border: 2px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    position: relative;
  }

  .device-card.live {
    border-color: #4caf50;
    animation: pulse-border 2s infinite;
  }

  @keyframes pulse-border {
    0%, 100% { border-color: #4caf50; }
    50% { border-color: #81c784; }
  }
</style>
```

---

## 📊 Respuesta Esperada

### Histórico de Comunicaciones

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
  {
    "id": 2,
    "device_id": "DEVICE123",
    "latitude": 19.4327,
    "longitude": -99.1333,
    ...
  }
]
```

### Stream SSE

```plaintext
event: update
data: {"device_id": "867564050638581", "latitude": 19.4326, "longitude": -99.1332, "speed": 45.5, "timestamp": "2024-01-15T10:30:00"}

event: update
data: {"device_id": "DEVICE123", "latitude": 19.4327, "longitude": -99.1333, "speed": 50.0, "timestamp": "2024-01-15T10:30:02"}
```

---

## ❌ Errores Comunes

### Error 422: Query parameter requerido

**Respuesta:**

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

---

### Error 401: Token inválido

**Respuesta:**

```json
{
  "detail": "Invalid token"
}
```

**Solución:** Verifica que el token JWT sea válido y no haya expirado.

---

### Error 404: Device no encontrado

Si usas `/devices/{device_id}/communications` con un ID inexistente:

**Respuesta:**

```json
[]
```

(Respuesta vacía, no error)\_

---

## 🔄 Migración desde Endpoints Antiguos

### ❌ ANTES (Deprecated)

```bash
# POST con body JSON
curl -X POST http://10.8.0.1:8000/communications/history \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_ids": ["867564050638581"]}'
```

### ✅ AHORA (REST v1)

```bash
# GET con query parameters
curl 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581' \
  -H "Authorization: Bearer TOKEN"
```

---

## 📚 Más Información

- **[API_REST_GUIDE.md](API_REST_GUIDE.md)** - Guía completa de la API REST
- **[MIGRATION_REST.md](MIGRATION_REST.md)** - Guía de migración detallada
- **[http://10.8.0.1:8000/api/docs](http://10.8.0.1:8000/api/docs)** - Swagger UI (documentación interactiva)

---

**¡Listo!** 🎉 Todos los ejemplos actualizados para REST v1.
