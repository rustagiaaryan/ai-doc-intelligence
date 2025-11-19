#!/usr/bin/env python3
"""
One-time migration script to update 'processed' status to 'completed'
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def main():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return

    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Update all documents with status 'processed' to 'completed'
        result = await session.execute(
            text("UPDATE documents SET status = 'completed' WHERE status = 'processed'")
        )
        await session.commit()

        print(f"\n✅ Updated {result.rowcount} documents from 'processed' to 'completed'")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
