"""
Tests para los schemas Pydantic.
"""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.communications import CommunicationResponse, DeviceHistoryRequest


@pytest.mark.unit
class TestDeviceHistoryRequest:
    """Tests para el schema DeviceHistoryRequest."""

    def test_valid_device_history_request(self):
        """
        Test: Schema válido con lista de device IDs.
        """
        data = {"device_ids": ["DEVICE1", "DEVICE2", "DEVICE3"]}
        request = DeviceHistoryRequest(**data)

        assert len(request.device_ids) == 3
        assert "DEVICE1" in request.device_ids

    def test_device_history_request_min_length(self):
        """
        Test: Schema requiere al menos 1 device ID.
        """
        data = {"device_ids": []}

        with pytest.raises(ValidationError) as exc_info:
            DeviceHistoryRequest(**data)

        assert "at least 1 item" in str(exc_info.value).lower()

    def test_device_history_request_max_length(self):
        """
        Test: Schema limita a máximo 100 device IDs.
        """
        data = {"device_ids": [f"DEVICE{i}" for i in range(101)]}

        with pytest.raises(ValidationError) as exc_info:
            DeviceHistoryRequest(**data)

        assert "at most 100" in str(exc_info.value).lower()

    def test_device_history_request_single_device(self):
        """
        Test: Schema acepta un solo device ID.
        """
        data = {"device_ids": ["SINGLE_DEVICE"]}
        request = DeviceHistoryRequest(**data)

        assert len(request.device_ids) == 1
        assert request.device_ids[0] == "SINGLE_DEVICE"

    def test_device_history_request_exactly_100_devices(self):
        """
        Test: Schema acepta exactamente 100 device IDs.
        """
        data = {"device_ids": [f"DEVICE{i}" for i in range(100)]}
        request = DeviceHistoryRequest(**data)

        assert len(request.device_ids) == 100


@pytest.mark.unit
class TestCommunicationResponse:
    """Tests para el schema CommunicationResponse."""

    def test_valid_communication_response(self):
        """
        Test: Schema válido con todos los campos.
        """
        data = {
            "id": 1,
            "device_id": "867564050638581",
            "latitude": Decimal("19.4326"),
            "longitude": Decimal("-99.1332"),
            "speed": Decimal("45.5"),
            "course": Decimal("180.0"),
            "gps_datetime": datetime(2024, 1, 15, 10, 30, 0),
            "main_battery_voltage": Decimal("12.5"),
            "backup_battery_voltage": Decimal("3.7"),
            "odometer": 15000,
            "trip_distance": 500,
            "total_distance": 150000,
            "engine_status": "ON",
            "fix_status": "VALID",
            "alert_type": None,
        }

        response = CommunicationResponse(**data)

        assert response.device_id == "867564050638581"
        assert response.latitude == Decimal("19.4326")
        assert response.speed == Decimal("45.5")

    def test_communication_response_with_null_values(self):
        """
        Test: Schema acepta valores None opcionales.
        """
        data = {
            "id": 1,
            "device_id": "TEST",
            "latitude": None,
            "longitude": None,
            "speed": None,
            "course": None,
            "gps_datetime": None,
        }

        response = CommunicationResponse(**data)

        assert response.device_id == "TEST"
        assert response.latitude is None
        assert response.longitude is None

    def test_communication_response_missing_required_fields(self):
        """
        Test: Schema requiere campos obligatorios.
        """
        data = {"latitude": Decimal("19.4326")}  # Falta id y device_id

        with pytest.raises(ValidationError) as exc_info:
            CommunicationResponse(**data)

        errors = exc_info.value.errors()
        missing_fields = {error["loc"][0] for error in errors}

        assert "id" in missing_fields
        assert "device_id" in missing_fields

    def test_communication_response_decimal_precision(self):
        """
        Test: Schema maneja decimales correctamente.
        """
        data = {
            "id": 1,
            "device_id": "TEST",
            "latitude": Decimal("19.432612345"),
            "longitude": Decimal("-99.133245678"),
        }

        response = CommunicationResponse(**data)

        assert isinstance(response.latitude, Decimal)
        assert isinstance(response.longitude, Decimal)
        assert response.latitude == Decimal("19.432612345")

    def test_communication_response_datetime_format(self):
        """
        Test: Schema maneja datetime correctamente.
        """
        data = {
            "id": 1,
            "device_id": "TEST",
            "gps_datetime": datetime(2024, 1, 15, 10, 30, 45),
        }

        response = CommunicationResponse(**data)

        assert isinstance(response.gps_datetime, datetime)
        assert response.gps_datetime.year == 2024
        assert response.gps_datetime.month == 1
        assert response.gps_datetime.day == 15

    def test_communication_response_integer_fields(self):
        """
        Test: Schema valida campos enteros correctamente.
        """
        data = {
            "id": 1,
            "device_id": "TEST",
            "odometer": 15000,
            "trip_distance": 500,
            "total_distance": 150000,
        }

        response = CommunicationResponse(**data)

        assert isinstance(response.odometer, int)
        assert response.odometer == 15000
        assert response.trip_distance == 500

    def test_communication_response_from_orm_model(self):
        """
        Test: Schema puede crear desde modelo ORM (from_attributes=True).
        """
        from app.models.communications import CommunicationSuntech

        # Crear modelo ORM mock
        orm_model = CommunicationSuntech(
            id=1,
            device_id="867564050638581",
            latitude=Decimal("19.4326"),
            longitude=Decimal("-99.1332"),
            speed=Decimal("45.5"),
        )

        # Crear schema desde ORM
        response = CommunicationResponse.model_validate(orm_model)

        assert response.id == 1
        assert response.device_id == "867564050638581"
        assert response.latitude == Decimal("19.4326")
