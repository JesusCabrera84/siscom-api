from sqlalchemy.future import select

from app.models.communications import (
    CommunicationCurrentState,
    CommunicationQueclink,
    CommunicationSuntech,
)


async def get_communications(session, device_ids: list[str]):
    """
    Obtiene el histórico completo de comunicaciones de los dispositivos especificados.

    Args:
        session: Sesión de base de datos
        device_ids: Lista de IDs de dispositivos

    Returns:
        Lista con todas las comunicaciones (Suntech + Queclink)
    """
    query_suntech = select(CommunicationSuntech).where(
        CommunicationSuntech.device_id.in_(device_ids)
    )
    query_queclink = select(CommunicationQueclink).where(
        CommunicationQueclink.device_id.in_(device_ids)
    )

    suntech = (await session.execute(query_suntech)).scalars().all()
    queclink = (await session.execute(query_queclink)).scalars().all()

    return suntech + queclink


async def get_latest_communications(
    session, device_ids: list[str], msg_class: str | None = None
):
    """
    Obtiene la última comunicación registrada de cada dispositivo especificado.

    Consulta la tabla optimizada communications_current_state que contiene
    solo el registro más reciente de cada dispositivo.

    Args:
        session: Sesión de base de datos
        device_ids: Lista de IDs de dispositivos
        msg_class: Filtro opcional por tipo de clase de mensaje (ej: "ALERT", "STATUS")

    Returns:
        Lista con la última comunicación de cada dispositivo solicitado
    """
    query = select(CommunicationCurrentState).where(
        CommunicationCurrentState.device_id.in_(device_ids)
    )

    # Agregar filtro por msg_class si se proporciona
    if msg_class is not None:
        query = query.where(CommunicationCurrentState.msg_class == msg_class)

    result = (await session.execute(query)).scalars().all()
    return result
