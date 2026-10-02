resource "azurerm_resource_group" "infra" {
  name     = "infratrace-rg"
  location = "Central India"

  tags = {
    environment = "development"
    owner       = "Aarushi"
    project     = "InfraTrace"
  }
}