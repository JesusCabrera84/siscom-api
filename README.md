# SISCOM API

API FastAPI para gestión de comunicaciones de dispositivos GPS (Suntech y Queclink).

## 🚀 Características

- ✅ FastAPI con async/await
- ✅ PostgreSQL con SQLAlchemy async
- ✅ Autenticación JWT
- ✅ Server-Sent Events (SSE) para streaming
- ✅ Pool de conexiones optimizado
- ✅ Health checks
- ✅ CORS configurable
- ✅ Docker y Docker Compose
- ✅ CI/CD con GitHub Actions

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

#### 1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/siscom-api.git
cd siscom-api
```

#### 2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### 3. Instalar dependencias:
```bash
# Dependencias básicas
pip install -r requirements.txt

# O con Make
make install
```

#### 4. Configurar variables de entorno:
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
```

### 5. Ejecutar la aplicación:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- API: http://localhost:8000
- Documentación: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🔧 Desarrollo y Calidad de Código

### Herramientas de Linting

Este proyecto usa herramientas modernas de linting y formateo para mantener la calidad del código:

#### Instalación de herramientas:
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

#### 🚀 Ejecutar todos los linters de una vez:
```bash
# Opción 1: Manualmente
ruff check app/ && black --check app/ && mypy app/ --ignore-missing-imports

# Opción 2: Usando Makefile (recomendado)
make check-all      # Verificar todo
make fix-all        # Auto-corregir y formatear
```

#### 📦 Comandos útiles con Makefile:
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

### Construir imagen:
```bash
docker build -t siscom-api:latest .
```

### Ejecutar con Docker Compose:
```bash
docker network create siscom-network
docker compose up -d
```

## 📚 Documentación de la API

### 🚀 Guías y Documentación

- **[📘 API REST Guide](API_REST_GUIDE.md)** - Documentación completa de todos los endpoints REST v1
- **[🔄 Migration Guide](MIGRATION_REST.md)** - Guía rápida de migración a REST v1
- **[📮 Postman Examples](POSTMAN_EXAMPLES.md)** - Ejemplos con cURL, Postman y JavaScript
- **[📖 Swagger UI](http://localhost:8000/api/docs)** - Documentación interactiva (cuando el servidor esté corriendo)

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

#### Stream SSE - Múltiples Dispositivos
```http
GET /api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123
Accept: text/event-stream
```

#### Stream SSE - Un Solo Dispositivo
```http
GET /api/v1/devices/{device_id}/communications/stream
Accept: text/event-stream
```

### Tabla de Endpoints

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `GET /api/v1/communications` | GET | ✅ JWT | Histórico de múltiples dispositivos |
| `GET /api/v1/communications/stream` | GET | ❌ No | Stream SSE de múltiples dispositivos |
| `GET /api/v1/devices/{device_id}/communications` | GET | ✅ JWT | Histórico de un solo dispositivo |
| `GET /api/v1/devices/{device_id}/communications/stream` | GET | ❌ No | Stream SSE de un solo dispositivo |

## 🏗️ Arquitectura

```
siscom-api/
├── app/
│   ├── api/
│   │   └── routes/          # Endpoints de la API
│   ├── core/
│   │   ├── config.py        # Configuración
│   │   ├── database.py      # Conexión a DB
│   │   └── security.py      # JWT y autenticación
│   ├── models/              # Modelos SQLAlchemy
│   ├── services/            # Lógica de negocio
│   ├── utils/               # Utilidades
│   └── main.py              # Aplicación principal
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

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas de despliegue en EC2 con GitHub Actions.

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

```bash
pytest
```

## 📝 Mejoras Sugeridas

### Implementadas:
- ✅ Pool de conexiones optimizado
- ✅ Health check endpoint
- ✅ CORS configurado
- ✅ Docker multi-stage build
- ✅ GitHub Actions CI/CD
- ✅ Variables de entorno bien estructuradas

### Por Implementar:
- ⚠️ Logging estructurado con Loguru (archivos utils vacíos)
- ⚠️ Manejo de excepciones personalizado
- ⚠️ Pruebas unitarias e integración
- ⚠️ Rate limiting
- ⚠️ Caché (Redis) para consultas frecuentes
- ⚠️ Métricas y monitoreo (Prometheus)
- ⚠️ Documentación de esquemas con Pydantic
- ⚠️ Migraciones de base de datos (Alembic)
- ⚠️ WebSockets o RabbitMQ para eventos en tiempo real
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

