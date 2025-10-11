#!/bin/bash
# Script para probar el logging del middleware
# Uso: ./test_middleware_logging.sh

echo "🧪 Probando logging del middleware"
echo "====================================="
echo ""
echo "Este script hará varias peticiones a tu API local"
echo "Revisa los logs para ver qué se registra y qué se cuenta"
echo ""

API_URL="http://localhost:8000"

echo "1️⃣ Petición a /health (debe estar EXCLUIDA)"
curl -s "${API_URL}/health" > /dev/null
echo "✅ Petición a /health enviada"
echo ""

echo "2️⃣ Petición a /docs (debe estar EXCLUIDA)"
curl -s "${API_URL}/docs" > /dev/null
echo "✅ Petición a /docs enviada"
echo ""

echo "3️⃣ Petición a /openapi.json (debe estar EXCLUIDA)"
curl -s "${API_URL}/openapi.json" > /dev/null
echo "✅ Petición a /openapi.json enviada"
echo ""

echo "4️⃣ Petición a /api/v1/communications (debe CONTARSE)"
curl -s -H "Authorization: Bearer test" "${API_URL}/api/v1/communications" > /dev/null
echo "✅ Petición a /api/v1/communications enviada"
echo ""

echo "5️⃣ Petición a una ruta que no existe (debe CONTARSE)"
curl -s "${API_URL}/ruta-inexistente" > /dev/null
echo "✅ Petición a /ruta-inexistente enviada"
echo ""

echo "====================================="
echo "📋 Resumen"
echo "====================================="
echo ""
echo "Ahora revisa los logs de tu aplicación:"
echo ""
echo "  Si estás usando Docker:"
echo "    docker logs siscom-api | tail -30"
echo ""
echo "  Si estás ejecutando localmente:"
echo "    Revisa la salida de uvicorn"
echo ""
echo "Deberías ver:"
echo "  • 📨 Request: ... para TODAS las peticiones"
echo "  • ⏭️ Ruta excluida: para /health, /docs, /openapi.json"
echo "  • 📊 Contando métrica: para /api/v1/communications y /ruta-inexistente"
echo "  • ⏱️ Latencia: solo para las rutas contadas"
echo ""
echo "Si ves incrementos sin que veas logs de '📊 Contando métrica',"
echo "significa que el incremento viene de otro lado (ej: health checks frecuentes)"

