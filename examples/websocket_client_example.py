#!/usr/bin/env python3
"""
Ejemplo de cliente WebSocket para el endpoint de streaming de siscom-api.

Este script se conecta al WebSocket y muestra los mensajes en tiempo real.

Uso:
    python websocket_client_example.py --device-ids 0848086072,0848086073
    python websocket_client_example.py --device-ids 0848086072 --host localhost:8000
"""

import asyncio
import json
import sys
from argparse import ArgumentParser

try:
    import websockets
except ImportError:
    print("❌ Error: La librería 'websockets' no está instalada.")
    print("   Instalar con: pip install websockets")
    sys.exit(1)


async def connect_to_stream(host: str, device_ids: list[str]):
    """
    Conecta al WebSocket y procesa mensajes en tiempo real.

    Args:
        host: Host del servidor (ej: localhost:8000)
        device_ids: Lista de device_ids a monitorear
    """
    # Construir URL
    device_ids_str = ",".join(device_ids)
    uri = f"ws://{host}/api/v1/stream?device_ids={device_ids_str}"

    print(f"🔌 Conectando a: {uri}")
    print(f"📡 Monitoreando devices: {device_ids}")
    print("-" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado exitosamente\n")

            # Contador de mensajes
            message_count = 0

            async for message in websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get("event", "unknown")

                    if event_type == "message":
                        # Mensaje de datos
                        message_count += 1
                        payload = data.get("data", {})
                        device_data = payload.get("data", {})

                        device_id = device_data.get("DEVICE_ID", "N/A")
                        timestamp = payload.get("timestamp", "N/A")

                        print(f"📦 Mensaje #{message_count}")
                        print(f"   Device ID: {device_id}")
                        print(f"   Timestamp: {timestamp}")

                        # Mostrar campos interesantes si existen
                        interesting_fields = [
                            "LAT",
                            "LON",
                            "SPEED",
                            "ALTITUDE",
                            "HEADING",
                            "SATELLITES",
                        ]
                        for field in interesting_fields:
                            if field in device_data:
                                print(f"   {field}: {device_data[field]}")

                        print()

                    elif event_type == "ping":
                        # Keep-alive
                        print("💓 Keep-alive recibido")

                    elif event_type == "error":
                        # Error del servidor
                        error_msg = data.get("data", {}).get("message", "Unknown error")
                        print(f"❌ Error del servidor: {error_msg}")
                        break

                    else:
                        print(f"⚠️  Evento desconocido: {event_type}")
                        print(f"   Datos: {data}")

                except json.JSONDecodeError as e:
                    print(f"❌ Error al decodificar JSON: {e}")
                    print(f"   Mensaje raw: {message}")
                except Exception as e:
                    print(f"❌ Error al procesar mensaje: {e}")

    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ Error de WebSocket: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Desconexión solicitada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Punto de entrada del script."""
    parser = ArgumentParser(description="Cliente WebSocket de ejemplo para siscom-api")
    parser.add_argument(
        "--device-ids",
        "-d",
        required=True,
        help="Device IDs separados por comas (ej: 0848086072,0848086073)",
    )
    parser.add_argument(
        "--host",
        "-H",
        default="localhost:8000",
        help="Host del servidor (default: localhost:8000)",
    )

    args = parser.parse_args()

    # Parsear device_ids
    device_ids = [d.strip() for d in args.device_ids.split(",") if d.strip()]

    if not device_ids:
        print("❌ Error: Debe especificar al menos un device_id")
        sys.exit(1)

    # Conectar
    try:
        asyncio.run(connect_to_stream(args.host, device_ids))
    except KeyboardInterrupt:
        print("\n👋 Hasta luego!")


if __name__ == "__main__":
    main()
