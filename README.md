# SISCOM API

API FastAPI para gestión de comunicaciones de dispositivos GPS (Suntech y Queclink).

## 🚀 Características

- ✅ FastAPI con async/await
- ✅ PostgreSQL con SQLAlchemy async
- ✅ Autenticación JWT
- ✅ Server-Sent Events (SSE) para streaming
- ✅ Integración MQTT con Mosquitto para eventos en tiempo real
- ✅ Pool de conexiones optimizado
- ✅ Health checks
- ✅ CORS configurable
- ✅ Docker y Docker Compose
- ✅ CI/CD con GitHub Actions
- ✅ Métricas StatsD con aio-statsd para Telegraf/InfluxDB

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 12+
- Docker y Docker Compose (para deployment)

## 🛠️ Instalación Local

### Opción A: Con script de setup (recomendado)

```bash
git clone https://github.com/tu-usuario/siscom-api.git
cd siscom-api
./scripts/setup_dev.sh
```

### Opción B: Manual

#### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/siscom-api.git
cd siscom-api
```

#### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### 3. Instalar dependencias

```bash
# Dependencias básicas
pip install -r requirements.txt

# O con Make
make install
```

#### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=tu_password
DB_DATABASE=siscom
DB_MIN_CONNECTIONS=10
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT_SECS=30
DB_IDLE_TIMEOUT_SECS=300

JWT_SECRET_KEY=tu_secret_key_super_seguro
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

ALLOWED_ORIGINS=*

# Métricas StatsD (opcional)
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api

# MQTT Configuration
BROKER_HOST=localhost:1883
BROKER_TOPIC=#
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=mqtt_password
```

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:

- API: <http://localhost:8000>
- Documentación: <http://localhost:8000/api/docs>
- ReDoc: <http://localhost:8000/api/redoc>

## 🔧 Desarrollo y Calidad de Código

### Herramientas de Linting

Este proyecto usa herramientas modernas de linting y formateo para mantener la calidad del código:

#### Instalación de herramientas

```bash
pip install ruff black mypy
```

#### 🔍 Ruff - Linter ultrarrápido

Ruff es un linter de Python extremadamente rápido que reemplaza a flake8, isort, y más.

```bash
# Verificar código
ruff check app/

# Auto-corregir problemas
ruff check app/ --fix

# Verificar un archivo específico
ruff check app/main.py
```

#### 🎨 Black - Formateador de código

Black formatea automáticamente tu código siguiendo PEP 8.

```bash
# Verificar formato (sin modificar)
black --check app/

# Formatear código automáticamente
black app/

# Formatear un archivo específico
black app/main.py
```

#### 📝 MyPy - Verificador de tipos estáticos

MyPy verifica los tipos de datos en tu código Python.

```bash
# Verificar tipos
mypy app/ --ignore-missing-imports

# Verificar con más detalle
mypy app/ --strict
```

#### 🚀 Ejecutar todos los linters de una vez

```bash
# Opción 1: Manualmente
ruff check app/ && black --check app/ && mypy app/ --ignore-missing-imports

# Opción 2: Usando Makefile (recomendado)
make check-all      # Verificar todo
make fix-all        # Auto-corregir y formatear
```

#### 📦 Comandos útiles con Makefile

```bash
make help           # Ver todos los comandos disponibles
make install        # Instalar dependencias
make lint           # Ejecutar Ruff
make lint-fix       # Auto-corregir con Ruff
make format         # Formatear con Black
make format-check   # Verificar formato
make type-check     # Verificar tipos con MyPy
make test           # Ejecutar tests
make dev            # Ejecutar servidor en desarrollo
make docker-build   # Construir imagen Docker
make docker-up      # Levantar con Docker Compose
```

#### 💡 Configuración en tu editor

**VSCode** - Instala estas extensiones:

- Ruff (charliermarsh.ruff)
- Black Formatter (ms-python.black-formatter)
- Pylance para MyPy (ms-python.vscode-pylance)

Agrega a `.vscode/settings.json`:

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "ruff.enable": true
}
```

#### 🔄 Pre-commit hooks (Opcional)

Para ejecutar linters automáticamente antes de cada commit:

```bash
pip install pre-commit

# Crear archivo .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
EOF

# Instalar hooks
pre-commit install
```

### CI/CD

Los linters se ejecutan automáticamente en cada push a través de GitHub Actions. Si el código no pasa los linters, el deploy se detiene automáticamente.

## 🐳 Docker

### Construir imagen

```bash
docker build -t siscom-api:latest .
```

### Ejecutar con Docker Compose

```bash
docker network create siscom-network
docker compose up -d
```

## 📚 Documentación

### 📖 Documentación Principal

| Documento                                           | Descripción                                            |
| --------------------------------------------------- | ------------------------------------------------------ |
| **[📘 API REST Guide](docs/API_REST_GUIDE.md)**     | Documentación completa de todos los endpoints          |
| **[📮 Ejemplos de Uso](docs/POSTMAN_EXAMPLES.md)**  | Ejemplos con cURL, Postman, JavaScript, Python, Svelte |
| **[📊 Métricas](docs/METRICS.md)**                  | Sistema de métricas StatsD/Telegraf/InfluxDB           |
| **[📈 Queries Grafana](docs/GRAFANA_QUERIES.md)**   | Dashboards y queries para visualizar métricas          |
| **[🚀 Deployment](docs/DEPLOYMENT.md)**             | Guía de despliegue en EC2 con GitHub Actions           |
| **[🔌 MQTT Integration](docs/MQTT_INTEGRATION.md)** | Integración con Mosquitto para streaming en tiempo real |
| **[📖 Swagger UI](http://localhost:8000/api/docs)** | Documentación interactiva (servidor corriendo)         |

### Endpoints REST v1

#### Health Check

```http
GET /health
```

#### Comunicaciones - Múltiples Dispositivos

```http
GET /api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123
Authorization: Bearer {token}
```

#### Comunicaciones - Un Solo Dispositivo

```http
GET /api/v1/devices/{device_id}/communications
Authorization: Bearer {token}
```

#### Stream SSE - Eventos en Tiempo Real (MQTT)

Endpoint de streaming que consume mensajes de Mosquitto y los transmite vía Server-Sent Events:

```http
# Todos los dispositivos
GET /api/v1/stream
Accept: text/event-stream

# Filtrar por device_ids
GET /api/v1/stream?device_ids=0848086072,0848086073
Accept: text/event-stream
```

**Ejemplo con curl:**

```bash
curl -N "http://localhost:8000/api/v1/stream?device_ids=0848086072"
```

Ver [MQTT_INTEGRATION.md](docs/MQTT_INTEGRATION.md) para más detalles sobre la integración MQTT.

### Tabla de Endpoints

| Endpoint                                                | Método | Auth   | Descripción                          |
| ------------------------------------------------------- | ------ | ------ | ------------------------------------ |
| `GET /health`                                           | GET    | ❌ No  | Health check del servicio            |
| `GET /api/v1/communications`                            | GET    | ✅ JWT | Histórico de múltiples dispositivos  |
| `GET /api/v1/devices/{device_id}/communications`        | GET    | ✅ JWT | Histórico de un solo dispositivo     |
| `GET /api/v1/stream`                                    | GET    | ❌ No  | Stream SSE con mensajes MQTT         |
| `GET /api/v1/stream?device_ids={ids}`                   | GET    | ❌ No  | Stream SSE filtrado por dispositivos |

## 🏗️ Arquitectura

```plaintext
siscom-api/
├── app/
│   ├── api/
│   │   └── routes/          # Endpoints de la API
│   ├── core/
│   │   ├── config.py        # Configuración
│   │   ├── database.py      # Conexión a DB
│   │   ├── middleware.py    # Middleware de métricas
│   │   └── security.py      # JWT y autenticación
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── services/
│   │   ├── mqtt_client.py   # Cliente MQTT para Mosquitto
│   │   ├── repository.py    # Repositorio de datos
│   │   └── sse.py           # Lógica SSE (opcional)
│   ├── utils/
│   │   ├── exceptions.py    # Excepciones personalizadas
│   │   ├── logger.py        # Logging
│   │   └── metrics.py       # Cliente aio-statsd
│   └── main.py              # Aplicación principal
├── docs/                    # 📚 Documentación
│   ├── API_REST_GUIDE.md    # 📘 Guía completa del API
│   ├── POSTMAN_EXAMPLES.md  # 📮 Ejemplos de uso
│   ├── METRICS.md           # 📊 Sistema de métricas
│   ├── GRAFANA_QUERIES.md   # 📈 Queries y dashboards
│   ├── DEPLOYMENT.md        # 🚀 Guía de deployment
│   └── MQTT_INTEGRATION.md  # 🔌 Integración MQTT/Mosquitto
├── test/                    # Tests unitarios e integración
├── scripts/                 # Scripts de utilidad
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔐 Seguridad

- Autenticación JWT para endpoints protegidos
- Contenedor corre con usuario no privilegiado
- Secrets manejados con variables de entorno
- Pool de conexiones con límites configurados
- Health checks implementados

## 🚢 Despliegue

Ver documentación completa de despliegue en [DEPLOYMENT.md](docs/DEPLOYMENT.md):

- Instrucciones detalladas de despliegue en EC2 con GitHub Actions
- Configuración de variables de entorno en GitHub (incluye STATSD\_\*)
- Health checks y verificación de deployment

## 📊 Modelos de Datos

### CommunicationSuntech / CommunicationQueclink

Tablas separadas para cada fabricante, compartiendo la misma estructura base:

- `device_id`: Identificador del dispositivo
- `latitude`, `longitude`: Coordenadas GPS
- `speed`, `course`: Velocidad y dirección
- `gps_datetime`: Timestamp del GPS
- `main_battery_voltage`, `backup_battery_voltage`: Voltajes
- `odometer`, `trip_distance`, `total_distance`: Distancias
- Y más campos...

## 🧪 Testing

### Suite Completa de Tests con pytest

El proyecto incluye una suite completa de tests unitarios y de integración con más de 50 tests y ~95% de cobertura.

#### Ejecutar Tests

```bash
# Opción 1: Script interactivo (recomendado)
./run_unit_tests.sh

# Opción 2: pytest directo
pytest                    # Todos los tests
pytest -v                 # Verbose
pytest --cov=app          # Con cobertura

# Opción 3: Make commands
make test                 # Todos los tests
make test-unit            # Solo unitarios
make test-integration     # Solo integración
make test-cov             # Con cobertura HTML
make test-auth            # Solo autenticación
make test-fast            # Excluir tests lentos
```

#### Tests por Categoría

```bash
pytest -m unit            # Tests unitarios (rápidos)
pytest -m integration     # Tests de integración
pytest -m auth            # Tests de autenticación
pytest -m database        # Tests de base de datos
pytest -m "not slow"      # Excluir tests lentos
```

#### Tests Específicos

```bash
# Un archivo específico
pytest test/test_health.py

# Una clase específica
pytest test/test_security.py::TestJWTToken

# Un test específico
pytest test/test_health.py::TestHealthEndpoint::test_health_check_returns_200
```

#### Cobertura de Tests

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html

# Ver reporte en navegador
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
```

#### Estructura de Tests

- `test/test_health.py` - Tests del health check endpoint
- `test/test_security.py` - Tests de JWT y autenticación
- `test/test_communications.py` - Tests de endpoints de comunicaciones
- `test/test_repository.py` - Tests del servicio de repositorio
- `test/test_schemas.py` - Tests de schemas Pydantic
- `test/test_models.py` - Tests de modelos SQLAlchemy
- `test/test_config.py` - Tests de configuración
- `test/conftest.py` - Fixtures compartidas

Ver documentación completa en [test/README.md](test/README.md)

## 📊 Métricas y Monitoreo

La API envía métricas automáticamente a Telegraf usando el protocolo StatsD con **aio-statsd** (librería asíncrona optimizada para FastAPI).

### Métricas Disponibles

1. **Peticiones por minuto** (`siscom_api.requests`)
   - Contador de todas las peticiones HTTP
   - Tag: `app=siscom-api`

2. **Latencia del endpoint /stream** (`siscom_api.latency.stream`)
   - Tiempo de respuesta en milisegundos
   - Genera percentiles (p50, p90, p95, p99) y media
   - Tag: `app=siscom-api`

3. **Conexiones SSE activas** (`siscom_api.sse.active_connections`)
   - Número actual de conexiones Server-Sent Events
   - Tag: `app=siscom-api`

### Configuración

Agrega estas variables a tu `.env`:

```env
STATSD_HOST=localhost
STATSD_PORT=8126
STATSD_PREFIX=siscom_api
```

### Uso con Telegraf

1. Copia el archivo de configuración de ejemplo:

   ```bash
   cp telegraf-statsd.conf /path/to/telegraf/telegraf.conf
   ```

2. Configura las variables de InfluxDB en Telegraf

3. Inicia Telegraf:

   ```bash
   docker run -d --name telegraf \
     -p 8125:8125/udp \
     -v $(pwd)/telegraf-statsd.conf:/etc/telegraf/telegraf.conf:ro \
     telegraf:latest
   ```

4. Prueba las métricas:

   ```bash
   python test_metrics.py
   ```

### Ventajas de aio-statsd

- ✅ **Asíncrono:** Completamente integrado con FastAPI y asyncio
- ✅ **Sin bloqueo:** No afecta el rendimiento del event loop
- ✅ **Automático:** Conexión y desconexión manejadas en el lifecycle de la app
- ✅ **Tags nativos:** Formato InfluxDB optimizado
- ✅ **Robusto:** Maneja errores de red sin impactar la aplicación

Ver documentación completa en [METRICS.md](docs/METRICS.md)

## 📝 Mejoras Sugeridas

### Implementadas

- ✅ Pool de conexiones optimizado
- ✅ Health check endpoint
- ✅ CORS configurado
- ✅ Docker multi-stage build
- ✅ GitHub Actions CI/CD
- ✅ Variables de entorno bien estructuradas
- ✅ **Suite completa de tests con pytest (50+ tests, ~95% coverage)**
- ✅ **Métricas StatsD con aio-statsd para Telegraf/InfluxDB**
- ✅ **Integración MQTT con Mosquitto para streaming en tiempo real**

### Por Implementar

- ⚠️ Logging estructurado con Loguru (archivos utils vacíos)
- ⚠️ Manejo de excepciones personalizado
- ⚠️ Rate limiting
- ⚠️ Caché (Redis) para consultas frecuentes
- ⚠️ Documentación de esquemas con Pydantic
- ⚠️ Migraciones de base de datos (Alembic)
- ⚠️ Índices de base de datos optimizados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

[Tu licencia aquí]

## 👥 Autores

[Tu nombre/equipo aquí]

## 📞 Contacto

[Tu contacto aquí]
