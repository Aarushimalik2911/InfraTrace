from database import get_connection
from git_reader import get_git_history
from git_files import get_changed_files
from git_diff import get_file_diff
from terraform_resource_detector import detect_terraform_resource


def detect_change_type(diff):
    """
    Detect whether a file was created, deleted, or modified.
    """

    if "new file mode" in diff:
        return "created"

    if "deleted file mode" in diff:
        return "deleted"

    return "modified"


def sync_diffs():
    connection = get_connection()
    cursor = connection.cursor()

    history = get_git_history()

    total_files = 0
    terraform_resources_found = 0

    for commit in history:

        commit_id = commit["commit_id"]

        files = get_changed_files(commit_id)

        for file_path in files:

            # Get only this file's diff
            diff = get_file_diff(
                commit_id,
                file_path
            )

            # Detect change type
            change_type = detect_change_type(diff)

            terraform_resource_name = None

            # Detect Terraform resource only for Terraform files
            if file_path.endswith(".tf"):

                terraform_resource_name = detect_terraform_resource(
                    diff
                )

            # Insert change into database
            cursor.execute("""
                INSERT INTO infrastructure_changes
                (
                    commit_id,
                    file_path,
                    change_type,
                    old_value,
                    new_value,
                    diff_content,
                    terraform_resource_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                commit_id,
                file_path,
                change_type,
                None,
                None,
                diff,
                terraform_resource_name
            ))

            total_files += 1

            if terraform_resource_name:

                terraform_resources_found += 1

                print(
                    f"Detected resource: "
                    f"{terraform_resource_name} "
                    f"| Change: {change_type} "
                    f"| File: {file_path}"
                )

    connection.commit()

    cursor.close()
    connection.close()

    print()
    print(
        f"Synced {total_files} file changes successfully!"
    )

    print(
        f"Terraform resources detected: "
        f"{terraform_resources_found}"
    )


if __name__ == "__main__":
    sync_diffs()