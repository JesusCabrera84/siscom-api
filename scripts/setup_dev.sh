#!/bin/bash

# Script de configuración para desarrollo local
set -e

echo "🚀 Configurando ambiente de desarrollo para SISCOM API..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi
echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"

# Crear entorno virtual
echo -e "${YELLOW}Creando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✅ Entorno virtual ya existe${NC}"
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo -e "${YELLOW}Instalando dependencias...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Instalar herramientas de desarrollo
echo -e "${YELLOW}Instalando herramientas de desarrollo...${NC}"
pip install ruff black mypy pytest-cov ipython
echo -e "${GREEN}✅ Herramientas instaladas${NC}"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creando archivo .env de ejemplo...${NC}"
    cat > .env << EOF
# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=siscom
DB_MIN_CONNECTIONS=10
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT_SECS=30
DB_IDLE_TIMEOUT_SECS=300

# Seguridad JWT
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=*
EOF
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠️  Recuerda configurar las variables de entorno en .env${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# Crear directorio de logs
mkdir -p logs
echo -e "${GREEN}✅ Directorio de logs creado${NC}"

# Información final
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Configuración completada!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Para activar el entorno virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Para ejecutar la aplicación:"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Para ejecutar tests:"
echo "  pytest"
echo ""
echo "Para ver la documentación:"
echo "  http://localhost:8000/api/docs"
echo ""

