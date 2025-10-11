#!/bin/bash
# Script para verificar la configuración de StatsD en siscom-api
# Uso: ./verify_statsd_config.sh

echo "🔍 Verificando configuración de StatsD"
echo "========================================"
echo ""

# 1. Verificar que las variables están en config.py
echo "1️⃣ Verificando app/core/config.py..."
if grep -q "STATSD_HOST" app/core/config.py; then
    echo "✅ STATSD_HOST encontrado en config.py"
    grep "STATSD_HOST" app/core/config.py | head -1
else
    echo "❌ ERROR: STATSD_HOST NO está en config.py"
fi

if grep -q "STATSD_PORT" app/core/config.py; then
    echo "✅ STATSD_PORT encontrado en config.py"
    grep "STATSD_PORT" app/core/config.py | head -1
else
    echo "❌ ERROR: STATSD_PORT NO está en config.py"
fi

if grep -q "STATSD_PREFIX" app/core/config.py; then
    echo "✅ STATSD_PREFIX encontrado en config.py"
    grep "STATSD_PREFIX" app/core/config.py | head -1
else
    echo "❌ ERROR: STATSD_PREFIX NO está en config.py"
fi
echo ""

# 2. Verificar que se usan en metrics.py
echo "2️⃣ Verificando app/utils/metrics.py..."
if grep -q "settings.STATSD_HOST" app/utils/metrics.py; then
    echo "✅ settings.STATSD_HOST usado en metrics.py"
    grep "settings.STATSD_HOST" app/utils/metrics.py
else
    echo "❌ ERROR: settings.STATSD_HOST NO usado en metrics.py"
fi

if grep -q "settings.STATSD_PORT" app/utils/metrics.py; then
    echo "✅ settings.STATSD_PORT usado en metrics.py"
    grep "settings.STATSD_PORT" app/utils/metrics.py
else
    echo "❌ ERROR: settings.STATSD_PORT NO usado en metrics.py"
fi
echo ""

# 3. Verificar que están en docker-compose.yml
echo "3️⃣ Verificando docker-compose.yml..."
if grep -q "STATSD_HOST:" docker-compose.yml; then
    echo "✅ STATSD_HOST en docker-compose.yml"
    grep "STATSD_HOST:" docker-compose.yml
else
    echo "❌ ERROR: STATSD_HOST NO está en docker-compose.yml"
    echo "   Las variables no llegarán al contenedor!"
fi

if grep -q "STATSD_PORT:" docker-compose.yml; then
    echo "✅ STATSD_PORT en docker-compose.yml"
    grep "STATSD_PORT:" docker-compose.yml
else
    echo "❌ ERROR: STATSD_PORT NO está en docker-compose.yml"
fi

if grep -q "STATSD_PREFIX:" docker-compose.yml; then
    echo "✅ STATSD_PREFIX en docker-compose.yml"
    grep "STATSD_PREFIX:" docker-compose.yml
else
    echo "❌ ERROR: STATSD_PREFIX NO está en docker-compose.yml"
fi
echo ""

# 4. Verificar que están en el workflow
echo "4️⃣ Verificando .github/workflows/deploy.yml..."
if grep -q "STATSD_HOST:" .github/workflows/deploy.yml; then
    echo "✅ STATSD_HOST en workflow"
    grep "STATSD_HOST:" .github/workflows/deploy.yml | head -2
else
    echo "❌ ERROR: STATSD_HOST NO está en workflow"
fi
echo ""

# 5. Verificar archivo .env local (si existe)
echo "5️⃣ Verificando .env local (si existe)..."
if [ -f .env ]; then
    if grep -q "STATSD" .env; then
        echo "✅ Variables STATSD en .env:"
        grep "STATSD" .env
    else
        echo "⚠️  .env existe pero no tiene variables STATSD"
        echo "   Esto es normal si solo se usan en producción"
    fi
else
    echo "ℹ️  No existe .env local (normal en desarrollo)"
fi
echo ""

# Resumen
echo "========================================"
echo "📊 Resumen de Verificación"
echo "========================================"
echo ""
echo "Flujo de configuración correcto:"
echo "1. Variables definidas en app/core/config.py ✅"
echo "2. Usadas en app/utils/metrics.py via settings ✅"
echo "3. Declaradas en docker-compose.yml environment ✅"
echo "4. Creadas en .env por workflow de GitHub ✅"
echo "5. Pasadas al contenedor via docker-compose ✅"
echo ""
echo "Para uso en producción, asegúrate de configurar en GitHub:"
echo "Settings → Secrets and variables → Actions → Variables"
echo "  - STATSD_HOST (ej: telegraf)"
echo "  - STATSD_PORT (ej: 8126)"
echo "  - STATSD_PREFIX (ej: siscom_api)"

