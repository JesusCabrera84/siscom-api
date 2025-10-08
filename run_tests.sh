#!/bin/bash
set -e

echo "🚀 Iniciando pruebas SISCOM API con TestSprite..."

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Verificar PostgreSQL
echo -e "${GREEN}1. Verificando PostgreSQL...${NC}"
if ! docker ps | grep -q siscom-postgres; then
    echo "Iniciando PostgreSQL..."
    docker run -d --name siscom-postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=siscom \
      -p 5432:5432 \
      postgres:15-alpine 2>/dev/null || {
        echo -e "${YELLOW}PostgreSQL ya existe, iniciando...${NC}"
        docker start siscom-postgres 2>/dev/null || true
    }
    sleep 5
fi

# 2. Instalar dependencias
echo -e "${GREEN}2. Verificando dependencias...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Instalando dependencias..."
    pip3 install -q -r requirements.txt
else
    echo "Dependencias ya instaladas ✓"
fi

# 3. Iniciar servidor
echo -e "${GREEN}3. Iniciando servidor FastAPI en puerto 8000...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
echo "PID del servidor: $SERVER_PID"
sleep 5

# 4. Verificar health check
echo -e "${GREEN}4. Verificando health check...${NC}"
RETRIES=5
for i in $(seq 1 $RETRIES); do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✅ Servidor corriendo correctamente${NC}"
        break
    else
        if [ $i -eq $RETRIES ]; then
            echo -e "${RED}❌ Servidor no responde después de $RETRIES intentos${NC}"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi
        echo "Intento $i/$RETRIES - Esperando..."
        sleep 2
    fi
done

# 5. Ejecutar TestSprite
echo -e "${GREEN}5. Ejecutando TestSprite (esto puede tomar unos minutos)...${NC}"
node /home/chch/.npm/_npx/8ddf6bea01b2519d/node_modules/@testsprite/testsprite-mcp/dist/index.js generateCodeAndExecute

# 6. Detener servidor
echo -e "${GREEN}6. Limpiando...${NC}"
kill $SERVER_PID 2>/dev/null || true
sleep 2

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ¡Pruebas completadas exitosamente!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Reportes generados:"
echo "  - testsprite_tests/testsprite-mcp-test-report.md"
echo "  - testsprite_tests/tmp/raw_report.md"
echo ""
echo "📋 Documentación:"
echo "  - testsprite_tests/REPORTE_ANALISIS_TESTSPRITE.md"
echo "  - testsprite_tests/EJECUTAR_PRUEBAS.md"
echo ""
echo "Ver reporte principal:"
echo "  cat testsprite_tests/testsprite-mcp-test-report.md"
echo ""

