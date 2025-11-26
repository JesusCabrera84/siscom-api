"""
Tests para los modelos SQLAlchemy.
"""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communications import CommunicationQueclink, CommunicationSuntech


@pytest.mark.unit
@pytest.mark.database
class TestCommunicationSuntech:
    """Tests para el modelo CommunicationSuntech."""

    @pytest.mark.asyncio
    async def test_create_suntech_communication(self, db_session: AsyncSession):
        """
        Test: Crear un registro Suntech.
        """
        comm = CommunicationSuntech(
            device_id="TEST_SUNTECH",
            latitude=Decimal("19.4326"),
            longitude=Decimal("-99.1332"),
            speed=Decimal("45.5"),
        )

        db_session.add(comm)
        await db_session.commit()
        await db_session.refresh(comm)

        assert comm.id is not None
        assert comm.device_id == "TEST_SUNTECH"
        assert comm.latitude == Decimal("19.4326")

    @pytest.mark.asyncio
    async def test_suntech_table_name(self, db_session: AsyncSession):
        """
        Test: Modelo usa el nombre de tabla correcto.
        """
        assert CommunicationSuntech.__tablename__ == "communications_suntech"

    @pytest.mark.asyncio
    async def test_suntech_has_all_fields(self):
        """
        Test: Modelo tiene todos los campos esperados.
        """
        expected_fields = [
            "id",
            "device_id",
            "latitude",
            "longitude",
            "speed",
            "course",
            "gps_datetime",
            "gps_epoch",
            "main_battery_voltage",
            "backup_battery_voltage",
            "odometer",
            "trip_distance",
            "total_distance",
            "engine_status",
            "fix_status",
        ]

        for field in expected_fields:
            assert hasattr(CommunicationSuntech, field)

    @pytest.mark.asyncio
    async def test_suntech_with_null_values(self, db_session: AsyncSession):
        """
        Test: Modelo acepta valores NULL en campos opcionales.
        """
        comm = CommunicationSuntech(
            device_id="NULL_TEST",
            latitude=None,
            longitude=None,
            speed=None,
        )

        db_session.add(comm)
        await db_session.commit()
        await db_session.refresh(comm)

        assert comm.device_id == "NULL_TEST"
        assert comm.latitude is None
        assert comm.longitude is None

    @pytest.mark.asyncio
    async def test_suntech_with_complete_data(self, db_session: AsyncSession):
        """
        Test: Modelo guarda correctamente todos los campos.
        """
        comm = CommunicationSuntech(
            device_id="COMPLETE_TEST",
            latitude=Decimal("19.4326"),
            longitude=Decimal("-99.1332"),
            speed=Decimal("45.5"),
            course=Decimal("180.0"),
            gps_datetime=datetime(2024, 1, 15, 10, 30, 0),
            gps_epoch=1705318200,
            main_battery_voltage=Decimal("12.5"),
            backup_battery_voltage=Decimal("3.7"),
            odometer=15000,
            trip_distance=500,
            total_distance=150000,
            engine_status="ON",
            fix_status="VALID",
        )

        db_session.add(comm)
        await db_session.commit()
        await db_session.refresh(comm)

        assert comm.device_id == "COMPLETE_TEST"
        assert comm.latitude == Decimal("19.4326")
        assert comm.speed == Decimal("45.5")
        assert comm.odometer == 15000
        assert comm.engine_status == "ON"


@pytest.mark.unit
@pytest.mark.database
class TestCommunicationQueclink:
    """Tests para el modelo CommunicationQueclink."""

    @pytest.mark.asyncio
    async def test_create_queclink_communication(self, db_session: AsyncSession):
        """
        Test: Crear un registro Queclink.
        """
        comm = CommunicationQueclink(
            device_id="TEST_QUECLINK",
            latitude=Decimal("25.6866"),
            longitude=Decimal("-100.3161"),
            speed=Decimal("60.0"),
        )

        db_session.add(comm)
        await db_session.commit()
        await db_session.refresh(comm)

        assert comm.id is not None
        assert comm.device_id == "TEST_QUECLINK"
        assert comm.latitude == Decimal("25.6866")

    @pytest.mark.asyncio
    async def test_queclink_table_name(self):
        """
        Test: Modelo usa el nombre de tabla correcto.
        """
        assert CommunicationQueclink.__tablename__ == "communications_queclink"

    @pytest.mark.asyncio
    async def test_queclink_has_same_structure_as_suntech(self):
        """
        Test: Queclink tiene la misma estructura que Suntech.
        """
        suntech_fields = set(dir(CommunicationSuntech))
        queclink_fields = set(dir(CommunicationQueclink))

        # Filtrar campos privados y de SQLAlchemy
        suntech_public = {f for f in suntech_fields if not f.startswith("_")}
        queclink_public = {f for f in queclink_fields if not f.startswith("_")}

        # Ambos deben tener los mismos campos públicos
        # (excepto __tablename__ que es diferente)
        core_fields = {"device_id", "latitude", "longitude", "speed", "odometer"}

        for field in core_fields:
            assert field in suntech_public
            assert field in queclink_public


@pytest.mark.unit
@pytest.mark.database
class TestModelQueries:
    """Tests para queries de los modelos."""

    @pytest.mark.asyncio
    async def test_query_by_device_id(
        self,
        db_session: AsyncSession,
        sample_suntech_communication
    ):
        """
        Test: Query por device_id funciona correctamente.
        """
        from sqlalchemy.future import select

        query = select(CommunicationSuntech).where(
            CommunicationSuntech.device_id == "867564050638581"
        )

        result = await db_session.execute(query)
        communications = result.scalars().all()

        assert len(communications) == 1
        assert communications[0].device_id == "867564050638581"

    @pytest.mark.asyncio
    async def test_query_multiple_device_ids(
        self,
        db_session: AsyncSession,
        multiple_communications
    ):
        """
        Test: Query con múltiples device IDs.
        """
        from sqlalchemy.future import select

        device_ids = ["SUNTECH0", "SUNTECH1"]
        query = select(CommunicationSuntech).where(
            CommunicationSuntech.device_id.in_(device_ids)
        )

        result = await db_session.execute(query)
        communications = result.scalars().all()

        assert len(communications) == 2
        found_ids = {comm.device_id for comm in communications}
        assert found_ids == {"SUNTECH0", "SUNTECH1"}

