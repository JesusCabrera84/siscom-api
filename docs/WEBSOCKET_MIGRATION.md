# 🚀 Migración SSE → WebSocket de Alta Performance

## 📋 Resumen de Cambios

Se ha implementado una arquitectura WebSocket de alta performance para reemplazar Server-Sent Events (SSE), diseñada para escalar eficientemente a decenas o cientos de conexiones simultáneas.

### ✅ Ventajas sobre SSE

1. **Sin problemas de buffering**: Los ALB de AWS y nginx no interferirán con WebSocket
2. **Full-duplex**: Comunicación bidireccional (aunque actualmente solo servidor → cliente)
3. **Menor overhead**: Protocolo más eficiente que HTTP/1.1 SSE
4. **Mejor soporte móvil**: Especialmente en React Native y apps nativas
5. **Backpressure natural**: Control de flujo automático cuando un cliente es lento
6. **Escalabilidad**: Un único consumer MQTT para todas las conexiones

---

## 🏗️ Arquitectura Implementada

### Componentes

```
┌─────────────────┐
│   MQTT Broker   │
│   (Mosquitto)   │
└────────┬────────┘
         │
         │ paho-mqtt
         │
    ┌────▼────────────────────┐
    │   MQTTClient            │
    │   (mqtt_client.py)      │
    │   - Callbacks system    │
    └────┬────────────────────┘
         │
         │ callback
         │
    ┌────▼─────────────────────┐
    │   WebSocketBroker        │
    │   (stream.py)            │
    │   - Pub/Sub interno      │
    │   - asyncio.Queue        │
    └────┬─────────────────────┘
         │
         │ distribuye mensajes
         │
    ┌────▼─────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  WebSocket #1    │    │  WebSocket #2   │    │  WebSocket #N   │
    │  device_ids:     │    │  device_ids:    │    │  device_ids:    │
    │  [A, B]          │    │  [C]            │    │  [A]            │
    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

### Flujo de Mensajes

1. **MQTT** recibe un mensaje del broker Mosquitto
2. **mqtt_client** decodifica JSON y ejecuta callbacks registrados
3. **mqtt_message_handler** recibe el mensaje vía callback
4. **WebSocketBroker** distribuye el mensaje solo a las colas suscritas al `DEVICE_ID`
5. **WebSocket connections** reciben el mensaje de su cola y lo envían al cliente

### Clave de Performance

- ✅ **Un solo consumer MQTT** para todas las conexiones
- ✅ **No duplicación de trabajo** en decodificación/parseo
- ✅ **Distribución en memoria** ultra rápida con `asyncio.Queue`
- ✅ **Filtrado eficiente** por device_id antes de enviar

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

// Cerrar conexión manualmente
// ws.close();
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

## 🛠️ Archivos Modificados

### 1. `app/api/routes/stream.py`

**Cambios principales:**
- ✅ Clase `WebSocketBroker` para pub/sub interno
- ✅ Endpoint WebSocket `@router.websocket("/stream")`
- ✅ Handler `mqtt_message_handler` para recibir mensajes MQTT
- ✅ Función `start_mqtt_broker_bridge()` para inicializar el puente
- ✅ Endpoint de estadísticas `GET /stream/stats`
- ⚠️ SSE endpoint mantenido como legacy (puede removerse después)

### 2. `app/services/mqtt_client.py`

**Cambios principales:**
- ✅ Sistema de callbacks: `_message_callbacks`
- ✅ Método `register_message_callback()` para suscribir callbacks
- ✅ Método `unregister_message_callback()` para desuscribir
- ✅ Modificación en `_on_message()` para ejecutar callbacks

### 3. `app/main.py`

**Cambios principales:**
- ✅ Import de `start_mqtt_broker_bridge`
- ✅ Inicialización del bridge en el startup del `lifespan`

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

### Usando curl + websocat

```bash
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
  http://localhost:8000/api/v1/stream?device_ids=0848086072
```

### Usando Postman

1. Crear nueva request → WebSocket
2. URL: `ws://localhost:8000/api/v1/stream?device_ids=0848086072`
3. Conectar y observar mensajes entrantes

---

## 🚦 Migración desde SSE

### SSE (Antiguo)

```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/v1/stream?device_ids=0848086072'
);

eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
});
```

### WebSocket (Nuevo)

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/api/v1/stream?device_ids=0848086072'
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === 'message') {
    console.log(message.data);
  }
};
```

### Diferencias Clave

| Aspecto              | SSE                          | WebSocket                    |
|---------------------|------------------------------|------------------------------|
| Protocolo           | HTTP/1.1 (unidireccional)    | WS (bidireccional)           |
| Buffering en ALB    | ❌ Problemático              | ✅ Sin problemas             |
| Overhead            | Alto (HTTP headers)          | Bajo (frames pequeños)       |
| Reconexión auto     | ✅ Nativa en EventSource     | ⚠️ Manual en WebSocket       |
| Formato de mensaje  | `event` + `data` separados   | JSON con `{"event": "..."}`  |

---

## 📝 Retrocompatibilidad

El endpoint SSE **se mantiene funcionando** en `/api/v1/stream` (GET):

```bash
# SSE sigue funcionando (legacy)
curl -N http://localhost:8000/api/v1/stream?device_ids=0848086072
```

Esto permite una **migración gradual** de clientes:
1. Nuevos clientes → usar WebSocket
2. Clientes existentes → seguir usando SSE
3. Eventualmente deprecar y remover SSE

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
   # Debe aparecer: "✅ MQTT → WebSocket Broker bridge iniciado"
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

## 📚 Referencias

- [RFC 6455 - WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Python asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)

---

## ✅ Checklist de Implementación

- [x] Crear clase `WebSocketBroker` con pub/sub interno
- [x] Implementar sistema de callbacks en `MQTTClient`
- [x] Crear endpoint WebSocket `/stream`
- [x] Inicializar bridge MQTT → Broker en startup
- [x] Agregar endpoint de estadísticas `/stream/stats`
- [x] Implementar backpressure automático
- [x] Mantener SSE como legacy para retrocompatibilidad
- [x] Documentar uso y migración

---

**¿Preguntas?** Contactar al equipo de desarrollo.

