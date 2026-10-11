import subprocess
import json


AZ_COMMAND = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"


def get_azure_resources():
    """
    Read Azure resources from the currently selected subscription.

    READ-ONLY:
    This function does not create, update, or delete Azure resources.
    """

    result = subprocess.run(
        [
            AZ_COMMAND,
            "resource",
            "list",
            "--output",
            "json"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    resources = json.loads(result.stdout)

    return resources


if __name__ == "__main__":

    resources = get_azure_resources()

    print("=" * 70)
    print("AZURE RESOURCES")
    print("=" * 70)

    print(f"Total resources found: {len(resources)}")

    for resource in resources:

        print()
        print("Name:", resource.get("name"))
        print("Type:", resource.get("type"))
        print("Location:", resource.get("location"))
        print("Resource Group:", resource.get("resourceGroup"))
        print(
            "Provisioning State:",
            resource.get("provisioningState")
        )