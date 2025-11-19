#!/usr/bin/env python3
"""
Debug script to check document chunks in the database
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def main():
    database_url = os.getenv('DATABASE_URL')
    print(f"Database URL: {database_url}")

    # Use asyncpg driver
    if database_url and database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check for chunks with specific document_id
        doc_id = '5f6c07df-6c78-45be-97a0-50de8e1f272e'
        print(f"\n=== Checking chunks for document {doc_id} ===")

        result = await session.execute(
            text("""
                SELECT id, document_id, user_id, chunk_index,
                       LENGTH(chunk_text) as text_length,
                       embedding IS NOT NULL as has_embedding
                FROM document_chunks
                WHERE document_id = :doc_id
            """),
            {"doc_id": doc_id}
        )
        chunks = result.fetchall()

        if not chunks:
            print(f"❌ No chunks found for document {doc_id}")

            # Check all chunks
            print("\n=== Checking all chunks in database ===")
            result = await session.execute(
                text("""
                    SELECT id, document_id, user_id, chunk_index,
                           LENGTH(chunk_text) as text_length,
                           embedding IS NOT NULL as has_embedding
                    FROM document_chunks
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
            )
            all_chunks = result.fetchall()
            for chunk in all_chunks:
                print(f"  ID: {chunk[0][:8]}... | Doc: {chunk[1][:8]}... | User: {chunk[2][:8]}... | "
                      f"Index: {chunk[3]} | Text len: {chunk[4]} | Has embedding: {chunk[5]}")
        else:
            print(f"✅ Found {len(chunks)} chunk(s):")
            for chunk in chunks:
                print(f"  ID: {chunk[0]}")
                print(f"  Document ID: {chunk[1]}")
                print(f"  User ID: {chunk[2]}")
                print(f"  Chunk Index: {chunk[3]}")
                print(f"  Text Length: {chunk[4]}")
                print(f"  Has Embedding: {chunk[5]}")
                print()

        # Check the document itself
        print(f"\n=== Checking document record ===")
        result = await session.execute(
            text("""
                SELECT id, user_id, filename, status, processed_at
                FROM documents
                WHERE id = :doc_id
            """),
            {"doc_id": doc_id}
        )
        doc = result.fetchone()
        if doc:
            print(f"  ID: {doc[0]}")
            print(f"  User ID: {doc[1]}")
            print(f"  Filename: {doc[2]}")
            print(f"  Status: {doc[3]}")
            print(f"  Processed at: {doc[4]}")
        else:
            print(f"❌ Document {doc_id} not found in documents table")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
