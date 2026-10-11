
from fastapi.testclient import TestClient
import backend.main as main

client = TestClient(main.app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to InfraTrace"


def test_azure_resources_endpoint(monkeypatch):
    # Mock Azure CLI so this test does not depend on a live Azure account.
    monkeypatch.setattr(
        main,
        "get_azure_resources",
        lambda: [
            {
                "name": "NetworkWatcher_centralindia",
                "type": "Microsoft.Network/networkWatchers",
                "location": "centralindia",
                "resourceGroup": "NetworkWatcherRG",
                "provisioningState": "Succeeded",
            }
        ],
    )

    response = client.get("/azure-resources")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["resources"][0]["name"] == (
        "NetworkWatcher_centralindia"
    )


def test_azure_sync_endpoint(monkeypatch):
    # Mock the sync function to avoid writing to your database.
    monkeypatch.setattr(
        main,
        "sync_azure_resources",
        lambda: None,
    )

    response = client.post("/azure-resources/sync")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Azure resources synced successfully."
    )


def test_terraform_azure_comparison_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "compare_resources",
        lambda: {
            "terraform_count": 1,
            "azure_count": 2,
            "matched": 0,
            "missing_in_azure": 1,
            "azure_only": 2,
        },
    )

    response = client.get("/terraform-azure-comparison")

    assert response.status_code == 200
    data = response.json()
    assert data["terraform_count"] == 1
    assert data["azure_count"] == 2


def test_ask_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_answer",
        lambda question: {
            "answer": "Two Azure resources were found in the test data.",
            "sources": [],
        },
    )

    response = client.get(
        "/ask",
        params={"question": "What Azure resources are available?"},
    )

    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"]

