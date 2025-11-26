import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test-ana"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # CONFIRMAR base seleccionada
        res = await conn.execute(text("SELECT current_database(), current_schema()"))
        print("\n>>> DB / SCHEMA:", res.fetchall(), "\n")

        # ¿Cuántas filas tiene la tabla?
        res = await conn.execute(text("SELECT COUNT(*) FROM communications_current_state"))
        print(">>> COUNT:", res.scalar(), "\n")

        # ¿Qué device_id existen?
        res = await conn.execute(text("""
            SELECT DISTINCT device_id
            FROM communications_current_state
            ORDER BY device_id
            LIMIT 10
        """))
        print(">>> DISTINCT DEVICE IDs:", res.fetchall(), "\n")

        # ¿Están tus 3 devices?
        res = await conn.execute(text("""
            SELECT device_id, latitude, longitude, received_at
            FROM communications_current_state
            WHERE device_id IN ('0848063597','867564050638581','0848086072')
            ORDER BY received_at DESC
        """))
        print(">>> TUS 3 IDs:", res.fetchall(), "\n")

    await engine.dispose()

asyncio.run(main())
