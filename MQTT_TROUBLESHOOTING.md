# Solución de Problemas - MQTT y StatsD

## Error MQTT: Código 7

### ¿Qué es el código de error 7?

El **código de error 7** en MQTT significa **"Error de conexión de red / Broker rechaza la conexión"**. Este error generalmente ocurre cuando:

1. **Cliente duplicado**: Múltiples clientes intentan conectarse con el mismo `client_id`
2. **Problemas de red**: Latencia, paquetes perdidos, o conexión inestable
3. **Keep-alive muy corto**: El broker desconecta por no recibir ping a tiempo
4. **Broker sobrecargado**: El servidor está rechazando nuevas conexiones
5. **Credenciales incorrectas o expiradas**

## Cambios Implementados

### 1. Client ID Único
```python
# ANTES: Client ID estático (causaba conflictos)
client_id=f"siscom-api-{settings.APP_NAME}"

# AHORA: Client ID único por instancia
unique_client_id = f"siscom-api-{settings.APP_NAME}-{uuid.uuid4().hex[:8]}"
```

**Por qué**: Si tienes múltiples instancias o reinicios rápidos, el broker desconecta la conexión anterior cuando detecta el mismo client_id.

### 2. Clean Session False
```python
# ANTES
clean_session=True

# AHORA
clean_session=False
```

**Por qué**: Con `clean_session=False`, el broker mantiene las suscripciones y mensajes pendientes incluso si el cliente se desconecta temporalmente.

### 3. Keep-alive Incrementado
```python
# ANTES
keepalive=60

# AHORA
keepalive=120
```

**Por qué**: Un keep-alive más largo tolera mejor latencias de red y evita desconexiones por timeouts prematuros.

### 4. Reconexión Automática Configurada
```python
self.client.reconnect_delay_set(min_delay=1, max_delay=120)
self.client.max_inflight_messages_set(20)
self.client.max_queued_messages_set(0)
```

**Por qué**: Mejora la resiliencia del cliente ante desconexiones temporales.

### 5. Versión de Protocolo Explícita
```python
protocol=mqtt.MQTTv311
```

**Por qué**: Especificar la versión evita negociaciones que pueden fallar.

### 6. Mejor Logging
Ahora los logs incluyen:
- Descripción del error específico
- Contador de intentos de reconexión
- Client ID usado en la conexión

## Verificaciones Adicionales

Si el problema persiste, verifica:

### 1. Conexión al Broker
```bash
# Probar conexión con mosquitto_sub
mosquitto_sub -h 34.237.30.30 -p 1883 \
  -u administrator \
  -P "ewioquiowuqpweiqouewqpDDSa4asda55" \
  -t "tracking/data" \
  -v
```

### 2. Límites del Broker
Consulta con el administrador del broker:
- ¿Hay límite de conexiones simultáneas?
- ¿Hay timeout de inactividad configurado?
- ¿Las credenciales están vigentes?

### 3. Red y Firewall
```bash
# Verificar conectividad
ping 34.237.30.30

# Verificar puerto MQTT
telnet 34.237.30.30 1883

# O con netcat
nc -zv 34.237.30.30 1883
```

### 4. Variables de Entorno
Verifica que estén configuradas en tu `.env`:
```env
BROKER_HOST=34.237.30.30:1883
BROKER_TOPIC=tracking/data
MQTT_USERNAME=administrator
MQTT_PASSWORD=tu_password_aquí
```

## Códigos de Error MQTT Comunes

| Código | Significado |
|--------|-------------|
| 0 | Conexión exitosa |
| 1 | Versión de protocolo inaceptable |
| 2 | Client ID rechazado |
| 3 | Servidor no disponible |
| 4 | Usuario o contraseña incorrectos |
| 5 | No autorizado |
| 7 | **Error de conexión de red / Broker rechaza la conexión** |

## Monitoreo

Puedes monitorear la estabilidad de la conexión observando los logs:
- Si `_reconnect_attempts` aumenta constantemente, hay un problema de red
- Si se conecta y desconecta inmediatamente, verifica client_id duplicados
- Si tarda mucho en reconectar, revisa el broker

## Contacto con el Administrador del Broker

Si el problema persiste, pregunta al administrador:
1. ¿Hay otros clientes conectados con el mismo client_id?
2. ¿Cuál es el timeout de keep-alive configurado en el broker?
3. ¿Hay límite de conexiones por IP?
4. ¿Los logs del broker muestran algún error?

---

## Error StatsD: Connection Refused

### ¿Qué es este error?

```
aio_statsd.client - ERROR - status:False error: [Errno 111] Connection refused
ConnectionRefusedError: [Errno 111] Connection refused
```

Este error indica que tu aplicación intenta enviar métricas a un servidor **StatsD/Telegraf** que no está disponible o corriendo.

### ¿Es crítico?

**No.** StatsD solo se usa para métricas de monitoreo (latencias, contadores, etc.). Tu aplicación funcionará perfectamente sin él.

### Solución Implementada

He configurado la aplicación para que **StatsD sea opcional**:

1. **Por defecto está deshabilitado** para evitar estos errores:

```python
# app/core/config.py
STATSD_ENABLED: bool = False  # Cambiar a True cuando tengas StatsD corriendo
```

2. **El código verifica la configuración** antes de intentar conectarse
3. **Si la conexión falla**, se deshabilita automáticamente para evitar reintentos

### ¿Cómo habilitar StatsD?

Si quieres usar métricas de monitoreo:

#### Opción 1: Usando Docker (Recomendado)

1. **Instalar Telegraf con Docker**:

```bash
docker run -d \
  --name telegraf \
  --restart always \
  -p 8126:8126/udp \
  -v $PWD/telegraf-siscom-addon.conf:/etc/telegraf/telegraf.conf:ro \
  telegraf
```

2. **Habilitar en tu `.env`**:

```env
STATSD_ENABLED=true
STATSD_HOST=localhost
STATSD_PORT=8126
```

3. **Reiniciar la aplicación**

#### Opción 2: Sin StatsD (Modo Actual)

Simplemente déjalo como está (`STATSD_ENABLED=false`). La aplicación funcionará sin problemas.

### Verificar que StatsD está escuchando

```bash
# Verificar que el puerto está abierto
nc -zvu localhost 8126

# O con netstat
netstat -an | grep 8126
```

### Variables de Entorno para StatsD

```env
# Deshabilitar StatsD (por defecto)
STATSD_ENABLED=false

# Habilitar StatsD (cuando tengas el servidor corriendo)
STATSD_ENABLED=true
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api
```

**IMPORTANTE**: Con `STATSD_ENABLED=false`, **no verás más estos errores** y la aplicación funcionará normalmente.

