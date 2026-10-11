import re


def detect_terraform_resource(diff):
    """
    Detect the Terraform resource affected by a Git diff.

    Example:
    resource "azurerm_resource_group" "infra"

    Returns:
        azurerm_resource_group.infra
    """

    resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'

    matches = re.findall(resource_pattern, diff)

    if not matches:
        return None

    resource_type, resource_name = matches[0]

    return f"{resource_type}.{resource_name}"


if __name__ == "__main__":
    sample_diff = """
    +resource "azurerm_resource_group" "infra" {
    +  name     = "infratrace-rg"
    +  location = "Central India"
    +}
    """

    resource = detect_terraform_resource(sample_diff)

    print("Detected Terraform resource:")
    print(resource)
    