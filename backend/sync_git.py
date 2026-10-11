from database import get_connection
from git_reader import get_git_history


def sync_git_history():

    connection = get_connection()
    cursor = connection.cursor()

    history = get_git_history()

    for commit in history:

        cursor.execute("""
            INSERT INTO resource_changes
            (resource_id, commit_id, author, change_description, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            1,
            commit["commit_id"],
            commit["author"],
            commit["message"],
            commit["date"]
        ))

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Synced {len(history)} Git commits successfully!")


if __name__ == "__main__":
    sync_git_history()