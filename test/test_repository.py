"""
Tests para el módulo de servicios/repository.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.repository import get_communications


@pytest.mark.unit
@pytest.mark.database
class TestGetCommunications:
    """Tests para la función get_communications."""
    
    @pytest.mark.asyncio
    async def test_get_communications_empty_database(
        self,
        db_session: AsyncSession
    ):
        """
        Test: Función retorna lista vacía si no hay datos.
        """
        device_ids = ["NONEXISTENT"]
        result = await get_communications(db_session, device_ids)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_communications_returns_suntech_data(
        self,
        db_session: AsyncSession,
        sample_suntech_communication
    ):
        """
        Test: Función retorna datos de Suntech.
        """
        device_ids = ["867564050638581"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 1
        assert result[0].device_id == "867564050638581"
        assert result[0].__class__.__name__ == "CommunicationSuntech"
    
    @pytest.mark.asyncio
    async def test_get_communications_returns_queclink_data(
        self,
        db_session: AsyncSession,
        sample_queclink_communication
    ):
        """
        Test: Función retorna datos de Queclink.
        """
        device_ids = ["QUECLINK123"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 1
        assert result[0].device_id == "QUECLINK123"
        assert result[0].__class__.__name__ == "CommunicationQueclink"
    
    @pytest.mark.asyncio
    async def test_get_communications_merges_both_tables(
        self,
        db_session: AsyncSession,
        sample_suntech_communication,
        sample_queclink_communication
    ):
        """
        Test: Función mezcla resultados de ambas tablas.
        """
        device_ids = ["867564050638581", "QUECLINK123"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 2
        
        device_id_set = {comm.device_id for comm in result}
        assert "867564050638581" in device_id_set
        assert "QUECLINK123" in device_id_set
    
    @pytest.mark.asyncio
    async def test_get_communications_with_multiple_devices(
        self,
        db_session: AsyncSession,
        multiple_communications
    ):
        """
        Test: Función maneja múltiples device IDs correctamente.
        """
        device_ids = ["SUNTECH0", "SUNTECH1", "QUECLINK0"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 3
        
        device_id_set = {comm.device_id for comm in result}
        assert device_id_set == {"SUNTECH0", "SUNTECH1", "QUECLINK0"}
    
    @pytest.mark.asyncio
    async def test_get_communications_filters_correctly(
        self,
        db_session: AsyncSession,
        multiple_communications
    ):
        """
        Test: Función solo retorna los dispositivos solicitados.
        """
        # Solo pedir SUNTECH0 y SUNTECH1
        device_ids = ["SUNTECH0", "SUNTECH1"]
        result = await get_communications(db_session, device_ids)
        
        # No debe incluir SUNTECH2 ni QUECLINK*
        device_id_set = {comm.device_id for comm in result}
        assert device_id_set == {"SUNTECH0", "SUNTECH1"}
        assert "SUNTECH2" not in device_id_set
        assert "QUECLINK0" not in device_id_set
    
    @pytest.mark.asyncio
    async def test_get_communications_with_single_device(
        self,
        db_session: AsyncSession,
        sample_suntech_communication
    ):
        """
        Test: Función funciona con un solo device ID.
        """
        device_ids = ["867564050638581"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 1
        assert result[0].device_id == "867564050638581"
    
    @pytest.mark.asyncio
    async def test_get_communications_returns_correct_type(
        self,
        db_session: AsyncSession,
        sample_suntech_communication
    ):
        """
        Test: Función retorna objetos SQLAlchemy correctos.
        """
        from app.models.communications import CommunicationSuntech
        
        device_ids = ["867564050638581"]
        result = await get_communications(db_session, device_ids)
        
        assert len(result) == 1
        assert isinstance(result[0], CommunicationSuntech)
        
        # Verificar que tiene los atributos esperados
        assert hasattr(result[0], "id")
        assert hasattr(result[0], "device_id")
        assert hasattr(result[0], "latitude")
        assert hasattr(result[0], "longitude")

