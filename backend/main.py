from fastapi import FastAPI
from backend.database import get_connection

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Welcome to InfraTrace"
    }


@app.get("/resources/{resource_id}/history")
def get_resource_history(resource_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.id,
            r.name,
            r.type,
            r.provider,
            r.environment,
            r.owner,
            c.commit_id,
            c.author,
            c.change_description,
            c.timestamp
        FROM resources r
        LEFT JOIN resource_changes c
            ON r.id = c.resource_id
        WHERE r.id = %s
        ORDER BY c.timestamp DESC;
    """, (resource_id,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return {
            "message": "Resource not found"
        }

    resource = rows[0]

    return {
        "resource": {
            "id": resource[0],
            "name": resource[1],
            "type": resource[2],
            "provider": resource[3],
            "environment": resource[4],
            "owner": resource[5]
        },
        "history": [
            {
                "commit_id": row[6],
                "author": row[7],
                "change_description": row[8],
                "timestamp": row[9]
            }
            for row in rows
            if row[6] is not None
        ]
    }