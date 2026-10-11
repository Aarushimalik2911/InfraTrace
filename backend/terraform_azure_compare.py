
from backend.database import get_connection


def compare_resources():
    connection = get_connection()
    cursor = connection.cursor()

    # Get Terraform resources
    cursor.execute("""
        SELECT
            id,
            resource_type,
            resource_name,
            provider,
            file_path
        FROM infrastructure_resources
        ORDER BY id;
    """)
    terraform_resources = cursor.fetchall()

    # Get existing Azure resources
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

    cursor.close()
    connection.close()

    comparison = []
    matched = 0
    missing_in_azure = 0
    azure_only = 0
    matched_azure_ids = set()

    # Compare Terraform resource definitions with Azure
    for terraform in terraform_resources:
        terraform_id = terraform[0]
        terraform_type = terraform[1]
        terraform_name = terraform[2]
        provider = terraform[3]
        file_path = terraform[4]

        matched_azure = None

        # Current demo contains an Azure resource group definition
        if terraform_type == "azurerm_resource_group":
            expected_name = "infratrace-rg"

            for azure in azure_resources:
                azure_id = azure[0]
                azure_name = azure[2]
                azure_type = azure[3]

                if (
                    azure_type == "Microsoft.Resources/resourceGroups"
                    and azure_name == expected_name
                ):
                    matched_azure = azure
                    matched_azure_ids.add(azure_id)
                    break

        terraform_info = {
            "id": terraform_id,
            "resource_type": terraform_type,
            "resource_name": terraform_name,
            "provider": provider,
            "file_path": file_path
        }

        if matched_azure:
            matched += 1
            comparison.append({
                "terraform": terraform_info,
                "status": "MATCHED",
                "azure": {
                    "id": matched_azure[0],
                    "resource_id": matched_azure[1],
                    "name": matched_azure[2],
                    "resource_type": matched_azure[3],
                    "resource_group": matched_azure[4],
                    "location": matched_azure[5],
                    "provisioning_state": matched_azure[6]
                }
            })
        else:
            missing_in_azure += 1
            comparison.append({
                "terraform": terraform_info,
                "status": "NOT_FOUND_IN_AZURE"
            })

    # Find Azure resources not matched to Terraform
    for azure in azure_resources:
        if azure[0] in matched_azure_ids:
            continue

        azure_only += 1
        comparison.append({
            "terraform": None,
            "status": "AZURE_RESOURCE_NOT_IN_TERRAFORM",
            "azure": {
                "id": azure[0],
                "resource_id": azure[1],
                "name": azure[2],
                "resource_type": azure[3],
                "resource_group": azure[4],
                "location": azure[5],
                "provisioning_state": azure[6]
            }
        })

    return {
        "summary": {
            "terraform_resources": len(terraform_resources),
            "azure_resources": len(azure_resources),
            "matched": matched,
            "missing_in_azure": missing_in_azure,
            "azure_only": azure_only
        },
        "comparison": comparison
    }


if __name__ == "__main__":
    print(compare_resources())
