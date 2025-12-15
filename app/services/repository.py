from datetime import date

from sqlalchemy import func
from sqlalchemy.future import select

from app.models.communications import (
    CommunicationCurrentState,
    CommunicationQueclink,
    CommunicationSuntech,
)


async def get_communications(
    session, device_ids: list[str], received_at: date | None = None
):
    """
    Obtiene el histórico completo de comunicaciones de los dispositivos especificados.

    Args:
        session: Sesión de base de datos
        device_ids: Lista de IDs de dispositivos
        received_at: Fecha opcional para filtrar por received_at (solo fecha, sin hora)

    Returns:
        Lista con todas las comunicaciones (Suntech + Queclink)
    """
    query_suntech = select(CommunicationSuntech).where(
        CommunicationSuntech.device_id.in_(device_ids)
    )
    query_queclink = select(CommunicationQueclink).where(
        CommunicationQueclink.device_id.in_(device_ids)
    )

    # Si se proporciona received_at, filtrar por esa fecha
    if received_at is not None:
        query_suntech = query_suntech.where(
            func.date(CommunicationSuntech.received_at) == received_at
        )
        query_queclink = query_queclink.where(
            func.date(CommunicationQueclink.received_at) == received_at
        )

    # Ordenar por received_at descendente para obtener los más recientes primero
    query_suntech = query_suntech.order_by(CommunicationSuntech.received_at.desc())
    query_queclink = query_queclink.order_by(CommunicationQueclink.received_at.desc())

    suntech = (await session.execute(query_suntech)).scalars().all()
    queclink = (await session.execute(query_queclink)).scalars().all()

    return suntech + queclink


async def get_latest_communications(
    session, device_ids: list[str], msg_class: str | None = None
):
    """
    Obtiene la última comunicación con coordenadas válidas de cada dispositivo.

    Devuelve un único registro por device_id: el más reciente que tenga
    coordenadas válidas (latitude y longitude no nulos), independientemente
    de la clase de mensaje, a menos que se especifique msg_class.

    Args:
        session: Sesión de base de datos
        device_ids: Lista de IDs de dispositivos
        msg_class: Filtro opcional por tipo de clase de mensaje (ej: "ALERT", "STATUS")

    Returns:
        Lista con la última comunicación con coordenadas válidas de cada dispositivo
    """
    # Crear subconsulta con ROW_NUMBER para obtener el registro más reciente por device_id
    row_number_col = (
        func.row_number()
        .over(
            partition_by=CommunicationCurrentState.device_id,
            order_by=CommunicationCurrentState.received_at.desc(),
        )
        .label("row_num")
    )

    # Seleccionar explícitamente solo las columnas que existen en la tabla física
    subquery = select(
        CommunicationCurrentState.device_id,
        CommunicationCurrentState.backup_battery_voltage,
        CommunicationCurrentState.course,
        CommunicationCurrentState.delivery_type,
        CommunicationCurrentState.engine_status,
        CommunicationCurrentState.fix_status,
        CommunicationCurrentState.gps_datetime,
        CommunicationCurrentState.gps_epoch,
        CommunicationCurrentState.latitude,
        CommunicationCurrentState.longitude,
        CommunicationCurrentState.main_battery_voltage,
        CommunicationCurrentState.msg_class,
        CommunicationCurrentState.network_status,
        CommunicationCurrentState.odometer,
        CommunicationCurrentState.rx_lvl,
        CommunicationCurrentState.satellites,
        CommunicationCurrentState.speed,
        CommunicationCurrentState.received_epoch,
        CommunicationCurrentState.received_at,
        row_number_col,
    ).where(
        CommunicationCurrentState.device_id.in_(device_ids),
        CommunicationCurrentState.latitude.isnot(None),
        CommunicationCurrentState.longitude.isnot(None),
    )

    # Agregar filtro por msg_class si se proporciona
    if msg_class is not None:
        subquery = subquery.where(CommunicationCurrentState.msg_class == msg_class)

    subquery = subquery.subquery()

    # Query final: seleccionar directamente del subquery y filtrar row_num = 1
    query = select(subquery).where(subquery.c.row_num == 1)

    result = await session.execute(query)

    # Reconstruir instancias de CommunicationCurrentState desde el row mapping
    # Excluir row_num que es solo para el filtro
    communications = []
    for row in result:
        row_dict = dict(row._mapping)
        row_dict.pop("row_num", None)  # Eliminar row_num antes de crear la instancia
        communications.append(CommunicationCurrentState(**row_dict))

    return communications
