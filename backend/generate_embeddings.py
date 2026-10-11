from sentence_transformers import SentenceTransformer
from database import get_connection


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings():

    connection = get_connection()
    cursor = connection.cursor()

    # Get contexts that don't have embeddings yet
    cursor.execute("""
        SELECT id, content
        FROM resource_context
        WHERE embedding IS NULL;
    """)

    rows = cursor.fetchall()

    print(f"Found {len(rows)} contexts without embeddings.")

    for row in rows:

        context_id = row[0]
        content = row[1]

        # Generate 384-dimensional embedding
        embedding = model.encode(content)

        # Convert numpy array to PostgreSQL vector format
        embedding_string = "[" + ",".join(
            str(float(value))
            for value in embedding
        ) + "]"

        cursor.execute("""
            UPDATE resource_context
            SET embedding = %s
            WHERE id = %s;
        """, (
            embedding_string,
            context_id
        ))

        print(f"Generated embedding for context {context_id}")

    connection.commit()

    cursor.close()
    connection.close()

    print("All embeddings generated successfully!")


if __name__ == "__main__":
    generate_embeddings()