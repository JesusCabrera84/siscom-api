# 📚 Ejemplos de Uso - WebSocket Stream

Esta carpeta contiene ejemplos prácticos para conectarse al endpoint WebSocket de siscom-api.

El stream usa `device_id` como filtro y puede enviar dos tipos de eventos en la misma conexión:

- Posiciones
- Alertas (`message_type: alert`)

## 📁 Archivos

### 1. `websocket_client_example.py`

Cliente WebSocket en Python para testing desde la terminal.

**Requisitos:**
```bash
pip install websockets
```

**Uso:**
```bash
# Ejemplo básico
python examples/websocket_client_example.py --device-ids 0848086072

# Múltiples devices
python examples/websocket_client_example.py --device-ids 0848086072,0848086073

# Servidor remoto
python examples/websocket_client_example.py \
  --device-ids 0848086072 \
  --host api.example.com:8000

# Con permisos de ejecución
chmod +x examples/websocket_client_example.py
./examples/websocket_client_example.py --device-ids 0848086072
```

**Salida esperada:**
```
🔌 Conectando a: ws://localhost:8000/api/v1/stream?device_ids=0848086072
📡 Monitoreando devices: ['0848086072']
------------------------------------------------------------
✅ WebSocket conectado exitosamente

📦 Mensaje #1
   Device ID: 0848086072
   Timestamp: 2024-12-11T10:30:00Z
   LAT: -33.4567
   LON: -70.6789
   SPEED: 45

💓 Keep-alive recibido

🚨 Alerta recibida (message_type=alert)
    Device ID: 0848086072
    Alert Type: Engine OFF
```

---

### 2. `websocket_client_example.html`

Cliente WebSocket interactivo en HTML/JavaScript para testing desde el navegador.

**Uso:**

1. **Opción A: Abrir directamente en el navegador**
   ```bash
   # En Linux/macOS
   xdg-open examples/websocket_client_example.html
   # o
   open examples/websocket_client_example.html
   
   # En Windows
   start examples/websocket_client_example.html
   ```

2. **Opción B: Servir con un servidor local**
   ```bash
   # Python 3
   python -m http.server 8080 --directory examples
   
   # Luego abrir en navegador:
   # http://localhost:8080/websocket_client_example.html
   ```

**Características:**
- ✅ Interfaz visual moderna y responsive
- ✅ Conexión/desconexión en vivo
- ✅ Visualización de mensajes en tiempo real
- ✅ Estadísticas de conexión (uptime, mensajes, keep-alives)
- ✅ Botón para consultar estadísticas del broker
- ✅ Limpieza de mensajes

**Screenshot conceptual:**
```
┌─────────────────────────────────────────────────────┐
│ 🚀 WebSocket Client - siscom-api                   │
├─────────────────────────────────────────────────────┤
│ Host: [localhost:8000                             ] │
│ Devices: [0848086072,0848086073                   ] │
│ [🔌 Conectar] [🔌 Desconectar] [🗑️ Limpiar] [📊 Stats] │
├─────────────────────────────────────────────────────┤
│ 🟢 Conectado                                        │
├─────────────────────────────────────────────────────┤
│ [0] Mensajes | [3] Keep-alives | [127s] Uptime     │
├─────────────────────────────────────────────────────┤
│ 📦 Mensaje de 0848086072                            │
│    Timestamp: 2024-12-11T10:30:00Z                  │
│    LAT: -33.4567                                    │
│    LON: -70.6789                                    │
│                                                     │
│ 💓 Keep-alive recibido                              │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Rápido

### Testing con curl + websocat

```bash
# Instalar websocat (si no está instalado)
# macOS:
brew install websocat

# Linux:
sudo apt install websocat

# Conectar
websocat "ws://localhost:8000/api/v1/stream?device_ids=0848086072"
```

### Testing con Postman

1. Crear nueva request → **WebSocket**
2. URL: `ws://localhost:8000/api/v1/stream?device_ids=0848086072`
3. Conectar y observar mensajes entrantes

---

## 📊 Consultar Estadísticas del Broker

```bash
# Con curl
curl http://localhost:8000/api/v1/stream/stats

# Respuesta esperada:
{
  "total_messages_processed": 15234,
  "active_subscribers": 45,
  "devices_being_monitored": 23
}
```

---

## 🐛 Troubleshooting

### Error: "Must specify at least one device_id"

**Causa:** No se proporcionaron device_ids en la URL.

**Solución:**
```bash
# ❌ Mal
ws://localhost:8000/api/v1/stream

# ✅ Bien
ws://localhost:8000/api/v1/stream?device_ids=0848086072
```

---

### Error de conexión (Connection refused)

**Causa:** El servidor no está corriendo o la URL es incorrecta.

**Verificar:**
```bash
# 1. Verificar que el servidor esté corriendo
curl http://localhost:8000/health

# 2. Verificar logs del servidor
# Debe aparecer: "✅ Bridge Kafka → WebSocket activo"
```

---

### No llegan mensajes

**Verificar:**

1. **Kafka está conectado:**
   - Ver logs del servidor
   - Buscar: "Conectado exitosamente a Kafka/Redpanda"

2. **El device_id está publicando:**
   - Verificar que el dispositivo GPS esté enviando datos
   - Verificar que el `DEVICE_ID` en el mensaje Kafka coincida

3. **Estadísticas del broker:**
   ```bash
   curl http://localhost:8000/api/v1/stream/stats
   ```

---

## 🔗 Endpoint Público (Share Location)

Existe un endpoint WebSocket público para compartir ubicaciones con usuarios externos usando tokens PASETO temporales:

### URL
```
ws://localhost:8000/api/v1/public/share-location/stream?token=v4.local.xxx...
```

### Características
- ✅ **Autenticación por token PASETO** (no requiere JWT)
- ✅ **Expiración automática** del token durante la conexión
- ✅ **Filtra automáticamente** por el `device_id` del token
- ✅ **Keep-alive** cada 60 segundos

### Ejemplo JavaScript

```javascript
const token = 'v4.local.xxx...'; // Token PASETO obtenido de /init
const ws = new WebSocket(`ws://localhost:8000/api/v1/public/share-location/stream?token=${token}`);

ws.onopen = () => console.log('Conectado al stream público');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.event === 'message') {
        console.log('📍 Nueva ubicación:', data.data);
    } else if (data.event === 'expired') {
        console.log('⏰ Token expirado, solicitar nuevo token');
        ws.close();
    } else if (data.event === 'ping') {
        console.log('💓 Keep-alive');
    }
};

ws.onclose = (event) => {
    if (event.code === 1008) {
        console.log('🚫 Token inválido o expirado');
    }
};
```

### Diferencias con el endpoint privado

| Característica | `/api/v1/stream` | `/api/v1/public/share-location/stream` |
|----------------|------------------|----------------------------------------|
| Autenticación | No requerida | Token PASETO |
| Device IDs | Especificados en query | Automático del token |
| Expiración | Sin límite | Según token PASETO |
| Uso típico | Apps internas | Links compartidos externos |

---

## 📚 Más Información

Ver la documentación completa en:
- [`/docs/WEBSOCKET_STREAMING.md`](../docs/WEBSOCKET_STREAMING.md) - Guía completa de uso
- [`/docs/SSE_HTTP2_FIX.md`](../docs/SSE_HTTP2_FIX.md) - Contexto histórico (SSE deprecado)

---

## 🤝 Contribuir

Si creas un cliente de ejemplo en otro lenguaje (Go, Rust, Java, etc.), ¡agrega el archivo aquí!

**Idiomas deseados:**
- [ ] Go
- [ ] Rust
- [ ] Java/Kotlin
- [ ] Swift (iOS)
- [ ] Dart (Flutter)
- [ ] React Native

---

¿Preguntas? Contactar al equipo de desarrollo.

