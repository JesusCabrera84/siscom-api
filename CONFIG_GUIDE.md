# Guía de Configuración - Variables de Entorno

Esta guía documenta todas las variables de entorno que puedes configurar en tu archivo `.env`.

## Información de la Aplicación

```env
APP_NAME=siscom-api
APP_VERSION=0.1.0
```

## Base de Datos PostgreSQL

```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=tu_usuario
DB_PASSWORD=tu_password
DB_DATABASE=tu_database
DB_MIN_CONNECTIONS=10
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT_SECS=30
DB_IDLE_TIMEOUT_SECS=300
```

## Seguridad JWT

```env
JWT_SECRET_KEY=tu_clave_secreta_super_segura_aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**⚠️ IMPORTANTE**: Genera una clave segura para producción:

```bash
openssl rand -hex 32
```

## CORS (Cross-Origin Resource Sharing)

```env
# Permitir todos los orígenes (desarrollo)
ALLOWED_ORIGINS=*

# Permitir orígenes específicos (producción)
ALLOWED_ORIGINS=https://tudominio.com,https://app.tudominio.com
```

## MQTT Configuration

```env
BROKER_HOST=34.237.30.30:1883
BROKER_TOPIC=tracking/data
MQTT_USERNAME=tu_usuario_mqtt
MQTT_PASSWORD=tu_password_mqtt
```

### Notas sobre MQTT:

- `BROKER_HOST`: Puede incluir el puerto (ej: `host:1883`) o solo el host (por defecto usa puerto 1883)
- `BROKER_TOPIC`: Topic al que te suscribirás
- Las credenciales son **opcionales** si tu broker no requiere autenticación

## StatsD/Telegraf (Métricas - OPCIONAL)

```env
# Deshabilitar métricas (por defecto, sin errores)
STATSD_ENABLED=false

# Habilitar métricas (solo si tienes Telegraf/StatsD corriendo)
STATSD_ENABLED=true
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api
```

### ¿Cuándo habilitar StatsD?

- **`STATSD_ENABLED=false`** (Recomendado para empezar):
  - No verás errores de conexión
  - La aplicación funcionará sin problemas
  - No tendrás métricas en Grafana

- **`STATSD_ENABLED=true`** (Solo si tienes el servidor):
  - Necesitas Telegraf/StatsD corriendo en el puerto configurado
  - Obtendrás métricas de latencia, requests, conexiones SSE, etc.
  - Puedes visualizarlas en Grafana

### Instalar Telegraf (Docker)

Si quieres habilitar métricas:

```bash
docker run -d \
  --name telegraf \
  --restart always \
  -p 8126:8126/udp \
  -v $PWD/telegraf-siscom-addon.conf:/etc/telegraf/telegraf.conf:ro \
  telegraf
```

Luego cambia `STATSD_ENABLED=true` en tu `.env`.

## Ejemplo Completo

Crea un archivo `.env` en la raíz del proyecto con este contenido:

```env
# Aplicación
APP_NAME=siscom-api
APP_VERSION=0.1.0

# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=mi_usuario
DB_PASSWORD=mi_password_seguro
DB_DATABASE=siscom_db
DB_MIN_CONNECTIONS=10
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT_SECS=30
DB_IDLE_TIMEOUT_SECS=300

# JWT
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=*

# StatsD (Deshabilitar por ahora)
STATSD_ENABLED=false
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api

# MQTT
BROKER_HOST=34.237.30.30:1883
BROKER_TOPIC=tracking/data
MQTT_USERNAME=administrator
MQTT_PASSWORD=tu_password_mqtt
```

## Valores por Defecto

Si no especificas alguna variable en `.env`, se usarán estos valores por defecto:

| Variable                      | Valor por Defecto |
| ----------------------------- | ----------------- |
| `STATSD_ENABLED`              | `false`           |
| `STATSD_HOST`                 | `localhost`       |
| `STATSD_PORT`                 | `8126`            |
| `STATSD_PREFIX`               | `siscom_api`      |
| `BROKER_HOST`                 | `localhost:1883`  |
| `BROKER_TOPIC`                | `#`               |
| `ALLOWED_ORIGINS`             | `*`               |
| `JWT_ALGORITHM`               | `HS256`           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`              |

## Seguridad

🔒 **NUNCA subas tu archivo `.env` a Git**

Asegúrate de que `.env` esté en tu `.gitignore`:

```bash
echo ".env" >> .gitignore
```
