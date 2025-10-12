# 🐛 Bug Fix: aio-statsd métodos NO son async

## 🔴 Problema Encontrado

Al desplegar, se encontraron estos errores en los logs:

```
[Metrics] Error incrementing: object NoneType can't be used in 'await' expression
INFO:     10.8.0.2:50524 - "GET /api/v1/communications?device_ids=867564050638581 HTTP/1.1" 200 OK
[Metrics] Error incrementing: object NoneType can't be used in 'await' expression
```

Además, los logs del middleware con emojis (📨, 📊, ⏱️) NO aparecían.

## 🔍 Diagnóstico

### Problema 1: Métodos de aio-statsd NO son async

A pesar del nombre "aio-statsd" (async io), los métodos para enviar métricas **NO son async**:

```python
# En aio_statsd/client.py línea 315-321
def increment(self, key: str, value: int, sample_rate=None) -> None:  # ⚠️ NO es async!
    statsd_protocol: "StatsdProtocol" = StatsdProtocol().increment(key, value)
    self.send_statsd(statsd_protocol, sample_rate)

def decrement(self, key: str, value: int, sample_rate=None) -> None:  # ⚠️ NO es async!
    ...

def timing(self, key: str, value: int, sample_rate=None) -> None:  # ⚠️ NO es async!
    ...
```

El **único método async** es `connect()`.

### Problema 2: Logging no configurado

FastAPI/Uvicorn no mostraba los logs del middleware porque `logging.basicConfig()` no estaba configurado en `app/main.py`.

## ✅ Solución Aplicada

### Fix 1: Quitar `await` de métodos de envío de métricas

**Archivo: `app/utils/metrics.py`**

```python
# ❌ ANTES (INCORRECTO)
async def increment_requests(self, endpoint: str | None = None):
    await self.ensure_connected()
    await self.client.increment(metric, 1)  # ❌ ERROR: increment NO es async

# ✅ DESPUÉS (CORRECTO)
async def increment_requests(self, endpoint: str | None = None):
    await self.ensure_connected()  # ✅ SÍ es async
    self.client.increment(metric, 1)  # ✅ NO usar await
```

**Cambios en todos los métodos:**
- `increment_requests()` → `self.client.increment()` sin await
- `timing_latency()` → `self.client.timing()` sin await
- `increment_active_connections()` → `self.client.increment()` sin await
- `decrement_active_connections()` → `self.client.decrement()` sin await

### Fix 2: Configurar logging en main.py

**Archivo: `app/main.py`**

```python
import logging
from contextlib import asynccontextmanager
# ... imports

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Asegurar que el middleware tenga logging activado
logging.getLogger("app.core.middleware").setLevel(logging.INFO)
```

## 📊 Resultado Esperado

### Antes (con errores):
```
INFO:     127.0.0.1:44792 - "GET /health HTTP/1.1" 200 OK
[Metrics] Error incrementing: object NoneType can't be used in 'await' expression
INFO:     10.8.0.2:50524 - "GET /api/v1/communications?device_ids=867564050638581 HTTP/1.1" 200 OK
[Metrics] Error incrementing: object NoneType can't be used in 'await' expression
```

### Después (correcto):
```
INFO:     127.0.0.1:44792 - "GET /health HTTP/1.1" 200 OK
2024-10-12 15:30:45 - app.core.middleware - INFO - 📨 Request: GET /health | Client: 127.0.0.1 | User-Agent: python-requests/2.28.0
2024-10-12 15:30:45 - app.core.middleware - DEBUG - ⏭️  Ruta excluida de métricas: /health
INFO:     10.8.0.2:50524 - "GET /api/v1/communications?device_ids=867564050638581 HTTP/1.1" 200 OK
2024-10-12 15:30:50 - app.core.middleware - INFO - 📨 Request: GET /api/v1/communications | Client: 10.8.0.2
2024-10-12 15:30:50 - app.core.middleware - INFO - 📊 Contando métrica para: GET /api/v1/communications
2024-10-12 15:30:50 - app.core.middleware - INFO - ⏱️  Latencia: GET /api/v1/communications -> 125.45ms | Status: 200
```

## 🎓 Lecciones Aprendidas

### 1. "aio-statsd" es engañoso
- A pesar del nombre "aio" (async io), la mayoría de métodos NO son async
- Solo `connect()` y `close()` son async
- Los métodos de envío (`increment`, `decrement`, `timing`, etc.) son **sincrónicos**

### 2. Verificar siempre la firma de métodos
```python
# Cómo verificar si un método es async:
import inspect
print(inspect.iscoroutinefunction(client.increment))  # False
print(inspect.iscoroutinefunction(client.connect))    # True
```

### 3. Logging en FastAPI
- FastAPI/Uvicorn usa su propio sistema de logging
- Necesitas configurar `logging.basicConfig()` en `main.py`
- Los logs personalizados del middleware no aparecen sin esta configuración

### 4. Los errores silenciosos son peligrosos
- El `try/except` con `print()` ocultó el error real
- Mejor usar logging apropiado:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  
  try:
      ...
  except Exception as e:
      logger.error(f"Error: {e}", exc_info=True)  # Muestra traceback completo
  ```

## 🔗 Referencias

- Código de aio-statsd: `.venv/lib/python3.13/site-packages/aio_statsd/client.py` línea 315-321
- Documentación de logging: https://docs.python.org/3/library/logging.html
- FastAPI logging: https://fastapi.tiangolo.com/tutorial/handling-errors/#logging

## 📝 Archivos Modificados

1. `app/utils/metrics.py` - Quitado `await` de métodos de envío
2. `app/main.py` - Agregada configuración de logging
3. Este documento

## ✅ Checklist de Verificación

- [x] Quitar `await` de `client.increment()`
- [x] Quitar `await` de `client.decrement()`
- [x] Quitar `await` de `client.timing()`
- [x] Mantener `await` en `client.connect()`
- [x] Mantener `await` en `client.close()`
- [x] Configurar `logging.basicConfig()` en main.py
- [x] Configurar nivel de log para middleware
- [ ] Hacer commit y push
- [ ] Verificar en producción que los logs aparecen
- [ ] Verificar que NO hay errores "[Metrics] Error"

