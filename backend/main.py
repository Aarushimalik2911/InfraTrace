from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_connection
from backend.resource_history import (
    get_resource_history as get_infrastructure_history
)
from backend.rag import generate_answer
from backend.azure_reader import get_azure_resources
from backend.sync_azure import sync_azure_resources
from backend.terraform_azure_compare import compare_resources


app = FastAPI(title="InfraTrace API")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to InfraTrace"
    }


# ---------------------------------------------------------
# Infrastructure Resource History
# ---------------------------------------------------------

@app.get("/infrastructure-resources/{resource_id}/history")
def infrastructure_resource_history(resource_id: int):
    history = get_infrastructure_history(resource_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Infrastructure resource not found"
        )

    return history


# ---------------------------------------------------------
# Live Azure Resources
# ---------------------------------------------------------

@app.get("/azure-resources")
def azure_resources():
    resources = get_azure_resources()

    return {
        "count": len(resources),
        "resources": [
            {
                "name": resource.get("name"),
                "type": resource.get("type"),
                "location": resource.get("location"),
                "resource_group": resource.get("resourceGroup"),
                "provisioning_state": resource.get(
                    "provisioningState"
                )
            }
            for resource in resources
        ]
    }


# ---------------------------------------------------------
# Basic Resource History
# ---------------------------------------------------------

@app.get("/resources/{resource_id}/history")
def resource_history(resource_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                r.id,
                r.name,
                r.type,
                r.provider,
                r.environment,
                r.owner,
                c.commit_id,
                c.author,
                c.change_description,
                c.timestamp
            FROM resources r
            LEFT JOIN resource_changes c
                ON r.id = c.resource_id
            WHERE r.id = %s
            ORDER BY c.timestamp DESC;
        """, (resource_id,))

        rows = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    resource = rows[0]

    return {
        "resource": {
            "id": resource[0],
            "name": resource[1],
            "type": resource[2],
            "provider": resource[3],
            "environment": resource[4],
            "owner": resource[5]
        },
        "history": [
            {
                "commit_id": row[6],
                "author": row[7],
                "change_description": row[8],
                "timestamp": row[9]
            }
            for row in rows
            if row[6] is not None
        ]
    }


# ---------------------------------------------------------
# Infrastructure Resources
# ---------------------------------------------------------

@app.get("/infrastructure-resources")
def get_infrastructure_resources():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                resource_type,
                resource_name,
                provider,
                file_path,
                tags
            FROM infrastructure_resources
            ORDER BY id;
        """)

        rows = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    return {
        "count": len(rows),
        "resources": [
            {
                "id": row[0],
                "resource_type": row[1],
                "resource_name": row[2],
                "provider": row[3],
                "file_path": row[4],
                "tags": row[5]
            }
            for row in rows
        ]
    }


# ---------------------------------------------------------
# RAG Question Answering
# ---------------------------------------------------------

@app.get("/ask")
def ask_infratrace(question: str):
    return generate_answer(question)


# ---------------------------------------------------------
# Terraform ↔ Azure Comparison
# ---------------------------------------------------------

@app.get("/terraform-azure-comparison")
def terraform_azure_comparison():
    return compare_resources()


# ---------------------------------------------------------
# Stored Azure Resource Details
# ---------------------------------------------------------

@app.get("/azure-resources/stored")
def get_stored_azure_resources():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                azure_resource_id,
                name,
                resource_type,
                resource_group,
                location,
                provisioning_state,
                updated_at
            FROM azure_resources
            ORDER BY name;
        """)

        rows = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    return {
        "count": len(rows),
        "resources": [
            {
                "id": row[0],
                "azure_resource_id": row[1],
                "name": row[2],
                "resource_type": row[3],
                "resource_group": row[4],
                "location": row[5],
                "provisioning_state": row[6],
                "last_synced": row[7]
            }
            for row in rows
        ]
    }


# ---------------------------------------------------------
# Sync Azure Resources
# ---------------------------------------------------------

@app.post("/azure-resources/sync")
def sync_azure_resources_endpoint():
    try:
        sync_azure_resources()

        return {
            "message": "Azure resources synced successfully."
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Azure resource sync failed: {exc}"
        ) from exc
