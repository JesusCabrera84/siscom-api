# Features

## 1. Health Check Endpoint

**Endpoint**: `GET /health`

**Purpose**: Service health monitoring and availability checking

**Requirements**:
- Must return 200 OK when service is running
- Must include service name and version
- No authentication required
- Response time should be < 100ms

**Response Format**:
```json
{
  "status": "healthy",
  "service": "siscom-api",
  "version": "0.1.0"
}
```

---

## 2. Historical Communications - Multiple Devices

**Endpoint**: `GET /api/v1/communications`

**Purpose**: Retrieve historical GPS communications for multiple devices simultaneously

**Requirements**:
- JWT authentication required
- Support 1-100 device IDs per request
- Return data from both Suntech and Queclink tables
- Results should be ordered by timestamp (newest first)

**Query Parameters**:
- `device_ids`: array of strings (required, min: 1, max: 100)

**Response**:
- Array of communication objects with GPS data (latitude, longitude, speed, course, timestamps, battery levels, odometer, etc.)

---

## 3. Historical Communications - Single Device

**Endpoint**: `GET /api/v1/devices/{device_id}/communications`

**Purpose**: Retrieve historical GPS communications for a specific device

**Requirements**:
- JWT authentication required
- Device ID as path parameter
- Return data from both Suntech and Queclink tables
- Results should be ordered by timestamp (newest first)

**Path Parameters**:
- `device_id`: string (required)

---

## 4. Real-Time Stream - Multiple Devices

**Endpoint**: `GET /api/v1/communications/stream`

**Purpose**: Subscribe to real-time GPS updates for multiple devices via Server-Sent Events

**Requirements**:
- No authentication required (configurable)
- Support 1-50 device IDs per request
- Must use SSE protocol (text/event-stream)
- Events should be sent as they arrive
- Connection should remain open indefinitely
- Client should be able to reconnect automatically

**Query Parameters**:
- `device_ids`: array of strings (required, min: 1, max: 50)

**Headers**:
- `Accept: text/event-stream` (required)

**Event Format**:
```
event: update
data: {"device_id": "...", "latitude": ..., "longitude": ..., "speed": ..., "timestamp": "..."}
```

---

## 5. Real-Time Stream - Single Device

**Endpoint**: `GET /api/v1/devices/{device_id}/communications/stream`

**Purpose**: Subscribe to real-time GPS updates for a specific device via Server-Sent Events

**Requirements**:
- No authentication required (configurable)
- Device ID as path parameter
- Must use SSE protocol (text/event-stream)
- Events should be sent as they arrive
- Connection should remain open indefinitely

**Path Parameters**:
- `device_id`: string (required)

