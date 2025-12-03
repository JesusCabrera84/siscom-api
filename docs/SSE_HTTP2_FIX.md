# Solución para ERR_HTTP2_PROTOCOL_ERROR en SSE

## Problema
Los navegadores reportan `ERR_HTTP2_PROTOCOL_ERROR 200` al conectarse a endpoints de Server-Sent Events (SSE) cuando se usa HTTP/2. Esto ocurre porque **SSE fue diseñado para HTTP/1.1** y tiene incompatibilidades con HTTP/2.

## Solución Implementada

### 1. Forzar HTTP/1.1 en Uvicorn
Se ha configurado uvicorn para usar exclusivamente HTTP/1.1:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --http h11
```

Archivos modificados:
- `Dockerfile`: CMD actualizado con `--http h11`
- `Makefile`: targets `dev` y `run` actualizados

### 2. Headers SSE Optimizados
Se agregaron headers específicos para SSE en ambos endpoints:

```python
headers={
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",  # Para nginx/proxies
    "Connection": "keep-alive",
}
```

Archivos modificados:
- `app/api/routes/public.py`: endpoint `/stream`
- `app/api/routes/stream.py`: endpoint `/stream`

## Configuración AWS (Si aplica)

Si estás usando un **Application Load Balancer (ALB)** o **CloudFront** delante de tu API, necesitas configuraciones adicionales:

### AWS Application Load Balancer

Si tienes un ALB, necesitas:

1. **Configurar HTTP/1.1 en el Target Group**:
   - Ve a EC2 → Target Groups
   - Selecciona tu target group
   - En "Health checks", asegúrate de que usa HTTP/1.1
   - En "Attributes", configura:
     - `deregistration_delay.timeout_seconds`: 120 (o más)
     - `stickiness.enabled`: true (importante para SSE)

2. **Configurar el Listener del ALB**:
   - El ALB puede recibir HTTP/2 del cliente
   - Pero debe comunicarse con el backend usando HTTP/1.1
   - Esto es automático, el ALB hace downgrade

3. **Aumentar el Idle Timeout**:
```bash
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn <tu-alb-arn> \
  --attributes Key=idle_timeout.timeout_seconds,Value=300
```

### AWS CloudFront (Si aplica)

Si usas CloudFront delante del ALB:

1. **Configurar comportamiento para SSE**:
```json
{
  "PathPattern": "/api/v1/*/stream",
  "TargetOriginId": "api-origin",
  "ViewerProtocolPolicy": "https-only",
  "AllowedMethods": ["GET", "HEAD", "OPTIONS"],
  "CachedMethods": ["GET", "HEAD"],
  "Compress": false,
  "DefaultTTL": 0,
  "MaxTTL": 0,
  "MinTTL": 0,
  "ForwardedValues": {
    "QueryString": true,
    "Cookies": {"Forward": "all"},
    "Headers": ["Accept", "Authorization"]
  }
}
```

2. **Configurar Origin**:
   - Origin Protocol Policy: HTTP Only (o HTTPS si tu ALB tiene SSL)
   - HTTP Version: HTTP/1.1 only

## Verificación

### 1. Verificar protocolo del servidor:
```bash
# En desarrollo
curl -v http://localhost:8000/health 2>&1 | grep "HTTP/"

# En producción
curl -v https://api.geminislabs.com/health 2>&1 | grep "HTTP/"
```

### 2. Probar SSE endpoint:
```bash
# Endpoint público
curl -N https://api.geminislabs.com/api/v1/public/share-location/stream?token=<tu-token>

# Deberías ver eventos SSE streaming sin errores
```

### 3. Verificar desde el navegador:
```javascript
// En la consola del navegador
const evtSource = new EventSource('https://api.geminislabs.com/api/v1/public/share-location/stream?token=<token>');

evtSource.onmessage = (event) => {
  console.log('Mensaje:', event.data);
};

evtSource.onerror = (error) => {
  console.error('Error:', error);
  console.log('ReadyState:', evtSource.readyState);
};

// ReadyState: 0=CONNECTING, 1=OPEN, 2=CLOSED
```

## Deployment

Para aplicar los cambios:

```bash
# 1. Commit y push
git add Dockerfile Makefile app/api/routes/
git commit -m "Fix: Forzar HTTP/1.1 para compatibilidad SSE"
git push origin master

# 2. El workflow de GitHub Actions desplegará automáticamente
# 3. Esperar ~2-3 minutos para que el contenedor esté healthy
# 4. Verificar logs en EC2:
ssh usuario@ec2 "docker logs siscom-api --tail 50"
```

## Troubleshooting

### Si el error persiste:

1. **Verificar que el cambio se aplicó**:
```bash
# Conectarte a EC2
ssh usuario@ec2-instance

# Verificar el comando del contenedor
docker inspect siscom-api | grep -A 5 "Cmd"

# Deberías ver: --http, h11
```

2. **Verificar si hay proxy/ALB en medio**:
```bash
# Ver headers de respuesta
curl -v https://api.geminislabs.com/health 2>&1 | grep -i "server:\|via:\|x-"
```

3. **Revisar Security Groups**:
   - Asegúrate de que el puerto 8000 esté abierto
   - Si hay ALB, debe poder comunicarse con el EC2

4. **Revisar logs del contenedor**:
```bash
docker logs siscom-api -f
```

## Referencias

- [SSE y HTTP/2 incompatibilidad](https://github.com/whatwg/html/issues/2177)
- [Uvicorn HTTP protocols](https://www.uvicorn.org/settings/#http)
- [AWS ALB SSE configuration](https://aws.amazon.com/premiumsupport/knowledge-center/elb-fix-connection-timeout/)

## Notas Importantes

- HTTP/2 usa multiplexing que puede causar problemas con streaming de larga duración
- SSE requiere conexiones persistentes que pueden ser cerradas por proxies
- Los navegadores limitan conexiones SSE a 6 por dominio en HTTP/1.1
- Considera usar WebSockets si HTTP/2 es un requisito estricto
