# 📚 Ejemplos de Uso - WebSocket Stream

Esta carpeta contiene ejemplos prácticos para conectarse al endpoint WebSocket de siscom-api.

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
# Debe aparecer: "✅ Bridge MQTT → WebSocket activo"
```

---

### No llegan mensajes

**Verificar:**

1. **MQTT está conectado:**
   - Ver logs del servidor
   - Buscar: "Conectado exitosamente al broker MQTT"

2. **El device_id está publicando:**
   - Verificar que el dispositivo GPS esté enviando datos
   - Verificar que el `DEVICE_ID` en el mensaje MQTT coincida

3. **Estadísticas del broker:**
   ```bash
   curl http://localhost:8000/api/v1/stream/stats
   ```

---

## 📚 Más Información

Ver la documentación completa en:
- [`/docs/WEBSOCKET_MIGRATION.md`](../docs/WEBSOCKET_MIGRATION.md) - Guía completa de migración y uso
- [`/docs/SSE_HTTP2_FIX.md`](../docs/SSE_HTTP2_FIX.md) - Contexto histórico del problema con SSE

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

