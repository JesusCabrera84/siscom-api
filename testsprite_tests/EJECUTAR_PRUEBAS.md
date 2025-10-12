# 🚀 Guía Rápida: Ejecutar Pruebas con TestSprite

## ⚡ Inicio Rápido (3 Comandos)

```bash
# 1. Instalar dependencias
pip3 install -r requirements.txt

# 2. Iniciar servidor (en una terminal)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Ejecutar TestSprite (en otra terminal)
cd /home/chch/Code/siscom-api && \
node /home/chch/.npm/_npx/8ddf6bea01b2519d/node_modules/@testsprite/testsprite-mcp/dist/index.js generateCodeAndExecute
```

---

## 📋 Pre-requisitos

### 1. PostgreSQL corriendo

Opción A - Docker (Recomendado):

```bash
docker run -d --name siscom-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=siscom \
  -p 5432:5432 \
  postgres:15-alpine
```

Opción B - PostgreSQL local:

```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE siscom;"
```

### 2. Archivo .env configurado

Ya existe en `/home/chch/Code/siscom-api/.env` con:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=siscom
JWT_SECRET_KEY=test_secret_key_for_testing_only_not_for_production
ALLOWED_ORIGINS=*
```

---

## 🔧 Instalación de Dependencias

```bash
cd /home/chch/Code/siscom-api

# Opción 1: Con pip
pip3 install -r requirements.txt

# Opción 2: Con Make
make install

# Opción 3: Con entorno virtual (recomendado para desarrollo)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🌐 Iniciar el Servidor

### Modo Desarrollo (con auto-reload)

```bash
cd /home/chch/Code/siscom-api
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O con Make:

```bash
make dev
```

### Modo Producción

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

O con Make:

```bash
make run
```

---

## ✅ Verificar que el Servidor está Corriendo

```bash
# Verificar health check
curl http://localhost:8000/health

# Debería retornar:
# {"status":"healthy","service":"siscom-api","version":"0.1.0"}
```

```bash
# Verificar documentación
curl http://localhost:8000/api/docs
```

Abre en tu navegador:

- <http://localhost:8000/api/docs> (Swagger UI)
- <http://localhost:8000/api/redoc> (ReDoc)

---

## 🧪 Ejecutar Pruebas con TestSprite

### Todas las Pruebas (10 casos de prueba)

```bash
cd /home/chch/Code/siscom-api
node /home/chch/.npm/_npx/8ddf6bea01b2519d/node_modules/@testsprite/testsprite-mcp/dist/index.js generateCodeAndExecute
```

### Pruebas Específicas

Para ejecutar solo casos de prueba específicos, edita los IDs:

```bash
# Solo health check (TC001)
# Modificar el comando para incluir: --testIds TC001

# Múltiples casos específicos
# --testIds TC001,TC002,TC006
```

---

## 📊 Ver Reportes Generados

Después de ejecutar TestSprite, los reportes se generan en:

```
/home/chch/Code/siscom-api/testsprite_tests/
├── testsprite-mcp-test-report.md    # Reporte final de pruebas
├── tmp/
│   └── raw_report.md                 # Reporte crudo
└── REPORTE_ANALISIS_TESTSPRITE.md   # Este análisis completo
```

Ver reporte:

```bash
cat /home/chch/Code/siscom-api/testsprite_tests/testsprite-mcp-test-report.md
```

O abrirlo en editor:

```bash
code /home/chch/Code/siscom-api/testsprite_tests/testsprite-mcp-test-report.md
```

---

## 🐛 Troubleshooting

### Error: "No module named uvicorn"

```bash
pip3 install uvicorn
# O reinstalar todas las dependencias
pip3 install -r requirements.txt
```

### Error: "connection to server failed"

PostgreSQL no está corriendo o configuración incorrecta en .env

```bash
# Verificar PostgreSQL
docker ps | grep postgres
# O
sudo systemctl status postgresql

# Verificar .env
cat .env | grep DB_
```

### Error: "port 8000 already in use"

```bash
# Encontrar y matar el proceso
sudo lsof -i :8000
sudo kill -9 <PID>

# O usar otro puerto
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Error: "Failed to set up testing tunnel"

El servidor no está corriendo en puerto 8000. Verificar:

```bash
curl http://localhost:8000/health
```

Si no responde, reiniciar el servidor.

---

## 🧹 Limpiar y Reiniciar

### Detener Servidor

```bash
# Encontrar proceso
ps aux | grep uvicorn

# Matar proceso
sudo kill -9 <PID>

# O con Ctrl+C en la terminal donde corre
```

### Limpiar PostgreSQL Docker

```bash
docker stop siscom-postgres
docker rm siscom-postgres
```

### Reiniciar Todo

```bash
# 1. Detener todo
docker stop siscom-postgres
killall python3

# 2. Limpiar
docker rm siscom-postgres

# 3. Reiniciar PostgreSQL
docker run -d --name siscom-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=siscom \
  -p 5432:5432 \
  postgres:15-alpine

# 4. Esperar 5 segundos
sleep 5

# 5. Reiniciar servidor
cd /home/chch/Code/siscom-api
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Pruebas Manuales Rápidas

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Documentación OpenAPI

```bash
curl http://localhost:8000/api/openapi.json | jq
```

### 3. SSE Stream (Ctrl+C para detener)

```bash
curl -N -H "Accept: text/event-stream" \
  "http://localhost:8000/api/v1/communications/stream?device_ids=867564050638581"
```

### 4. Endpoint Protegido (Sin JWT - debería fallar con 401)

```bash
curl -i "http://localhost:8000/api/v1/communications?device_ids=867564050638581"
```

---

## 🎯 Checklist Pre-Ejecución

Antes de ejecutar TestSprite, verifica:

- [ ] PostgreSQL corriendo (puerto 5432)
- [ ] Dependencias instaladas (`pip3 install -r requirements.txt`)
- [ ] Archivo `.env` configurado correctamente
- [ ] Servidor FastAPI corriendo (puerto 8000)
- [ ] Health check responde (`curl http://localhost:8000/health`)
- [ ] Documentación accesible (<http://localhost:8000/api/docs>)

---

## 📞 Comandos Útiles

```bash
# Ver logs del servidor (si corre en background)
tail -f /var/log/siscom-api.log

# Verificar puerto 8000
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# Verificar puerto 5432 (PostgreSQL)
sudo lsof -i :5432
sudo netstat -tulpn | grep 5432

# Verificar proceso de Python
ps aux | grep uvicorn
ps aux | grep python

# Verificar containers Docker
docker ps
docker logs siscom-postgres
```

---

## 🚀 Script All-in-One

Crea un script para automatizar todo:

```bash
cat > /home/chch/Code/siscom-api/run_tests.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Iniciando pruebas SISCOM API con TestSprite..."

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Verificar PostgreSQL
echo -e "${GREEN}1. Verificando PostgreSQL...${NC}"
if ! docker ps | grep -q siscom-postgres; then
    echo "Iniciando PostgreSQL..."
    docker run -d --name siscom-postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=siscom \
      -p 5432:5432 \
      postgres:15-alpine
    sleep 5
fi

# 2. Instalar dependencias
echo -e "${GREEN}2. Instalando dependencias...${NC}"
pip3 install -q -r requirements.txt

# 3. Iniciar servidor
echo -e "${GREEN}3. Iniciando servidor FastAPI...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 5

# 4. Verificar health check
echo -e "${GREEN}4. Verificando health check...${NC}"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Servidor corriendo correctamente${NC}"
else
    echo -e "${RED}❌ Servidor no responde${NC}"
    kill $SERVER_PID
    exit 1
fi

# 5. Ejecutar TestSprite
echo -e "${GREEN}5. Ejecutando TestSprite...${NC}"
node /home/chch/.npm/_npx/8ddf6bea01b2519d/node_modules/@testsprite/testsprite-mcp/dist/index.js generateCodeAndExecute

# 6. Detener servidor
echo -e "${GREEN}6. Limpiando...${NC}"
kill $SERVER_PID

echo -e "${GREEN}✅ ¡Pruebas completadas!${NC}"
echo "Ver reporte en: testsprite_tests/testsprite-mcp-test-report.md"
EOF

chmod +x /home/chch/Code/siscom-api/run_tests.sh
```

Luego ejecutar:

```bash
cd /home/chch/Code/siscom-api
./run_tests.sh
```

---

**Última actualización**: 7 de octubre de 2025
