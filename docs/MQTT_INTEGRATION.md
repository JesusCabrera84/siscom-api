# Integración MQTT con Mosquitto

Esta guía explica cómo funciona la integración de MQTT con Mosquitto para el streaming de eventos en tiempo real mediante Server-Sent Events (SSE).

## Configuración

### Variables de Entorno

Las siguientes variables de entorno deben configurarse en GitHub Secrets y en tu archivo `.env` local:

```bash
# MQTT Configuration
BROKER_HOST=<ip>:<puerto>          # Ejemplo: mosquitto.example.com:1883
BROKER_TOPIC=<topic>                # Ejemplo: devices/telemetry o # para todos
MQTT_USERNAME=<usuario>             # Usuario del broker MQTT
MQTT_PASSWORD=<contraseña>          # Contraseña del broker MQTT
```

### Docker Compose

Las variables MQTT ya están configuradas en `docker-compose.yml` y se cargan automáticamente desde el entorno o archivo `.env`.

## Arquitectura

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │  MQTT   │              │   SSE   │             │
│  Mosquitto  ├────────►│  siscom-api  ├────────►│   Cliente   │
│   Broker    │         │              │         │     Web     │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Componentes

1. **MQTTClient** (`app/services/mqtt_client.py`):
   - Cliente MQTT que se conecta al broker Mosquitto
   - Se suscribe al topic configurado
   - Maneja mensajes entrantes y los coloca en una cola asíncrona
   - Maneja reconexiones automáticas en caso de fallos

2. **Stream SSE** (`app/api/routes/stream.py`):
   - Endpoint `/api/v1/stream` que expone eventos SSE
   - Consume mensajes de la cola MQTT
   - Filtra mensajes por `device_ids` si se especifican
   - Envía keep-alive cada 60 segundos

3. **Lifecycle Management** (`app/main.py`):
   - Inicializa el cliente MQTT al iniciar la aplicación
   - Maneja errores de conexión sin detener la aplicación
   - Desconecta el cliente MQTT al cerrar la aplicación

## Formato de Mensaje

Los mensajes recibidos desde Mosquitto deben tener el siguiente formato JSON:

```json
{
  "data": {
    "DEVICE_ID": "0848086072",
    "LATITUD": "+20.652472",
    "LONGITUD": "-100.391423",
    "SPEED": "0.00",
    "GPS_DATETIME": "2025-10-18 00:51:16",
    "ENGINE_STATUS": "OFF",
    "SATELLITES": "9",
    ...
  },
  "decoded": { ... },
  "metadata": { ... },
  "raw": "...",
  "uuid": "..."
}
```

El campo `data.DEVICE_ID` se utiliza para filtrar mensajes por dispositivo.

## Uso del Endpoint SSE

### Recibir Todos los Eventos

```bash
curl -N http://localhost:8000/api/v1/stream
```

### Filtrar por Device IDs

Para recibir solo eventos de dispositivos específicos:

```bash
curl -N "http://localhost:8000/api/v1/stream?device_ids=0848086072,0848086073"
```

### Cliente JavaScript

```javascript
const eventSource = new EventSource("/api/v1/stream?device_ids=0848086072");

eventSource.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  console.log("Evento recibido:", data);
});

eventSource.addEventListener("ping", (event) => {
  console.log("Keep-alive recibido");
});

eventSource.onerror = (error) => {
  console.error("Error en SSE:", error);
  eventSource.close();
};
```

## Manejo de Errores

El cliente MQTT maneja errores de manera resiliente:

1. **Error de Conexión**: Si no puede conectarse al broker, registra el error pero no detiene la aplicación
2. **Desconexión Inesperada**: Intenta reconectar automáticamente
3. **Mensajes Malformados**: Registra el error y continúa procesando otros mensajes
4. **Cliente No Conectado**: El stream SSE espera hasta que el cliente MQTT se conecte

## Logs

Los logs del cliente MQTT incluyen:

- Información de conexión exitosa
- Errores de conexión
- Mensajes recibidos (nivel DEBUG)
- Desconexiones
- Errores al procesar mensajes

Para ver logs detallados, configura el nivel de logging:

```python
logging.getLogger("app.services.mqtt_client").setLevel(logging.DEBUG)
```

## Métricas

El sistema de métricas incluye:

- **Conexiones activas SSE**: Número de clientes conectados al stream
- Las métricas se envían a StatsD configurado en `STATSD_HOST`

## Troubleshooting

### El cliente no se conecta al broker

1. Verifica que las variables de entorno estén configuradas correctamente
2. Verifica la conectividad de red al broker
3. Revisa los logs de la aplicación
4. Verifica las credenciales MQTT

### No se reciben mensajes

1. Verifica que el topic configurado sea correcto
2. Verifica que el broker esté publicando mensajes
3. Revisa los logs en nivel DEBUG
4. Verifica que el formato JSON del mensaje sea correcto

### El stream SSE se desconecta

1. Verifica que el cliente HTTP soporte SSE
2. Verifica proxies/load balancers que puedan estar cerrando conexiones largas
3. Los keep-alive se envían cada 30 segundos para mantener la conexión activa

## Desarrollo Local

Para probar localmente sin broker MQTT:

1. El sistema no fallará si no puede conectarse a MQTT
2. Los logs mostrarán el error de conexión
3. El endpoint `/stream` responderá pero no recibirá mensajes

Para un entorno completo de desarrollo, considera usar Docker Compose con Mosquitto:

```yaml
services:
  mosquitto:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
```

## Seguridad

- Las credenciales MQTT se configuran mediante variables de entorno
- No se hardcodean credenciales en el código
- El broker MQTT debe configurarse con autenticación
- Considera usar TLS/SSL para comunicación con el broker en producción
