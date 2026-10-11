from sentence_transformers import SentenceTransformer
from database import get_connection


model = SentenceTransformer("all-MiniLM-L6-v2")


def search_context(question, limit=5):

    # Convert question into embedding
    question_embedding = model.encode(question)

    embedding_string = "[" + ",".join(
        str(float(value))
        for value in question_embedding
    ) + "]"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            resource_id,
            context_type,
            content,
            embedding <=> %s::vector AS distance
        FROM resource_context
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (
        embedding_string,
        embedding_string,
        limit
    ))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


if __name__ == "__main__":

    question = "Why was the Azure infrastructure changed?"

    results = search_context(question)

    for result in results:

        print("=" * 70)

        print("Context ID:", result[0])
        print("Resource ID:", result[1])
        print("Context Type:", result[2])
        print("Distance:", result[4])

        print("\nContext:")
        print(result[3])