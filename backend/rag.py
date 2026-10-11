
from sentence_transformers import SentenceTransformer
from backend.database import get_connection
import requests


# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def search_context(question, limit=5):

    # Convert question into an embedding
    question_embedding = embedding_model.encode(question)

    # Convert embedding to PostgreSQL vector format
    embedding_string = "[" + ",".join(
        str(float(value))
        for value in question_embedding
    ) + "]"

    # Connect to PostgreSQL
    connection = get_connection()
    cursor = connection.cursor()

    # Find the most relevant contexts
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


def generate_answer(question):

    # Step 1: Retrieve relevant contexts
    results = search_context(question, limit=5)

    if not results:
        return {
            "question": question,
            "answer": "I could not find any relevant infrastructure information.",
            "sources": []
        }

    # Step 2: Build context for the LLM
    context_parts = []

    for result in results:

        context_id = result[0]
        resource_id = result[1]
        context_type = result[2]
        content = result[3]
        distance = result[4]

        context_parts.append(
            f"""
Context ID: {context_id}
Resource ID: {resource_id}
Context Type: {context_type}
Similarity Distance: {distance}

Evidence:
{content}
"""
        )

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Create the prompt
    prompt = f"""
You are InfraTrace, an AI assistant for investigating cloud infrastructure.

Your job is to answer the user's question using ONLY the infrastructure
evidence provided below.

STRICT RULES:

1. Never invent or assume facts.
2. Never say that a value changed unless the Git diff explicitly shows
   the old value and the new value.
3. If the diff says "new file mode", describe the resource as CREATED.
4. If the diff says "deleted file mode", describe the resource as DELETED.
5. If the diff shows old and new lines, describe the specific modification.
6. If the evidence does not contain enough information, say:
   "I could not find enough information in InfraTrace."
7. Always mention the relevant:
   - Terraform resource
   - Git commit
   - author
   - changed file
   - change type
   when available.
8. Do not confuse a Git/configuration change with an actual Azure deployment.
   If the evidence only shows Terraform code, say that the Terraform
   configuration changed. Do NOT claim that Azure itself was deployed or
   modified.
9. Keep the answer concise and factual.
10. Separate the conclusion from the supporting evidence.

USER QUESTION:
{question}

INFRASTRUCTURE EVIDENCE:
{context}

Answer using ONLY the evidence above.
"""
    # Step 4: Send prompt to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    # Step 5: Get generated answer
    answer = response.json()["response"]

    # Step 6: Return answer and evidence
    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "context_id": result[0],
                "resource_id": result[1],
                "context_type": result[2],
                "distance": round(float(result[4]), 4),
                "evidence": result[3]
            }
            for result in results
        ]
    }


if __name__ == "__main__":

    question = "Why was the Azure infrastructure changed?"

    result = generate_answer(question)

    print("=" * 70)
    print("QUESTION")
    print("=" * 70)
    print(result["question"])

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print(
            f"Context ID: {source['context_id']} | "
            f"Resource ID: {source['resource_id']} | "
            f"Type: {source['context_type']} | "
            f"Distance: {source['distance']}"
        )

        print("Evidence:")
        print(source["evidence"])
        print()

