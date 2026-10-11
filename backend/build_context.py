from database import get_connection


def build_context():

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # 1. Clear existing contexts
    # ---------------------------------------------------------

    cursor.execute("""
        DELETE FROM resource_context;
    """)

    # ---------------------------------------------------------
    # 2. Build context for Terraform resources
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            resource_type,
            resource_name,
            provider,
            file_path,
            tags,
            configuration
        FROM infrastructure_resources
        ORDER BY id;
    """)

    resources = cursor.fetchall()

    resource_count = 0
    git_context_count = 0
    azure_context_count = 0

    for resource in resources:

        (
            resource_id,
            resource_type,
            resource_name,
            provider,
            file_path,
            tags,
            configuration
        ) = resource

        tags_text = ""

        if tags:

            if isinstance(tags, dict):

                tags_text = "\n".join(
                    f"{key}: {value}"
                    for key, value in tags.items()
                )

            else:

                tags_text = str(tags)

        content = f"""
Infrastructure Resource

Resource ID:
{resource_id}

Resource Type:
{resource_type}

Resource Name:
{resource_name}

Provider:
{provider}

Terraform File:
{file_path}

Tags:
{tags_text}

Terraform Configuration:
{configuration}
"""

        cursor.execute("""
            INSERT INTO resource_context
            (
                resource_id,
                context_type,
                content
            )
            VALUES (%s, %s, %s);
        """, (
            resource_id,
            "resource",
            content
        ))

        resource_count += 1

    # ---------------------------------------------------------
    # 3. Build Git change context
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            ic.id,
            ic.resource_id,
            ic.commit_id,
            rc.author,
            rc.timestamp,
            ic.file_path,
            ic.change_type,
            rc.change_description,
            ic.diff_content,
            ic.terraform_resource_name
        FROM infrastructure_changes ic

        LEFT JOIN resource_changes rc
            ON ic.commit_id = rc.commit_id

        WHERE ic.resource_id IS NOT NULL

        ORDER BY rc.timestamp DESC;
    """)

    changes = cursor.fetchall()

    for change in changes:

        (
            change_id,
            resource_id,
            commit_id,
            author,
            timestamp,
            file_path,
            change_type,
            description,
            diff_content,
            terraform_resource_name
        ) = change

        content = f"""
Infrastructure Change

Terraform Resource:
{terraform_resource_name}

Resource ID:
{resource_id}

Git Commit:
{commit_id}

Author:
{author}

Date:
{timestamp}

Changed File:
{file_path}

Change Type:
{change_type}

Change Description:
{description}

Git Diff:
{diff_content}
"""

        cursor.execute("""
            INSERT INTO resource_context
            (
                resource_id,
                context_type,
                content
            )
            VALUES (%s, %s, %s);
        """, (
            resource_id,
            "git",
            content
        ))

        git_context_count += 1

    # ---------------------------------------------------------
    # 4. Build context for Azure resources
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            azure_resource_id,
            name,
            resource_type,
            resource_group,
            location,
            provisioning_state
        FROM azure_resources
        ORDER BY id;
    """)

    azure_resources = cursor.fetchall()

    for azure_resource in azure_resources:

        (
            azure_id,
            azure_resource_id,
            name,
            resource_type,
            resource_group,
            location,
            provisioning_state
        ) = azure_resource

        content = f"""
Azure Resource

Azure Resource ID:
{azure_resource_id}

Resource Name:
{name}

Resource Type:
{resource_type}

Resource Group:
{resource_group}

Location:
{location}

Provisioning State:
{provisioning_state}
"""

        cursor.execute("""
            INSERT INTO resource_context
            (
                resource_id,
                context_type,
                content
            )
            VALUES (%s, %s, %s);
        """, (
            None,
            "azure",
            content
        ))

        azure_context_count += 1

    # ---------------------------------------------------------
    # 5. Save everything
    # ---------------------------------------------------------

    connection.commit()

    cursor.close()
    connection.close()

    print("Context building completed successfully!")
    print(f"Resource contexts created: {resource_count}")
    print(f"Git contexts created: {git_context_count}")
    print(f"Azure contexts created: {azure_context_count}")


if __name__ == "__main__":
    build_context()