# Configuración de Variables de GitHub para Deploy

Este documento describe cómo configurar las variables de entorno necesarias en GitHub para el despliegue automático de siscom-api.

## 📋 Variables Requeridas

### Secrets (Valores Sensibles)

Ve a: **Settings → Secrets and variables → Actions → Secrets**

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EC2_HOST` | IP o hostname de tu servidor EC2 | `34.xxx.xxx.xxx` |
| `EC2_USERNAME` | Usuario SSH en EC2 | `ubuntu` o `ec2-user` |
| `EC2_SSH_KEY` | Llave privada SSH completa | `-----BEGIN RSA PRIVATE KEY-----...` |
| `EC2_SSH_PORT` | Puerto SSH (opcional, default: 22) | `22` |
| `DB_PASSWORD` | Contraseña de la base de datos | `tu_password_seguro` |
| `JWT_SECRET_KEY` | Llave secreta para JWT | `tu_secret_key_super_seguro_aqui` |

### Variables (Valores No Sensibles)

Ve a: **Settings → Secrets and variables → Actions → Variables**

#### Base de Datos

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_USERNAME` | Usuario de PostgreSQL | `postgres` |
| `DB_DATABASE` | Nombre de la base de datos | `siscom` |
| `DB_MIN_CONNECTIONS` | Mínimo de conexiones en el pool | `10` |
| `DB_MAX_CONNECTIONS` | Máximo de conexiones en el pool | `20` |
| `DB_CONNECTION_TIMEOUT_SECS` | Timeout de conexión en segundos | `30` |
| `DB_IDLE_TIMEOUT_SECS` | Timeout de inactividad en segundos | `300` |

#### Métricas StatsD/Telegraf

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `STATSD_HOST` | Host donde corre Telegraf | `localhost` |
| `STATSD_PORT` | Puerto UDP de StatsD | `8126` |
| `STATSD_PREFIX` | Prefijo para las métricas | `siscom_api` |

## 🔧 Configuración en GitHub

### 1. Configurar Secrets

```bash
# En tu repositorio de GitHub:
Settings → Secrets and variables → Actions → Secrets → New repository secret
```

Agrega cada uno de los secrets mencionados arriba.

**Importante para `EC2_SSH_KEY`:**

```bash
# Copia el contenido completo de tu llave privada:
cat ~/.ssh/tu_llave_privada.pem

# Pega todo el contenido en GitHub, incluyendo las líneas:
# -----BEGIN RSA PRIVATE KEY-----
# ... contenido ...
# -----END RSA PRIVATE KEY-----
```

### 2. Configurar Variables

```bash
# En tu repositorio de GitHub:
Settings → Secrets and variables → Actions → Variables → New repository variable
```

Agrega cada una de las variables mencionadas arriba.

#### Variables de StatsD según tu configuración:

**Si Telegraf está en el mismo host que la API:**

```bash
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api
```

**Si Telegraf está en un container Docker:**

```bash
# Si usas docker-compose con ambos servicios:
STATSD_HOST=telegraf

# Si están en containers separados pero mismo host:
STATSD_HOST=172.17.0.1  # IP del gateway de Docker

# Si usas network_mode: host:
STATSD_HOST=localhost
```

**Si Telegraf está en otro servidor:**

```bash
STATSD_HOST=ip.del.servidor.telegraf
STATSD_PORT=8126
STATSD_PREFIX=siscom_api
```

## 📝 Ejemplo Completo

### Secrets

```plaintext
EC2_HOST = 34.234.56.78
EC2_USERNAME = ubuntu
EC2_SSH_KEY = -----BEGIN RSA PRIVATE KEY-----
              MIIEpAIBAAKCAQEA...
              ...
              -----END RSA PRIVATE KEY-----
EC2_SSH_PORT = 22
DB_PASSWORD = MySecurePassword123!
JWT_SECRET_KEY = super-secret-key-change-in-production-xyz123
```

### Variables

```plaintext
# Base de Datos
DB_HOST = 10.0.1.50
DB_PORT = 5432
DB_USERNAME = siscom_user
DB_DATABASE = siscom_prod
DB_MIN_CONNECTIONS = 10
DB_MAX_CONNECTIONS = 20
DB_CONNECTION_TIMEOUT_SECS = 30
DB_IDLE_TIMEOUT_SECS = 300

# Métricas
STATSD_HOST = localhost
STATSD_PORT = 8126
STATSD_PREFIX = siscom_api
```

## ✅ Verificar Configuración

Después de configurar las variables:

1. **Verifica que todas estén presentes:**
   - Ve a Settings → Secrets and variables → Actions
   - Revisa que todos los secrets y variables estén listados

2. **Prueba el deploy:**

   ```bash
   # Haz un push a master o ejecuta el workflow manualmente
   git push origin master
   
   # O desde GitHub:
   Actions → Deploy to EC2 → Run workflow
   ```

3. **Verifica en los logs:**
   - Ve a Actions → Selecciona el workflow
   - Revisa que el archivo .env se crea correctamente
   - No deberías ver errores de variables faltantes

## 🔍 Troubleshooting

### Error: "variable not set"

Si ves un error como `STATSD_HOST: variable not set`:

1. Verifica que la variable existe en GitHub (Settings → Secrets and variables → Actions → Variables)
2. Verifica que el nombre está escrito correctamente (es case-sensitive)
3. Verifica que está en la lista de `envs` en `.github/workflows/deploy.yml`

### Las métricas no funcionan después del deploy

1. Verifica que las variables se pasaron correctamente:

   ```bash
   # Conéctate a tu EC2
   ssh ubuntu@tu-ec2-host
   
   # Ve al directorio del proyecto
   cd ~/siscom-api
   
   # Verifica el .env
   cat .env | grep STATSD
   ```

2. Verifica que Telegraf puede recibir en ese host/puerto:

   ```bash
   # Desde el container de la API
   docker exec -it siscom-api bash
   nc -u -v -z $STATSD_HOST $STATSD_PORT
   ```

3. Verifica los logs de la API:

   ```bash
   docker logs siscom-api
   ```

## 📚 Recursos

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Variables](https://docs.github.com/en/actions/learn-github-actions/variables)
- [METRICS.md](METRICS.md) - Documentación de métricas
- [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md) - Guía rápida de configuración

## 🔐 Seguridad

- ✅ **NUNCA** comitees valores de secrets en el código
- ✅ Usa variables de GitHub para valores sensibles
- ✅ Las variables normales (no secrets) son visibles en los logs
- ✅ Los secrets se ofuscan en los logs de GitHub Actions
- ✅ Rota las llaves SSH y secrets periódicamente
