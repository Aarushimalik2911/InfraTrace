
from backend.database import get_connection
from backend.azure_reader import get_azure_resources


def sync_azure_resources():
    # Read existing resources from Azure using Azure CLI
    resources = get_azure_resources()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for resource in resources:
            cursor.execute("""
                INSERT INTO azure_resources (
                    azure_resource_id,
                    name,
                    resource_type,
                    resource_group,
                    location,
                    provisioning_state,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (azure_resource_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    resource_type = EXCLUDED.resource_type,
                    resource_group = EXCLUDED.resource_group,
                    location = EXCLUDED.location,
                    provisioning_state = EXCLUDED.provisioning_state,
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                resource.get("id"),
                resource.get("name"),
                resource.get("type"),
                resource.get("resourceGroup"),
                resource.get("location"),
                resource.get("provisioningState")
            ))

        connection.commit()
        cursor.close()

        print(f"Synced {len(resources)} Azure resources successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    sync_azure_resources()
