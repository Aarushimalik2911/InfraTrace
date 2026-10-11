from database import get_connection
from git_reader import get_git_history
from git_files import get_changed_files


def sync_commit_files():

    connection = get_connection()
    cursor = connection.cursor()

    history = get_git_history()

    total_files = 0

    for commit in history:

        commit_id = commit["commit_id"]

        files = get_changed_files(commit_id)

        for file_path in files:

            cursor.execute("""
                INSERT INTO commit_files
                (commit_id, file_path)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                commit_id,
                file_path
            ))

            total_files += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Synced {total_files} changed files successfully!")


if __name__ == "__main__":
    sync_commit_files()