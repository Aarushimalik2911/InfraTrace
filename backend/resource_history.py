from backend.database import get_connection


def get_resource_history(resource_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ir.id,
            ir.resource_type,
            ir.resource_name,
            ir.provider,
            ir.file_path,

            ic.commit_id,
            rc.author,
            rc.change_description,
            rc.timestamp,

            ic.change_type,
            ic.diff_content

        FROM infrastructure_resources ir

        LEFT JOIN infrastructure_changes ic
            ON ir.id = ic.resource_id

        LEFT JOIN resource_changes rc
            ON ic.commit_id = rc.commit_id

        WHERE ir.id = %s

        ORDER BY rc.timestamp DESC;
    """, (resource_id,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return None

    resource = rows[0]

    return {
        "resource": {
            "id": resource[0],
            "resource_type": resource[1],
            "resource_name": resource[2],
            "provider": resource[3],
            "file_path": resource[4]
        },

        "history": [
            {
                "commit_id": row[5],
                "author": row[6],
                "change_description": row[7],
                "timestamp": row[8],
                "change_type": row[9],
                "diff": row[10]
            }
            for row in rows
            if row[5] is not None
        ]
    }