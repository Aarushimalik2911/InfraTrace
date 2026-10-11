
import json

from database import get_connection
from terraform_parser import parse_terraform_file


def sync_terraform_resources():

    file_path = "infrastructure/terraform/main.tf"

    resources = parse_terraform_file(file_path)

    connection = get_connection()
    cursor = connection.cursor()

    total_resources = 0

    for resource in resources:

        resource_type = resource["resource_type"]
        resource_name = resource["resource_name"]
        configuration = resource["configuration"]
        tags = resource["tags"]

        # Detect cloud provider
        if resource_type.startswith("azurerm_"):
            provider = "Azure"

        elif resource_type.startswith("aws_"):
            provider = "AWS"

        elif resource_type.startswith("google_"):
            provider = "GCP"

        else:
            provider = "Unknown"

        cursor.execute("""
            INSERT INTO infrastructure_resources
            (
                resource_type,
                resource_name,
                provider,
                file_path,
                configuration,
                tags
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (resource_type, resource_name)
            DO UPDATE SET
                provider = EXCLUDED.provider,
                file_path = EXCLUDED.file_path,
                configuration = EXCLUDED.configuration,
                tags = EXCLUDED.tags;
        """, (
            resource_type,
            resource_name,
            provider,
            file_path,
            configuration,
            json.dumps(tags)
        ))

        total_resources += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Synced {total_resources} Terraform resources successfully!")


if __name__ == "__main__":
    sync_terraform_resources()
