# 🔄 Migración a REST v1 - Resumen de Cambios

## ✅ ¿Qué cambió?

Los endpoints han sido actualizados para seguir las **mejores prácticas REST**.

---

## 📋 Comparación Rápida

### ❌ ANTES (Deprecated)

```bash
# POST con body JSON
POST /communications/history
Body: {"device_ids": ["867564050638581"]}
```

### ✅ AHORA (REST Compliant)

```bash
# GET con query parameters
GET /api/v1/communications?device_ids=867564050638581
```

---

## 📡 Tabla de Migración

| Antes | Ahora | Método | Auth |
|-------|-------|--------|------|
| `POST /communications/history` | `GET /api/v1/communications` | GET | ✅ JWT |
| `GET /stream/` | `GET /api/v1/communications/stream` | GET | ❌ No |
| ❌ No existía | `GET /api/v1/devices/{device_id}/communications` | GET | ✅ JWT |
| ❌ No existía | `GET /api/v1/devices/{device_id}/communications/stream` | GET | ❌ No |

---

## 🚀 Ejemplos de Uso

### 1️⃣ Histórico de Múltiples Dispositivos

**Antes:**
```bash
curl -X POST http://10.8.0.1:8000/communications/history \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_ids": ["867564050638581", "DEVICE123"]}'
```

**Ahora:**
```bash
curl http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581&device_ids=DEVICE123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ"
```

**JavaScript:**
```javascript
// Múltiples device_ids con URLSearchParams
const deviceIds = ['867564050638581', 'DEVICE123'];
const params = new URLSearchParams();
deviceIds.forEach(id => params.append('device_ids', id));

const response = await fetch(
  `http://10.8.0.1:8000/api/v1/communications?${params}`,
  {
    headers: {
      'Authorization': 'Bearer TOKEN'
    }
  }
);
```

---

### 2️⃣ Histórico de UN Solo Dispositivo (NUEVO)

```bash
curl http://10.8.0.1:8000/api/v1/devices/867564050638581/communications \
  -H "Authorization: Bearer TOKEN"
```

**JavaScript:**
```javascript
const deviceId = '867564050638581';
const response = await fetch(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications`,
  {
    headers: {
      'Authorization': 'Bearer TOKEN'
    }
  }
);
```

---

### 3️⃣ Stream SSE de Múltiples Dispositivos

**Antes:**
```bash
curl -N http://10.8.0.1:8000/stream/?device_ids=867564050638581&device_ids=DEVICE123
```

**Ahora:**
```bash
curl -N http://10.8.0.1:8000/api/v1/communications/stream?device_ids=867564050638581&device_ids=DEVICE123
```

**JavaScript:**
```javascript
const deviceIds = ['867564050638581', 'DEVICE123'];
const params = new URLSearchParams();
deviceIds.forEach(id => params.append('device_ids', id));

const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/communications/stream?${params}`
);

eventSource.addEventListener('update', (event) => {
  const data = JSON.parse(event.data);
  console.log('Actualización:', data);
});
```

---

### 4️⃣ Stream SSE de UN Solo Dispositivo (NUEVO)

```bash
curl -N http://10.8.0.1:8000/api/v1/devices/867564050638581/communications/stream
```

**JavaScript:**
```javascript
const deviceId = '867564050638581';
const eventSource = new EventSource(
  `http://10.8.0.1:8000/api/v1/devices/${deviceId}/communications/stream`
);

eventSource.addEventListener('update', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Actualización de ${deviceId}:`, data);
});
```

---

## 🎯 Beneficios de los Cambios

### ✅ 1. REST Compliant
- GET para lectura (no modifica datos)
- Cacheable por navegadores y proxies
- URLs pueden ser guardadas como bookmarks

### ✅ 2. Versionamiento
- `/api/v1/` permite evolucionar sin romper clientes
- Futuras versiones: `/api/v2/`, `/api/v3/`

### ✅ 3. Estructura Jerárquica Clara
```
/api/v1/
  ├── communications/              ← Colección de comunicaciones
  │   ├── GET                      → Múltiples dispositivos
  │   └── stream/                  → Stream múltiples
  │
  └── devices/
      └── {device_id}/             ← Dispositivo específico
          └── communications/
              ├── GET              → Un solo dispositivo
              └── stream/          → Stream uno
```

### ✅ 4. Query Parameters
- Más flexible y extensible
- Fácil agregar filtros: `?device_ids=X&start_date=...&limit=100`

### ✅ 5. Path Parameters para Recursos Específicos
- Semánticamente claro: `/devices/867564050638581/communications`
- "Las comunicaciones del dispositivo 867564050638581"

---

## 📦 Archivos Actualizados

```
app/
├── api/
│   └── routes/
│       └── communications.py  ← Todos los endpoints consolidados aquí
├── main.py                    ← Removido router de stream (integrado)
└── schemas/
    └── communications.py      ← Schema de respuesta (CommunicationResponse)
```

---

## 📮 En Postman

1. **Importa la nueva colección:**
   - `SISCOM-API-v1.postman_collection.json`

2. **Configura variables:**
   - `base_url` = `http://10.8.0.1:8000`
   - `token` = `eyJhbGciOiJIUzI1NiJ9...`

3. **Prueba los 4 nuevos endpoints** ✅

---

## 🔍 Documentación Automática

Abre tu navegador:
```
http://10.8.0.1:8000/api/docs
```

Verás todos los endpoints con:
- Schemas de request/response
- Ejemplos interactivos
- Botón "Try it out" para probar

---

## ⚠️ Breaking Changes

### ⚠️ El endpoint anterior YA NO FUNCIONA:

```bash
# ❌ Este endpoint ya no existe
POST /communications/history
```

### ✅ Usa el nuevo:

```bash
# ✅ Nuevo endpoint REST
GET /api/v1/communications?device_ids=867564050638581
```

---

## 📝 Checklist de Actualización Frontend

- [ ] Cambiar de POST a GET
- [ ] Cambiar body JSON a query parameters
- [ ] Actualizar URLs con `/api/v1/`
- [ ] Usar URLSearchParams para múltiples device_ids
- [ ] Actualizar endpoints de stream
- [ ] Probar con DevTools del navegador
- [ ] Actualizar tests (si existen)

---

## 💻 Ejemplo de Actualización en Svelte

### ❌ Antes:

```javascript
const response = await fetch('http://10.8.0.1:8000/communications/history', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    device_ids: ['867564050638581', 'DEVICE123']
  })
});
```

### ✅ Ahora:

```javascript
const deviceIds = ['867564050638581', 'DEVICE123'];
const params = new URLSearchParams();
deviceIds.forEach(id => params.append('device_ids', id));

const response = await fetch(
  `http://10.8.0.1:8000/api/v1/communications?${params}`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
```

---

## 📚 Documentación Completa

- **API_REST_GUIDE.md** - Guía completa de todos los endpoints
- **http://10.8.0.1:8000/api/docs** - Documentación interactiva Swagger
- **SISCOM-API-v1.postman_collection.json** - Colección de Postman actualizada

---

## ✅ Verificación Rápida

```bash
# 1. Health check (sin cambios)
curl http://10.8.0.1:8000/health

# 2. Nuevo endpoint de comunicaciones (GET)
curl 'http://10.8.0.1:8000/api/v1/communications?device_ids=867564050638581' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ"

# 3. Nuevo endpoint por dispositivo (GET)
curl 'http://10.8.0.1:8000/api/v1/devices/867564050638581/communications' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.XmNK3GpH3Ys_7wsYBfq4C3M6goz71I7dTgUkuIa5lyQ"

# 4. Stream SSE (GET)
curl -N 'http://10.8.0.1:8000/api/v1/communications/stream?device_ids=867564050638581'
```

---

**¡Listo!** 🎉 Tus endpoints ahora siguen las mejores prácticas REST.

