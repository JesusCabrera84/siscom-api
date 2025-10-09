#!/usr/bin/env python3
"""
Script de prueba para verificar que las métricas StatsD están funcionando con aio-statsd.

Uso:
    python test_metrics.py

Este script envía métricas de prueba a StatsD/Telegraf usando aio-statsd (asíncrono).
"""

import asyncio

import aiostatsd

from app.core.config import settings


async def test_metrics():
    """Envía métricas de prueba a StatsD."""
    print(f"Conectando a StatsD en {settings.STATSD_HOST}:{settings.STATSD_PORT}")
    print(f"Prefix: {settings.STATSD_PREFIX}")
    print()

    # Crear cliente aio-statsd
    client = aiostatsd.Client(
        host=settings.STATSD_HOST,
        port=settings.STATSD_PORT,
        prefix=settings.STATSD_PREFIX,
    )

    app_tag = f"app:{settings.APP_NAME}"

    print("Enviando métricas de prueba...")
    print()

    # 1. Counter de peticiones
    print(f"✓ Incrementando contador de peticiones (tag: {app_tag})")
    for i in range(5):
        await client.increment(f"requests,{app_tag}")
        await asyncio.sleep(0.1)

    # 2. Timing de latencia
    print(f"✓ Enviando métricas de latencia (tag: {app_tag})")
    for latency in [45.2, 52.1, 48.9, 61.3, 49.8]:
        await client.timing(f"latency.stream,{app_tag}", latency)
        await asyncio.sleep(0.1)

    # 3. Simulación de conexiones SSE
    print(f"✓ Simulando conexiones SSE (tag: {app_tag})")

    # Incrementar conexiones
    print(f"  → Incrementando 3 conexiones")
    for i in range(3):
        await client.increment(f"sse.active_connections,{app_tag}")
        await asyncio.sleep(0.2)

    # Decrementar conexiones
    print(f"  → Decrementando 2 conexiones")
    for i in range(2):
        await client.decrement(f"sse.active_connections,{app_tag}")
        await asyncio.sleep(0.2)

    # Cerrar cliente
    await client.close()

    print()
    print("✅ Métricas de prueba enviadas correctamente")
    print()
    print("Verifica en Telegraf/InfluxDB que las siguientes métricas aparecen:")
    print(f"  - {settings.STATSD_PREFIX}.requests")
    print(f"  - {settings.STATSD_PREFIX}.latency.stream")
    print(f"  - {settings.STATSD_PREFIX}.sse.active_connections")
    print()
    print("Todas las métricas deben tener el tag: app=siscom-api")
    print()
    print("Formato de tags usado: InfluxDB (metric,tag1=value1,tag2=value2:value|type)")


async def main():
    try:
        await test_metrics()
    except Exception as e:
        print(f"❌ Error al enviar métricas: {e}")
        print()
        print("Verifica que:")
        print("  1. Telegraf está corriendo")
        print("  2. El puerto 8125/udp está accesible")
        print(
            f"  3. La configuración en .env es correcta (STATSD_HOST={settings.STATSD_HOST})"
        )
        print()
        print("Puedes probar manualmente con:")
        print(
            f"  echo 'siscom_api.test,app=siscom-api:1|c' | nc -u -w1 {settings.STATSD_HOST} {settings.STATSD_PORT}"
        )
        print()
        print("NOTA: siscom-api usa el puerto 8126 (no 8125) para no interferir con otros proyectos")


if __name__ == "__main__":
    asyncio.run(main())

