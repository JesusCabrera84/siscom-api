# 🚀 WebSocket Streaming API - Alta Performance

## 📋 Resumen

Sistema de streaming WebSocket de **alta performance**, diseñado para escalar a **decenas o cientos de conexiones simultáneas**.

### ✅ Características Principales

- **Alta escalabilidad**: Un único consumer MQTT para todas las conexiones
- **Full-duplex**: Comunicación bidireccional (WebSocket)
- **Backpressure automático**: Control de flujo cuando clientes son lentos
- **Sin buffering**: Sin problemas con ALB/nginx
- **Filtrado eficiente**: Por device_ids
- **Monitoreo en tiempo real**: Estadísticas del broker

---

## 🏗️ Arquitectura

```
                    ┌─────────────────────┐
                    │   MQTT Broker       │
                    │   (Mosquitto)       │
                    └──────────┬──────────┘
                               │
                               │ paho-mqtt
                               │
                    ┌──────────▼──────────────┐
                    │   MQTTClient            │
                    │   ✅ 1 consumer único   │
                    │   ✅ Callbacks system   │
                    └──────────┬──────────────┘
                               │
                        callback/publish
                               │
                    ┌──────────▼──────────────┐
                    │   WebSocketBroker       │
                    │   ✅ Pub/Sub interno    │
                    │   ✅ asyncio.Queue      │
                    │   ✅ Filtro device_id   │
                    └──────────┬──────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐           ┌────▼────┐          ┌────▼────┐
    │   WS 1  │           │   WS 2  │          │   WS N  │
    │ dev: A,B│           │ dev: C  │          │ dev: A  │
    └─────────┘           └─────────┘          └─────────┘
```

### Flujo de Mensajes

1. **MQTT** recibe mensaje → decodifica JSON
2. **mqtt_client** ejecuta callbacks registrados (thread-safe)
3. **mqtt_message_handler** recibe mensaje vía callback
4. **WebSocketBroker** distribuye solo a colas con ese device_id
5. **WebSocket connections** reciben y envían al cliente

**Clave de Performance:** Sin duplicación de trabajo, distribución en memoria ultra rápida.

---

## 🔌 Uso del Endpoint WebSocket

### URL del Endpoint

```
ws://localhost:8000/api/v1/stream?device_ids=DEVICE1,DEVICE2
```

### Parámetros

| Parámetro    | Tipo   | Requerido | Descripción                                    |
|-------------|--------|-----------|------------------------------------------------|
| `device_ids` | string | Sí        | Device IDs separados por comas (ej: "A,B,C")   |

### Ejemplo en JavaScript/TypeScript

```javascript
// Conectar al WebSocket
const ws = new WebSocket(
  'ws://localhost:8000/api/v1/stream?device_ids=0848086072,0848086073'
);

// Manejar conexión abierta
ws.onopen = () => {
  console.log('✅ WebSocket conectado');
};

// Manejar mensajes recibidos
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.event === 'message') {
    // Datos del dispositivo
    console.log('📡 Datos recibidos:', message.data);
  } else if (message.event === 'ping') {
    // Keep-alive (cada 60 segundos)
    console.log('💓 Keep-alive');
  }
};

// Manejar errores
ws.onerror = (error) => {
  console.error('❌ Error WebSocket:', error);
};

// Manejar cierre de conexión
ws.onclose = (event) => {
  console.log('🔌 WebSocket cerrado:', event.code, event.reason);
};
```

### Ejemplo en Python (websockets library)

```python
import asyncio
import json
import websockets

async def connect_to_stream():
    uri = "ws://localhost:8000/api/v1/stream?device_ids=0848086072"

    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket conectado")

        async for message in websocket:
            data = json.loads(message)

            if data["event"] == "message":
                print(f"📡 Datos recibidos: {data['data']}")
            elif data["event"] == "ping":
                print("💓 Keep-alive")

asyncio.run(connect_to_stream())
```

### Ejemplo en React

```jsx
import { useEffect, useState } from 'react';

function DeviceStream({ deviceIds }) {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/stream?device_ids=${deviceIds.join(',')}`
    );

    ws.onopen = () => {
      console.log('✅ WebSocket conectado');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.event === 'message') {
        setMessages((prev) => [...prev, message.data]);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ Error:', error);
    };

    ws.onclose = () => {
      console.log('🔌 Desconectado');
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [deviceIds]);

  return (
    <div>
      <h2>Estado: {connected ? '🟢 Conectado' : '🔴 Desconectado'}</h2>
      <ul>
        {messages.map((msg, idx) => (
          <li key={idx}>{JSON.stringify(msg)}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 📊 Monitoreo y Estadísticas

### Endpoint de Estadísticas

```bash
GET /api/v1/stream/stats
```

**Respuesta:**

```json
{
  "total_messages_processed": 15234,
  "active_subscribers": 45,
  "devices_being_monitored": 23
}
```

### Métricas Disponibles

| Métrica                    | Descripción                                           |
|----------------------------|-------------------------------------------------------|
| `total_messages_processed` | Total de mensajes MQTT procesados desde el inicio     |
| `active_subscribers`       | Número de suscripciones activas (colas)               |
| `devices_being_monitored`  | Número de device_ids únicos con subscribers activos   |

---

## 🔄 Formato de Mensajes

### Mensaje de Datos

```json
{
  "event": "message",
  "data": {
    "timestamp": "2024-12-11T10:30:00Z",
    "data": {
      "DEVICE_ID": "0848086072",
      "LAT": -33.4567,
      "LON": -70.6789,
      "SPEED": 45,
      ...
    }
  }
}
```

### Mensaje Keep-Alive (Ping)

```json
{
  "event": "ping",
  "data": {
    "type": "keep-alive"
  }
}
```

**Nota:** Los pings se envían automáticamente cada 60 segundos para mantener la conexión activa.

### Mensaje de Error

```json
{
  "event": "error",
  "data": {
    "message": "Debe especificar al menos un device_id en los query params"
  }
}
```

---

## 🔧 Configuración y Backpressure

### Límites de Cola

Cada WebSocket tiene colas con un máximo de **100 mensajes** por `device_id`:

```python
q = asyncio.Queue(maxsize=100)
```

### Backpressure Automático

Si un cliente WebSocket es muy lento y su cola se llena:

1. El broker detecta `q.full()` o captura `asyncio.QueueFull`
2. Se descarta el mensaje nuevo (backpressure)
3. Se registra un warning en los logs:
   ```
   Cola llena para device_id X. Aplicando backpressure (mensaje descartado)
   ```

**Esto evita:**
- ❌ Memory leaks
- ❌ Consumo infinito de RAM
- ❌ Bloqueos del broker

**Solución si ocurre frecuentemente:**
- Aumentar `maxsize` en `WebSocketBroker.subscribe()`
- Optimizar el cliente para procesar mensajes más rápido
- Reducir la frecuencia de mensajes MQTT

---

## 🧪 Testing del WebSocket

### Usando websocat (CLI)

```bash
# Instalar websocat
brew install websocat  # macOS
sudo apt install websocat  # Ubuntu

# Conectar al WebSocket
websocat "ws://localhost:8000/api/v1/stream?device_ids=0848086072"
```

### Usando Postman

1. Crear nueva request → WebSocket
2. URL: `ws://localhost:8000/api/v1/stream?device_ids=0848086072`
3. Conectar y observar mensajes entrantes

### Usando el cliente de ejemplo Python

```bash
python examples/websocket_client_example.py --device-ids 0848086072
```

### Usando el cliente de ejemplo HTML

```bash
open examples/websocket_client_example.html
```

---

## 🎯 Performance Esperado

### Benchmarks Aproximados

| Métrica                     | Valor Esperado          |
|-----------------------------|-------------------------|
| Latencia mensaje → cliente  | < 10ms                  |
| Conexiones simultáneas      | 100+ sin degradación    |
| Mensajes/segundo (total)    | 1000+ sin problema      |
| Memory overhead por WS      | ~1-2 MB                 |

### Escalabilidad

- **Vertical:** Un solo servidor puede manejar 100-500 WebSockets fácilmente
- **Horizontal:** Para > 500 conexiones, usar Redis Pub/Sub para compartir mensajes entre instancias

---

## 🔍 Troubleshooting

### El WebSocket se desconecta inmediatamente

**Causa:** No se especificaron `device_ids` en query params.

**Solución:**
```javascript
// ❌ Mal
ws://localhost:8000/api/v1/stream

// ✅ Bien
ws://localhost:8000/api/v1/stream?device_ids=0848086072
```

### No llegan mensajes

1. **Verificar que MQTT esté conectado:**
   ```bash
   # Ver logs de la aplicación
   # Debe aparecer: "✅ Bridge MQTT → WebSocket activo"
   ```

2. **Verificar estadísticas del broker:**
   ```bash
   curl http://localhost:8000/api/v1/stream/stats
   ```

3. **Verificar que el device_id esté publicando mensajes MQTT:**
   - Revisar el topic MQTT configurado
   - Confirmar que el `DEVICE_ID` en el mensaje coincida

### Mensajes se pierden (backpressure)

**Síntoma:** Logs muestran:
```
Cola llena para device_id X. Aplicando backpressure
```

**Causa:** El cliente WebSocket no procesa mensajes suficientemente rápido.

**Soluciones:**
1. Aumentar `maxsize` en `WebSocketBroker.subscribe()`
2. Optimizar el procesamiento en el cliente
3. Implementar throttling en el lado del dispositivo GPS

---

## 🔗 Endpoint Público (Share Location)

Además del endpoint principal, existe un **endpoint público** para compartir ubicaciones con usuarios externos usando tokens PASETO temporales.

### URL

```
ws://localhost:8000/api/v1/public/share-location/stream?token=v4.local.xxx...
```

### Diferencias con el Endpoint Principal

| Característica | `/api/v1/stream` | `/api/v1/public/share-location/stream` |
|----------------|------------------|----------------------------------------|
| Autenticación  | No requerida     | Token PASETO obligatorio               |
| Device IDs     | Especificados en query params | Automático desde el token      |
| Expiración     | Sin límite       | Según expiración del token PASETO      |
| Uso típico     | Apps internas    | Links compartidos a usuarios externos  |

### Flujo de Uso

1. **Obtener token PASETO** vía el endpoint `/api/v1/public/share-location/init`
2. **Conectar WebSocket** con el token en query params
3. **Recibir ubicaciones** del device_id asociado al token
4. **El token expira** → El servidor envía evento `expired` y cierra la conexión

### Eventos Especiales

```json
// Token expirado durante la conexión
{
  "event": "expired",
  "data": {
    "message": "Token expired"
  }
}
```

### Códigos de Cierre WebSocket

| Código | Razón | Descripción |
|--------|-------|-------------|
| 1008   | Policy Violation | Token inválido o expirado antes de conectar |
| 1000   | Normal Closure | Token expiró durante la conexión |

### Ejemplo JavaScript

```javascript
const token = 'v4.local.xxx...'; // Token obtenido de /init
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/public/share-location/stream?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.event) {
    case 'message':
      console.log('📍 Nueva ubicación:', data.data);
      break;
    case 'expired':
      console.log('⏰ Token expirado, solicitar nuevo token');
      ws.close();
      break;
    case 'ping':
      console.log('💓 Keep-alive');
      break;
  }
};

ws.onclose = (event) => {
  if (event.code === 1008) {
    console.log('🚫 Token inválido o expirado');
  }
};
```

---

## 📚 Referencias

- [RFC 6455 - WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Python asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)

---

## 📂 Estructura de Archivos

```
app/
├── api/
│   └── routes/
│       ├── stream.py          # WebSocket endpoint principal + broker
│       └── public.py          # WebSocket endpoint público (share-location)
├── services/
│   └── mqtt_client.py         # Cliente MQTT con callbacks
└── main.py                    # Inicialización del bridge

examples/
├── websocket_client_example.py    # Cliente Python CLI
├── websocket_client_example.html  # Cliente web interactivo
└── README.md                      # Guía de ejemplos
```

---

**Desarrollado con ❤️ para alto rendimiento y escalabilidad.**

