from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CommunicationBase:
    """
    Base común con todos los campos compartidos entre Suntech y Queclink.
    Si en el futuro agregas un tercer fabricante, solo heredas esta clase.
    """

    device_id = Column(String, index=True)
    backup_battery_voltage = Column(Numeric)
    course = Column(Numeric)
    delivery_type = Column(String)
    engine_status = Column(String)
    fix_status = Column(String)
    gps_datetime = Column(DateTime)
    gps_epoch = Column(BigInteger)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    main_battery_voltage = Column(Numeric)
    msg_class = Column(String)
    network_status = Column(String)
    odometer = Column(BigInteger)
    rx_lvl = Column(Integer)
    speed = Column(Numeric)
    total_distance = Column(BigInteger)
    trip_distance = Column(BigInteger)
    trip_hourmeter = Column(Integer)
    received_epoch = Column(BigInteger)
    received_at = Column(DateTime)
    created_at = Column(DateTime)
    alert_type = Column(String)


class CommunicationSuntech(Base, CommunicationBase):
    """
    Tabla para los registros provenientes de dispositivos Suntech.
    """

    __tablename__ = "communications_suntech"

    id = Column(Integer, primary_key=True, index=True)


class CommunicationQueclink(Base, CommunicationBase):
    """
    Tabla para los registros provenientes de dispositivos Queclink.
    """

    __tablename__ = "communications_queclink"

    id = Column(Integer, primary_key=True, index=True)


class CommunicationCurrentState(Base):
    """
    Tabla para el estado actual (última comunicación) de los dispositivos.

    Esta tabla materializada contiene la comunicación más reciente de cada dispositivo,
    optimizada para consultas rápidas de estado actual.

    Nota: device_id es la clave primaria (no existe campo id).
    """

    __tablename__ = "communications_current_state"

    # Primary Key
    device_id = Column(String, primary_key=True, index=True)

    # Campos del estado actual
    backup_battery_voltage = Column(Numeric)
    course = Column(Numeric)
    delivery_type = Column(String)
    engine_status = Column(String)
    fix_status = Column(String)
    gps_datetime = Column(DateTime)
    gps_epoch = Column(BigInteger)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    main_battery_voltage = Column(Numeric)
    msg_class = Column(String)
    network_status = Column(String)
    odometer = Column(BigInteger)
    rx_lvl = Column(Integer)
    satellites = Column(Integer)
    speed = Column(Numeric)
    received_epoch = Column(BigInteger)
    received_at = Column(DateTime)
