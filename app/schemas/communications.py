"""Schemas Pydantic para el módulo de comunicaciones."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class DeviceHistoryRequest(BaseModel):
    """
    Schema para la solicitud de historial de dispositivos.

    Valida que device_ids sea una lista con al menos 1 dispositivo.
    """

    device_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de IDs de dispositivos GPS",
        examples=[["867564050638581", "DEVICE123"]],
    )

    class Config:
        json_schema_extra = {
            "example": {"device_ids": ["867564050638581", "DEVICE123", "GPS001"]}
        }


class CommunicationResponse(BaseModel):
    """
    Schema para la respuesta de comunicaciones GPS (histórico).

    Representa un registro de comunicación de un dispositivo GPS
    de las tablas Suntech o Queclink.
    """

    id: int
    device_id: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    speed: Decimal | None = None
    course: Decimal | None = None
    gps_datetime: datetime | None = None
    main_battery_voltage: Decimal | None = None
    backup_battery_voltage: Decimal | None = None
    odometer: int | None = None
    trip_distance: int | None = None
    total_distance: int | None = None
    engine_status: str | None = None
    fix_status: str | None = None
    alert_type: str | None = None

    class Config:
        from_attributes = True  # Para SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": 1,
                "device_id": "867564050638581",
                "latitude": 19.4326,
                "longitude": -99.1332,
                "speed": 45.5,
                "course": 180.0,
                "gps_datetime": "2024-01-15T10:30:00",
                "main_battery_voltage": 12.5,
                "backup_battery_voltage": 3.7,
                "odometer": 15000,
                "trip_distance": 500,
                "total_distance": 150000,
                "engine_status": "ON",
                "fix_status": "VALID",
                "alert_type": None,
            }
        }


class CommunicationLatestResponse(BaseModel):
    """
    Schema para la respuesta de última comunicación (current_state).

    Representa el estado actual de un dispositivo GPS desde la tabla
    communications_current_state. No incluye 'id' ya que device_id es la PK.
    """

    device_id: str
    backup_battery_voltage: Decimal | None = None
    course: Decimal | None = None
    delivery_type: str | None = None
    engine_status: str | None = None
    fix_status: str | None = None
    gps_datetime: datetime | None = None
    gps_epoch: int | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    main_battery_voltage: Decimal | None = None
    msg_class: str | None = None
    network_status: str | None = None
    odometer: int | None = None
    rx_lvl: int | None = None
    satellites: int | None = None
    speed: Decimal | None = None
    received_epoch: int | None = None
    received_at: datetime | None = None

    class Config:
        from_attributes = True  # Para SQLAlchemy models
        json_schema_extra = {
            "example": {
                "device_id": "867564050638581",
                "latitude": 19.4326,
                "longitude": -99.1332,
                "speed": 45.5,
                "course": 180.0,
                "gps_datetime": "2024-01-15T10:30:00",
                "gps_epoch": 1705318200,
                "main_battery_voltage": 12.5,
                "backup_battery_voltage": 3.7,
                "odometer": 15000,
                "engine_status": "ON",
                "fix_status": "VALID",
                "satellites": 12,
                "rx_lvl": -65,
                "network_status": "CONNECTED",
                "msg_class": "HEARTBEAT",
                "delivery_type": "GPRS",
                "received_epoch": 1705318201,
                "received_at": "2024-01-15T10:30:01",
            }
        }
