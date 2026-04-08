# Integración Kafka/Redpanda con SISCOM API

Esta guía explica cómo funciona la integración de Kafka/Redpanda para el streaming de eventos en tiempo real mediante WebSocket.

## Configuración

### Variables de Entorno

Las siguientes variables de entorno deben configurarse:

```bash
# Kafka/Redpanda Configuration
KAFKA_BOOTSTRAP_SERVERS=<servidores_bootstrap>    # Ejemplo: localhost:9092,kafka1:9092,kafka2:9092
KAFKA_TOPIC=<topic_posiciones>                    # Ejemplo: tracking/data
KAFKA_ALERTS_TOPIC=<topic_alertas>                # Ejemplo: tracking/alerts (opcional)
KAFKA_GROUP_ID=<group_id>                         # Ejemplo: siscom-api-consumer
KAFKA_AUTO_OFFSET_RESET=<offset_reset>            # Ejemplo: latest o earliest
KAFKA_USERNAME=<usuario>                          # Usuario del cluster Kafka (opcional)
KAFKA_PASSWORD=<contraseña>                        # Contraseña del cluster Kafka (opcional)
KAFKA_SASL_MECHANISM=SCRAM-SHA-256                # Mecanismo SASL (opcional)
KAFKA_SECURITY_PROTOCOL=SASL_PLAINTEXT            # Protocolo de seguridad (opcional)

# Circuit Breaker / Resiliencia
KAFKA_MAX_RETRIES=5                               # Reintentos máximos antes de abrir circuito
KAFKA_CIRCUIT_BREAKER_COOLDOWN=300                # Cooldown en segundos cuando el circuito está abierto
```

### Docker Compose

Las variables Kafka ya están configuradas en `docker-compose.yml` y se cargan automáticamente desde el entorno o archivo `.env`.

## Arquitectura

```
┌─────────────┐         ┌─────────────────┐         ┌─────────────┐
│             │  Kafka  │                 │   WS    │             │
│ Redpanda/   ├────────►│  siscom-api     ├────────►│   Cliente   │
│ Kafka       │         │                 │         │     Web     │
└─────────────┘         └─────────────────┘         └─────────────┘
```

### Componentes

1. **KafkaClient** (`app/services/kafka_client.py`):
   - Cliente Kafka que se conecta al cluster Redpanda/Kafka
  - Se suscribe a uno o dos topics en un único consumer (`KAFKA_TOPIC` + opcional `KAFKA_ALERTS_TOPIC`)
  - Propaga callbacks con metadatos de Kafka (`topic`, `payload`, `timestamp`, `partition`, `offset`)
   - Maneja reconexiones automáticas en caso de fallos
   - Usa threading para consumir mensajes sin bloquear el event loop

2. **WebSocket Stream** (`app/api/routes/stream.py`):
   - Endpoint `/api/v1/stream` que expone eventos WebSocket
  - Enruta posiciones y alertas por `device_id`
  - Filtra mensajes por `device_ids` especificados por el cliente
   - Envía keep-alive cada 60 segundos

3. **Lifecycle Management** (`app/main.py`):
   - Inicializa el cliente Kafka al iniciar la aplicación
   - Maneja errores de conexión sin detener la aplicación
   - Desconecta el cliente Kafka al cerrar la aplicación

4. **Circuit Breaker** (resiliencia):
   - Previene reintentos infinitos cuando Kafka no está disponible
   - Tras `KAFKA_MAX_RETRIES` fallos consecutivos, el circuito se abre
   - Durante el periodo de cooldown (`KAFKA_CIRCUIT_BREAKER_COOLDOWN`), no se intentan reconexiones
   - Reduce spam de logs y carga del sistema cuando Kafka está caído
   - El estado del circuito se expone en el endpoint `/health`
   - Se reporta como métrica `kafka_circuit_breaker_open` (1=abierto, 0=cerrado)

## Formato de Mensaje

### Posiciones (`KAFKA_TOPIC`)

Se conserva el formato actual de posiciones; el `device_id` puede llegar en `data.device_id` o en raíz.

```json
{
  "data": {
    "device_id": "0848086072",
    "latitude": 20.652472,
    "longitude": -100.391423
  }
}
```

### Alertas (`KAFKA_ALERTS_TOPIC`)

El payload de alertas debe incluir `device_id` (raíz, `data.device_id` o `payload.device_id`).

```json
{
  "id": "5e29d441-16c6-43f2-ba48-650ea9946a58",
  "device_id": "0848086072",
  "alert_type": "Engine OFF",
  "payload": {
    "engine_status": "OFF",
    "latitude": 19.216813,
    "longitude": -102.575137
  },
  "occurred_at": "2026-03-29T20:56:34Z"
}
```

Salida al cliente WebSocket para alertas:

```json
{
  "event": "alert",
  "data": {
    "message_type": "alert",
    "source_topic": "tracking/alerts",
    "data": {
      "device_id": "0848086072",
      "alert_type": "Engine OFF"
    }
  }
}
```

## Uso del Endpoint WebSocket

### Conectarse al Stream

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream?device_ids=0848086072');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === 'message') {
    console.log('📍 Posición:', message.data);
  } else if (message.event === 'alert') {
    console.log('🚨 Alerta:', message.data);
  } else if (message.event === 'ping') {
    console.log('💓 Keep-alive');
  }
};
```

### Filtrar por Device IDs

Para recibir solo eventos de dispositivos específicos:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream?device_ids=0848086072,0848086073');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === 'message') {
    console.log('📍 Posición:', message.data);
  } else if (message.event === 'alert') {
    console.log('🚨 Alerta:', message.data);
  }
};
```

### Cliente JavaScript Completo

```javascript
const eventSource = new WebSocket("/api/v1/stream?device_ids=0848086072");

eventSource.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === "message") {
    console.log("Posición recibida:", message.data);
  } else if (message.event === "alert") {
    console.log("Alerta recibida:", message.data);
  } else if (message.event === "ping") {
    console.log("Keep-alive");
  }
};

eventSource.onopen = (event) => {
  console.log("Conexión WebSocket abierta");
};

eventSource.onerror = (error) => {
  console.error("Error en WebSocket:", error);
  eventSource.close();
};

eventSource.onclose = (event) => {
  console.log("Conexión WebSocket cerrada");
};
```

## Manejo de Errores

El cliente Kafka maneja errores de manera resiliente:

1. **Error de Conexión**: Si no puede conectarse al cluster, registra el error pero no detiene la aplicación
2. **Desconexión Inesperada**: Intenta reconectar automáticamente con backoff exponencial (máximo 30 segundos)
3. **Circuit Breaker**: Tras `KAFKA_MAX_RETRIES` (default: 5) fallos consecutivos:
   - El circuito se abre y se detienen los reintentos
   - Se registra un log crítico único (evita spam)
   - Después del cooldown (`KAFKA_CIRCUIT_BREAKER_COOLDOWN`, default: 300s), el circuito se cierra y se reintenta
4. **Mensajes Malformados**: Registra el error y continúa procesando otros mensajes
5. **Cliente No Conectado**: El stream WebSocket espera eventos una vez que Kafka entrega mensajes
6. **Compresión lz4**: La librería `lz4` está instalada para soportar mensajes comprimidos con codec lz4

## Logs

Los logs del cliente Kafka incluyen:

- Información de conexión exitosa
- Errores de conexión
- Mensajes recibidos (nivel DEBUG)
- Desconexiones
- Errores al procesar mensajes

Para ver logs detallados, configura el nivel de logging:

```python
logging.getLogger("app.services.kafka_client").setLevel(logging.DEBUG)
```

## Métricas

El sistema de métricas incluye:

- **Conexiones activas WebSocket**: Número de clientes conectados al stream
- Las métricas se envían a StatsD configurado en `STATSD_HOST`

## Troubleshooting

### El cliente no se conecta al cluster Kafka

1. Verifica que las variables de entorno estén configuradas correctamente
2. Verifica la conectividad de red al cluster Kafka/Redpanda
3. Revisa los logs de la aplicación
4. Verifica las credenciales Kafka si están configuradas

### No se reciben mensajes

1. Verifica que los topics configurados sean correctos (`KAFKA_TOPIC` y opcional `KAFKA_ALERTS_TOPIC`)
2. Verifica que el cluster esté publicando mensajes al topic
3. Revisa los logs en nivel DEBUG
4. Verifica que el formato JSON del mensaje sea correcto
5. Verifica que el mensaje incluya `device_id` para poder enrutar al WebSocket
6. Verifica que el `KAFKA_GROUP_ID` sea único para evitar conflictos

### El stream WebSocket se desconecta

1. Verifica que el cliente WebSocket soporte conexiones WebSocket
2. Verifica proxies/load balancers que puedan estar cerrando conexiones largas
3. Los keep-alive se envían cada 60 segundos para mantener la conexión activa

## Desarrollo Local

Para probar localmente sin cluster Kafka/Redpanda:

1. El sistema no fallará si no puede conectarse a Kafka
2. Los logs mostrarán el error de conexión
3. El endpoint `/stream` responderá pero no recibirá mensajes

Para un entorno completo de desarrollo, considera usar Docker Compose con Redpanda:

```yaml
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    ports:
      - "9092:9092"
      - "9644:9644"
    command:
      - redpanda start
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:9092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:9092
      - --pandaproxy-addr 0.0.0.0:8082
      - --advertise-pandaproxy-addr localhost:8082
```

## Seguridad

- Las credenciales Kafka se configuran mediante variables de entorno
- No se hardcodean credenciales en el código
- El cluster Kafka debe configurarse con autenticación SASL/PLAIN si es necesario
- Considera usar TLS/SSL para comunicación con el cluster en producción