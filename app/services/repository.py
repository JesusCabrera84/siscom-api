from sqlalchemy.future import select

from app.models.communications import CommunicationQueclink, CommunicationSuntech


async def get_communications(session, device_ids: list[str]):
    query_suntech = select(CommunicationSuntech).where(
        CommunicationSuntech.device_id.in_(device_ids)
    )
    query_queclink = select(CommunicationQueclink).where(
        CommunicationQueclink.device_id.in_(device_ids)
    )

    suntech = (await session.execute(query_suntech)).scalars().all()
    queclink = (await session.execute(query_queclink)).scalars().all()

    return suntech + queclink
