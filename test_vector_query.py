#!/usr/bin/env python3
"""
Test vector similarity search directly
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def main():
    database_url = os.getenv('DATABASE_URL', 'postgresql://docai:docai_local_password@localhost:5432/docai')

    # Use asyncpg driver
    if database_url and database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)

    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        doc_id = '5f6c07df-6c78-45be-97a0-50de8e1f272e'
        user_id = '2d1ac95f-38aa-4f63-b28b-31f961e4b8df'

        print(f"\n=== Testing vector query ===")
        print(f"Document ID: {doc_id}")
        print(f"User ID: {user_id}")

        # First get the actual embedding from the database
        print("\n1. Get existing embedding from database:")
        result = await session.execute(
            text("""
                SELECT id, chunk_text, embedding
                FROM document_chunks
                WHERE document_id = :doc_id AND user_id = :user_id
                LIMIT 1
            """),
            {"doc_id": doc_id, "user_id": user_id}
        )
        row = result.fetchone()
        if row:
            chunk_id = row[0]
            chunk_text = row[1][:100]
            stored_embedding = row[2]  # This should be a list
            print(f"  Chunk ID: {chunk_id}")
            print(f"  Chunk text (first 100 chars): {chunk_text}")
            print(f"  Embedding type: {type(stored_embedding)}")
            print(f"  Embedding length: {len(stored_embedding) if isinstance(stored_embedding, (list, tuple)) else 'N/A'}")

            # Now test the vector similarity search with the SAME embedding
            print("\n2. Test vector similarity search with same embedding:")
            embedding_str = "[" + ",".join(map(str, stored_embedding)) + "]"
            print(f"  Embedding string (first 100 chars): {embedding_str[:100]}...")

            result2 = await session.execute(
                text("""
                    SELECT
                        id,
                        chunk_text,
                        1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                    FROM document_chunks
                    WHERE user_id = :user_id
                    AND document_id = :doc_id
                    AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 5
                """),
                {
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "embedding": embedding_str
                }
            )
            rows = result2.fetchall()
            print(f"  Found {len(rows)} rows")
            for r in rows:
                print(f"    Chunk ID: {r[0][:8]}... | Similarity: {r[2]}")

        else:
            print(f"  ❌ No chunk found for document {doc_id} and user {user_id}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
