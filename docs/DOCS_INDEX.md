# 📚 Índice de Documentación - SISCOM API

## 🚀 Inicio Rápido

¿Primera vez usando la API? Empieza aquí:

1. **[README.md](../README.md)** - Descripción general del proyecto e instalación
2. **[MIGRATION_REST.md](MIGRATION_REST.md)** - Guía rápida de los cambios REST v1 (5 minutos)
3. **[Swagger UI](http://localhost:8000/api/docs)** - Documentación interactiva (requiere servidor corriendo)

---

## 📖 Documentación por Tema

### 🔌 API y Endpoints

| Documento | Descripción | Cuándo Leer |
|-----------|-------------|-------------|
| [API_REST_GUIDE.md](API_REST_GUIDE.md) | Guía completa de todos los endpoints REST v1 | Para entender todos los endpoints en detalle |
| [MIGRATION_REST.md](MIGRATION_REST.md) | Guía de migración desde endpoints antiguos | Si vienes de la versión anterior (POST) |
| [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md) | Ejemplos con cURL, Postman, JavaScript, Svelte | Para integrar en tu aplicación |

### 🔧 Configuración y Despliegue

| Documento | Descripción | Cuándo Leer |
|-----------|-------------|-------------|
| [README.md](../README.md) | Instalación local y configuración inicial | Al comenzar el proyecto |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Despliegue en EC2 con GitHub Actions | Para producción |
| [GITHUB_VARIABLES.md](GITHUB_VARIABLES.md) | Configuración de variables en GitHub | Para configurar CI/CD |

### 📊 Métricas y Monitoreo

| Documento | Descripción | Cuándo Leer |
|-----------|-------------|-------------|
| [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md) | Guía rápida de configuración de métricas | Para configurar métricas en 5 minutos |
| [METRICS.md](METRICS.md) | Documentación completa de métricas StatsD | Para entender el sistema de métricas |
| [GRAFANA_QUERIES.md](GRAFANA_QUERIES.md) | **Queries y dashboards para Grafana** | **Para crear visualizaciones y dashboards** ⭐ |
| [DEBUG_METRICS.md](DEBUG_METRICS.md) | Debugging de métricas y peticiones | Para investigar incrementos inesperados |
| [BUG_FIX_METRICS.md](BUG_FIX_METRICS.md) | Bug fix de aio-statsd await | Para entender el bug de await corregido |
| [CHANGELOG_METRICS.md](CHANGELOG_METRICS.md) | Cambios en la implementación de métricas | Para ver qué se implementó |
| [AGREGAR_A_TELEGRAF.md](AGREGAR_A_TELEGRAF.md) | Cómo agregar siscom-api a Telegraf existente | Para integrar con tu Telegraf actual |

### 🧪 Testing

| Documento | Descripción | Cuándo Leer |
|-----------|-------------|-------------|
| [TESTS_GENERADOS.md](TESTS_GENERADOS.md) | Documentación de tests generados | Para entender la suite de tests |
| [test/README.md](../test/README.md) | Guía de ejecución de tests | Para ejecutar y mantener tests |

### 📝 Desarrollo y Mejoras

| Documento | Descripción | Cuándo Leer |
|-----------|-------------|-------------|
| [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md) | Lista de mejoras futuras y pendientes | Para planificar desarrollo |
| [CHANGELOG.md](CHANGELOG.md) | Historial de cambios y versiones | Para ver qué ha cambiado |

---

## 📋 Tabla de Endpoints REST v1

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `GET /health` | GET | ❌ No | Health check del servidor |
| `GET /api/v1/communications` | GET | ✅ JWT | Histórico de múltiples dispositivos |
| `GET /api/v1/communications/stream` | GET | ❌ No | Stream SSE de múltiples dispositivos |
| `GET /api/v1/devices/{device_id}/communications` | GET | ✅ JWT | Histórico de un solo dispositivo |
| `GET /api/v1/devices/{device_id}/communications/stream` | GET | ❌ No | Stream SSE de un solo dispositivo |

**Ver [API_REST_GUIDE.md](API_REST_GUIDE.md) para detalles completos**

---

## 🎯 Guías por Caso de Uso

### "Quiero probar la API rápidamente"
1. Lee [MIGRATION_REST.md](MIGRATION_REST.md) (5 minutos)
2. Importa `SISCOM-API-v1.postman_collection.json` en Postman
3. Configura tu token JWT
4. Empieza a probar

### "Necesito integrar en mi frontend (Svelte)"
1. Lee [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md)
2. Ve a la sección "En Svelte"
3. Copia los componentes de ejemplo
4. Adapta a tu necesidad

### "Quiero entender todos los endpoints"
1. Lee [API_REST_GUIDE.md](API_REST_GUIDE.md) completo
2. Abre [Swagger UI](http://localhost:8000/api/docs)
3. Prueba cada endpoint con "Try it out"

### "Vengo de la versión anterior (POST)"
1. Lee [MIGRATION_REST.md](MIGRATION_REST.md)
2. Ve a la sección "Comparación Rápida"
3. Actualiza tu código según los ejemplos

### "Quiero desplegar en producción"
1. Lee [DEPLOYMENT.md](DEPLOYMENT.md)
2. Configura secrets en GitHub
3. Haz push a master para auto-deploy

### "Quiero contribuir o mejorar"
1. Lee [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md)
2. Revisa items pendientes
3. Lee [CHANGELOG.md](CHANGELOG.md) para contexto

---

## 🔍 Búsqueda Rápida

### Conceptos Clave

- **REST v1**: [API_REST_GUIDE.md](API_REST_GUIDE.md), [MIGRATION_REST.md](MIGRATION_REST.md)
- **JWT**: [README.md](../README.md#seguridad), [API_REST_GUIDE.md](API_REST_GUIDE.md#autenticación)
- **SSE (Server-Sent Events)**: [API_REST_GUIDE.md](API_REST_GUIDE.md#endpoints-de-server-sent-events-sse---tiempo-real)
- **Pydantic Schemas**: [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md#3-esquemas-pydantic)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Docker**: [README.md](../README.md#docker)
- **Métricas**: [METRICS.md](METRICS.md), [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md)

### Ejemplos de Código

- **cURL**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#ejemplos-con-curl)
- **JavaScript**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-javascripttypescript-frontend)
- **Python**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-python)
- **Svelte**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-svelte-frontend-completo)
- **Postman**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-postman)

### Solución de Problemas

- **Error 401**: [API_REST_GUIDE.md](API_REST_GUIDE.md#error-401-token-inválido)
- **Error 422**: [API_REST_GUIDE.md](API_REST_GUIDE.md#error-422-query-parameter-requerido)
- **Migración**: [MIGRATION_REST.md](MIGRATION_REST.md#breaking-changes)
- **Métricas**: [METRICS.md](METRICS.md#troubleshooting)
- **Métricas Inesperadas**: [DEBUG_METRICS.md](DEBUG_METRICS.md) ⭐
- **Troubleshooting**: [README.md](../README.md) sección final

---

## 📦 Archivos Adicionales

### Colecciones y Configuración

- **`SISCOM-API-v1.postman_collection.json`** - Colección de Postman lista para importar
- **`pyproject.toml`** - Configuración de Python y linters
- **`requirements.txt`** - Dependencias de Python
- **`docker-compose.yml`** - Configuración de Docker

### Código Fuente Principal

```
app/
├── api/
│   └── routes/
│       └── communications.py  ← Todos los endpoints REST v1
├── core/
│   ├── config.py              ← Configuración
│   ├── database.py            ← Conexión a DB
│   └── security.py            ← JWT validation
├── models/
│   └── communications.py      ← Modelos SQLAlchemy
├── schemas/
│   └── communications.py      ← Schemas Pydantic
├── services/
│   └── repository.py          ← Lógica de negocio
└── main.py                    ← Aplicación principal
```

---

## 🆘 ¿Necesitas Ayuda?

### 1. Revisa la documentación relevante arriba
### 2. Abre [Swagger UI](http://localhost:8000/api/docs) para ver ejemplos interactivos
### 3. Revisa [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md) para ejemplos de código
### 4. Consulta [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md) para features conocidas

---

## 🎓 Orden Recomendado de Lectura

### Para Desarrolladores Nuevos
1. [README.md](../README.md) - Instalación y setup
2. [MIGRATION_REST.md](MIGRATION_REST.md) - Entender endpoints REST v1
3. [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md) - Ejemplos prácticos
4. [API_REST_GUIDE.md](API_REST_GUIDE.md) - Documentación completa

### Para DevOps
1. [README.md](../README.md) - Arquitectura general
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Proceso de deployment
3. [GITHUB_VARIABLES.md](GITHUB_VARIABLES.md) - Configuración de variables
4. [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md) - Configuración de métricas
5. [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md) - Mejoras de infraestructura

### Para Frontend Developers
1. [MIGRATION_REST.md](MIGRATION_REST.md) - Entender endpoints
2. [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md) - Ejemplos de integración
3. [API_REST_GUIDE.md](API_REST_GUIDE.md) - Referencia completa

---

**Última actualización:** 2024-10-07  
**Versión de la API:** v1.0.0

