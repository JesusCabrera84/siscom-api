#!/bin/bash

# Script para despliegue local con Docker
set -e

echo "🐳 Desplegando SISCOM API localmente con Docker..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

# Verificar docker-compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    echo "Crea un archivo .env con las variables necesarias"
    exit 1
fi

# Crear red si no existe
echo -e "${YELLOW}Verificando red Docker...${NC}"
if ! docker network inspect siscom-network >/dev/null 2>&1; then
    echo -e "${YELLOW}Creando red siscom-network...${NC}"
    docker network create siscom-network
    echo -e "${GREEN}✅ Red creada${NC}"
else
    echo -e "${GREEN}✅ Red ya existe${NC}"
fi

# Build de la imagen
echo -e "${YELLOW}Construyendo imagen Docker...${NC}"
docker build -t siscom-api:latest .
echo -e "${GREEN}✅ Imagen construida${NC}"

# Detener contenedor existente
echo -e "${YELLOW}Deteniendo contenedor existente (si existe)...${NC}"
docker compose down 2>/dev/null || true

# Levantar servicios
echo -e "${YELLOW}Levantando servicios...${NC}"
docker compose up -d

# Esperar a que el servicio esté listo
echo -e "${YELLOW}Esperando a que el servicio esté listo...${NC}"
sleep 5

# Verificar salud del contenedor
echo -e "${YELLOW}Verificando salud del contenedor...${NC}"
if docker ps | grep -q siscom-api; then
    echo -e "${GREEN}✅ Contenedor corriendo${NC}"
    
    # Probar health check
    sleep 5
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check exitoso${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check falló, verificando logs...${NC}"
        docker logs siscom-api --tail 20
    fi
else
    echo -e "${RED}❌ El contenedor no está corriendo${NC}"
    echo "Logs del contenedor:"
    docker logs siscom-api
    exit 1
fi

# Información final
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Despliegue completado!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "API disponible en: http://localhost:8000"
echo "Documentación: http://localhost:8000/api/docs"
echo "Health check: http://localhost:8000/health"
echo ""
echo "Ver logs:"
echo "  docker logs -f siscom-api"
echo ""
echo "Detener:"
echo "  docker compose down"
echo ""

