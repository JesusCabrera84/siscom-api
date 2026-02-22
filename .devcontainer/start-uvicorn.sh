#!/bin/sh
if pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  echo "[siscom-api] uvicorn ya está en ejecución (puerto 8080)"
  exit 0
fi

# Esperar a que el workspace esté montado
sleep 3
if ! [ -f /app/app/main.py ]; then
  echo "[siscom-api] ERROR: /app/app/main.py no encontrado" | tee -a /tmp/uvicorn.log
  exit 1
fi

# Validar que el módulo sea importable ANTES de iniciar
if ! cd /app && python -c "from app.main import app" 2>/tmp/uvicorn-import-error.log; then
  echo "[siscom-api] ERROR: No se puede importar app.main" | tee -a /tmp/uvicorn.log
  cat /tmp/uvicorn-import-error.log | tee -a /tmp/uvicorn.log
  exit 1
fi

# Iniciar uvicorn en background con mejor manejo de señales
cd /app && nohup uvicorn app.main:app --port 8080 --host 0.0.0.0 >> /tmp/uvicorn.log 2>&1 &
UVICORN_PID=$!
sleep 2  # Dar tiempo a que uvicorn se inicie

# Verificar que el proceso siga vivo
if ! kill -0 $UVICORN_PID 2>/dev/null; then
  echo "[siscom-api] ERROR: uvicorn murió inmediatamente" | tee -a /tmp/uvicorn.log
  tail -20 /tmp/uvicorn.log
  exit 1
fi

echo "[siscom-api] uvicorn iniciado (PID: $UVICORN_PID, puerto 8080). Log: /tmp/uvicorn.log"