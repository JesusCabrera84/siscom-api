#!/bin/bash
# Script para verificar que el fix de aio-statsd está correcto
# Uso: ./verify_fix.sh

echo "🔍 Verificando corrección del bug de aio-statsd"
echo "================================================"
echo ""

errors=0

# 1. Verificar que NO hay await incorrectos en metrics.py
echo "1️⃣ Verificando que NO hay 'await client.increment()' en metrics.py..."
if grep -q "await self.client.increment" app/utils/metrics.py; then
    echo "❌ ERROR: Todavía hay 'await self.client.increment()' en metrics.py"
    echo "   Los métodos increment/decrement/timing NO son async"
    errors=$((errors + 1))
else
    echo "✅ Correcto: No se usa 'await' con client.increment()"
fi

if grep -q "await self.client.decrement" app/utils/metrics.py; then
    echo "❌ ERROR: Todavía hay 'await self.client.decrement()' en metrics.py"
    errors=$((errors + 1))
else
    echo "✅ Correcto: No se usa 'await' con client.decrement()"
fi

if grep -q "await self.client.timing" app/utils/metrics.py; then
    echo "❌ ERROR: Todavía hay 'await self.client.timing()' en metrics.py"
    errors=$((errors + 1))
else
    echo "✅ Correcto: No se usa 'await' con client.timing()"
fi
echo ""

# 2. Verificar que SÍ hay await correcto en connect/close
echo "2️⃣ Verificando que SÍ hay 'await client.connect()' (correcto)..."
if grep -q "await self.client.connect" app/utils/metrics.py; then
    echo "✅ Correcto: Se usa 'await client.connect()'"
else
    echo "❌ ERROR: Falta 'await self.client.connect()'"
    errors=$((errors + 1))
fi
echo ""

# 3. Verificar que logging está configurado en main.py
echo "3️⃣ Verificando configuración de logging en main.py..."
if grep -q "logging.basicConfig" app/main.py; then
    echo "✅ Correcto: logging.basicConfig() está configurado"
else
    echo "❌ ERROR: Falta logging.basicConfig() en main.py"
    errors=$((errors + 1))
fi

if grep -q 'logging.getLogger("app.core.middleware")' app/main.py; then
    echo "✅ Correcto: Logger del middleware está configurado"
else
    echo "❌ ERROR: Falta configuración del logger del middleware"
    errors=$((errors + 1))
fi
echo ""

# 4. Verificar que el middleware tiene logging
echo "4️⃣ Verificando que middleware usa logger..."
if grep -q "logger.info" app/core/middleware.py; then
    echo "✅ Correcto: Middleware usa logger.info()"
else
    echo "❌ ERROR: Middleware no usa logger.info()"
    errors=$((errors + 1))
fi
echo ""

# 5. Verificar variables STATSD en docker-compose
echo "5️⃣ Verificando variables STATSD en docker-compose.yml..."
if grep -q "STATSD_HOST:" docker-compose.yml; then
    echo "✅ Correcto: STATSD_HOST en docker-compose.yml"
else
    echo "❌ ERROR: Falta STATSD_HOST en docker-compose.yml"
    errors=$((errors + 1))
fi
echo ""

# Resumen final
echo "================================================"
if [ $errors -eq 0 ]; then
    echo "✅ TODAS LAS VERIFICACIONES PASARON"
    echo ""
    echo "Todo está correcto. Puedes hacer commit y push:"
    echo "  git add -A"
    echo "  git commit -m \"fix: corregir uso de await en aio-statsd y agregar logging\""
    echo "  git push origin master"
    exit 0
else
    echo "❌ SE ENCONTRARON $errors ERRORES"
    echo ""
    echo "Por favor corrige los errores antes de hacer commit."
    exit 1
fi

