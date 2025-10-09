# 📚 Documentación de SISCOM API

Bienvenido a la documentación completa de SISCOM API. Esta carpeta contiene toda la documentación técnica y guías del proyecto.

## 📖 Índice General

👉 **[DOCS_INDEX.md](DOCS_INDEX.md)** - Índice completo con navegación por temas y casos de uso

---

## 🚀 Inicio Rápido

### Para Desarrolladores
1. [Instalación y Setup](../README.md) - Configuración inicial del proyecto
2. [Guía de Migración](MIGRATION_REST.md) - Entiende los endpoints REST v1 en 5 minutos
3. [Ejemplos de Código](POSTMAN_EXAMPLES.md) - Ejemplos prácticos en varios lenguajes
4. [API REST Guide](API_REST_GUIDE.md) - Documentación completa de endpoints

### Para DevOps
1. [Despliegue en EC2](DEPLOYMENT.md) - Guía completa de deployment con GitHub Actions
2. [Variables de GitHub](GITHUB_VARIABLES.md) - Configuración de secrets y variables
3. [Agregar a Telegraf Existente](AGREGAR_A_TELEGRAF.md) - ⭐ Si ya tienes Telegraf configurado
4. [Métricas - Inicio Rápido](QUICKSTART_METRICS.md) - Configurar métricas en 5 minutos
5. [Métricas - Documentación](METRICS.md) - Sistema completo de métricas StatsD

---

## 📋 Documentos Disponibles

### API y Endpoints
- **[API_REST_GUIDE.md](API_REST_GUIDE.md)** - Guía completa de endpoints REST v1
- **[MIGRATION_REST.md](MIGRATION_REST.md)** - Guía de migración desde versión anterior
- **[POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md)** - Ejemplos con cURL, Postman, JavaScript, Svelte

### Configuración y Despliegue
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Despliegue en EC2 con GitHub Actions
- **[GITHUB_VARIABLES.md](GITHUB_VARIABLES.md)** - Configuración de variables de entorno en GitHub

### Métricas y Monitoreo
- **[QUICKSTART_METRICS.md](QUICKSTART_METRICS.md)** - Guía rápida de configuración (5 minutos)
- **[METRICS.md](METRICS.md)** - Documentación completa del sistema de métricas
- **[CHANGELOG_METRICS.md](CHANGELOG_METRICS.md)** - Historial de cambios en métricas

### Testing
- **[TESTS_GENERADOS.md](TESTS_GENERADOS.md)** - Documentación de tests generados
- **[../test/README.md](../test/README.md)** - Guía de ejecución de tests

### Desarrollo
- **[MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md)** - Mejoras futuras y pendientes
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios del proyecto

### Referencia
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Índice completo organizado por temas

---

## 🎯 Casos de Uso Rápidos

### "Necesito probar la API ahora mismo"
```bash
# 1. Lee esto
📄 MIGRATION_REST.md (5 minutos)

# 2. Importa esto
📦 ../SISCOM-API-v1.postman_collection.json

# 3. ¡Listo para probar!
```

### "Necesito integrar en mi frontend"
```bash
# 1. Entiende los endpoints
📄 MIGRATION_REST.md

# 2. Copia código de ejemplo
📄 POSTMAN_EXAMPLES.md

# 3. Referencia completa
📄 API_REST_GUIDE.md
```

### "Necesito deployar a producción"
```bash
# 1. Configura el deployment
📄 DEPLOYMENT.md

# 2. Configura variables
📄 GITHUB_VARIABLES.md

# 3. Configura métricas
📄 QUICKSTART_METRICS.md

# 4. Push a master
git push origin master
```

### "Necesito configurar métricas"
```bash
# 1. Guía rápida
📄 QUICKSTART_METRICS.md (5 minutos)

# 2. Documentación completa
📄 METRICS.md

# 3. Variables de GitHub
📄 GITHUB_VARIABLES.md
```

---

## 🔍 Buscar Información

### Por Tema
- **REST v1**: [API_REST_GUIDE.md](API_REST_GUIDE.md), [MIGRATION_REST.md](MIGRATION_REST.md)
- **JWT/Auth**: [API_REST_GUIDE.md](API_REST_GUIDE.md#autenticación)
- **SSE/Streaming**: [API_REST_GUIDE.md](API_REST_GUIDE.md#endpoints-de-server-sent-events-sse---tiempo-real)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md), [GITHUB_VARIABLES.md](GITHUB_VARIABLES.md)
- **Métricas**: [METRICS.md](METRICS.md), [QUICKSTART_METRICS.md](QUICKSTART_METRICS.md)
- **Testing**: [TESTS_GENERADOS.md](TESTS_GENERADOS.md)

### Por Lenguaje/Framework
- **cURL**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#ejemplos-con-curl)
- **JavaScript/TS**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-javascripttypescript-frontend)
- **Python**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-python)
- **Svelte**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md#en-svelte-frontend-completo)

---

## 📊 Métricas Disponibles

El sistema envía automáticamente estas métricas a Telegraf/InfluxDB:

1. **Peticiones por minuto** - `siscom_api.requests`
2. **Latencia del endpoint /stream** - `siscom_api.latency.stream`
3. **Conexiones SSE activas** - `siscom_api.sse.active_connections`

Ver [METRICS.md](METRICS.md) para detalles completos.

---

## 🆘 Ayuda

1. **Busca en**: [DOCS_INDEX.md](DOCS_INDEX.md) - Organizado por temas
2. **Swagger UI**: http://localhost:8000/api/docs - Documentación interactiva
3. **Ejemplos**: [POSTMAN_EXAMPLES.md](POSTMAN_EXAMPLES.md) - Código listo para usar
4. **Troubleshooting**: [METRICS.md](METRICS.md#troubleshooting) - Solución de problemas

---

## 📝 Contribuir

Para contribuir a la documentación:

1. Lee [MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md)
2. Revisa [CHANGELOG.md](CHANGELOG.md) para contexto
3. Actualiza [DOCS_INDEX.md](DOCS_INDEX.md) si agregas documentos nuevos

---

**Volver al**: [README principal](../README.md)

**Última actualización**: Octubre 2024  
**Versión de la API**: v1.0.0

