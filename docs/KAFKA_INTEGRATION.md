# Integración Kafka/Redpanda con SISCOM API

Esta guía explica cómo funciona la integración de Kafka/Redpanda para el streaming de eventos en tiempo real mediante WebSocket.

## Configuración

### Variables de Entorno

Las siguientes variables de entorno deben configurarse:

```bash
# Kafka/Redpanda Configuration
KAFKA_BOOTSTRAP_SERVERS=<servidores_bootstrap>    # Ejemplo: localhost:9092,kafka1:9092,kafka2:9092
KAFKA_TOPIC=<topic>                               # Ejemplo: tracking/data
KAFKA_GROUP_ID=<group_id>                         # Ejemplo: siscom-api-consumer
KAFKA_AUTO_OFFSET_RESET=<offset_reset>            # Ejemplo: latest o earliest
KAFKA_USERNAME=<usuario>                          # Usuario del cluster Kafka (opcional)
KAFKA_PASSWORD=<contraseña>                        # Contraseña del cluster Kafka (opcional)
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
   - Se suscribe al topic configurado
   - Maneja mensajes entrantes y los coloca en una cola asíncrona
   - Maneja reconexiones automáticas en caso de fallos
   - Usa threading para consumir mensajes sin bloquear el event loop

2. **WebSocket Stream** (`app/api/routes/stream.py`):
   - Endpoint `/api/v1/stream` que expone eventos WebSocket
   - Consume mensajes del cliente Kafka
   - Filtra mensajes por `device_ids` si se especifican
   - Envía keep-alive cada 60 segundos

3. **Lifecycle Management** (`app/main.py`):
   - Inicializa el cliente Kafka al iniciar la aplicación
   - Maneja errores de conexión sin detener la aplicación
   - Desconecta el cliente Kafka al cerrar la aplicación

## Formato de Mensaje

Los mensajes recibidos desde Kafka/Redpanda deben tener el siguiente formato JSON:

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

## Uso del Endpoint WebSocket

### Recibir Todos los Eventos

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Mensaje recibido:', data);
};
```

### Filtrar por Device IDs

Para recibir solo eventos de dispositivos específicos:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream?device_ids=0848086072,0848086073');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Mensaje recibido:', data);
};
```

### Cliente JavaScript Completo

```javascript
const eventSource = new WebSocket("/api/v1/stream?device_ids=0848086072");

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Evento recibido:", data);
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
2. **Desconexión Inesperada**: Intenta reconectar automáticamente con backoff exponencial
3. **Mensajes Malformados**: Registra el error y continúa procesando otros mensajes
4. **Cliente No Conectado**: El stream WebSocket espera hasta que el cliente Kafka se conecte

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

1. Verifica que el topic configurado sea correcto
2. Verifica que el cluster esté publicando mensajes al topic
3. Revisa los logs en nivel DEBUG
4. Verifica que el formato JSON del mensaje sea correcto
5. Verifica que el `KAFKA_GROUP_ID` sea único para evitar conflictos

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