#!/bin/bash
# Script para ejecutar tests unitarios de SISCOM API

set -e

echo "🧪 Ejecutando Tests Unitarios - SISCOM API"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que estamos en el directorio correcto
if [ ! -f "pytest.ini" ]; then
    echo "❌ Error: Debe ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Verificar dependencias de test
echo -e "${BLUE}1. Verificando dependencias de test...${NC}"
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependencias de test...${NC}"
    pip3 install pytest pytest-asyncio pytest-cov pytest-mock httpx
fi

# Crear base de datos de test si no existe
echo -e "${BLUE}2. Verificando base de datos de test...${NC}"
if command -v psql &> /dev/null; then
    psql -U postgres -lqt | cut -d \| -f 1 | grep -qw siscom_test || {
        echo "Creando base de datos siscom_test..."
        createdb siscom_test 2>/dev/null || \
        psql -U postgres -c "CREATE DATABASE siscom_test;" 2>/dev/null || \
        echo "⚠️  No se pudo crear BD de test, los tests de BD pueden fallar"
    }
else
    echo "⚠️  psql no encontrado, asumiendo BD de test existe"
fi

# Menú de opciones
echo ""
echo -e "${BLUE}Seleccione el tipo de tests a ejecutar:${NC}"
echo "1) Todos los tests"
echo "2) Solo tests unitarios (rápido)"
echo "3) Solo tests de integración"
echo "4) Tests con cobertura (reporte HTML)"
echo "5) Tests específicos de autenticación"
echo "6) Tests de un archivo específico"
echo ""
read -p "Opción (1-6) [1]: " option
option=${option:-1}

echo ""

case $option in
    1)
        echo -e "${GREEN}Ejecutando TODOS los tests...${NC}"
        pytest -v
        ;;
    2)
        echo -e "${GREEN}Ejecutando tests UNITARIOS...${NC}"
        pytest -v -m unit
        ;;
    3)
        echo -e "${GREEN}Ejecutando tests de INTEGRACIÓN...${NC}"
        pytest -v -m integration
        ;;
    4)
        echo -e "${GREEN}Ejecutando tests con COBERTURA...${NC}"
        pytest --cov=app --cov-report=term-missing --cov-report=html -v
        echo ""
        echo -e "${GREEN}✅ Reporte de cobertura generado en: htmlcov/index.html${NC}"
        echo "Para ver el reporte: xdg-open htmlcov/index.html"
        ;;
    5)
        echo -e "${GREEN}Ejecutando tests de AUTENTICACIÓN...${NC}"
        pytest -v -m auth
        ;;
    6)
        echo ""
        echo "Archivos de test disponibles:"
        ls -1 test/test_*.py | cat -n
        echo ""
        read -p "Ingrese el nombre del archivo (ej: test_health.py): " filename
        pytest -v "test/$filename"
        ;;
    *)
        echo "Opción inválida, ejecutando todos los tests..."
        pytest -v
        ;;
esac

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ Tests completados exitosamente!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}⚠️  Algunos tests fallaron${NC}"
    echo -e "${YELLOW}========================================${NC}"
fi

echo ""
echo "Comandos útiles:"
echo "  pytest -v                    # Todos los tests verbose"
echo "  pytest -m unit               # Solo unitarios"
echo "  pytest -m integration        # Solo integración"
echo "  pytest --cov=app             # Con cobertura"
echo "  pytest test/test_health.py   # Un archivo específico"
echo ""

exit $exit_code

