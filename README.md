# InfraTrace — Cloud Infrastructure History & Context Platform

InfraTrace is a Python-based cloud infrastructure investigation platform that combines Azure resource discovery, Terraform configuration analysis, Git change history, PostgreSQL storage, and Retrieval-Augmented Generation (RAG).

It helps developers and cloud engineers investigate infrastructure changes and retrieve relevant technical context from a single interface.

## Problem Statement

Infrastructure information is often scattered across configuration files, version-control history, cloud consoles, and documentation. This makes it difficult to understand what changed, what currently exists in the cloud, and why a configuration may differ from deployed resources.

InfraTrace brings these sources together to improve infrastructure visibility and troubleshooting.

## Key Features

- **Azure Resource Discovery:** Fetches existing Azure resources using Azure CLI.
- **Resource Synchronization:** Stores and updates Azure resource snapshots in PostgreSQL.
- **Terraform Analysis:** Extracts infrastructure resource definitions from Terraform files.
- **Terraform–Azure Comparison:** Compares declared infrastructure with resources discovered in Azure.
- **Git Change History:** Tracks infrastructure-related file changes using repository history.
- **RAG-Based Q&A:** Retrieves relevant context using vector embeddings and generates answers with a locally running language model.
- **REST API:** Exposes core functionality through FastAPI.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Database | PostgreSQL |
| Vector Search | pgvector |
| Embeddings | Sentence Transformers |
| Language Model | Ollama with Llama 3.2 |
| Cloud Integration | Azure CLI |
| Infrastructure as Code | Terraform |
| Version Control | Git |
| Frontend | HTML, CSS, JavaScript |

## Architecture

1. Azure CLI retrieves existing Azure resources.
2. Terraform files describe the intended infrastructure configuration.
3. Git history provides context about configuration changes.
4. PostgreSQL stores resource metadata, history, and retrieved context.
5. Sentence Transformers creates embeddings for semantic retrieval.
6. pgvector finds relevant context for a user question.
7. The local language model generates a response using the retrieved evidence.
8. FastAPI exposes the functionality to the frontend dashboard.

## Running Locally

### Prerequisites

- Python
- PostgreSQL with the pgvector extension
- Azure CLI authenticated to an Azure subscription
- Git
- Ollama with the required language model downloaded

### Start the Backend

Activate your Python virtual environment and install the dependencies from the project's dependency file, if available.

```powershell
uvicorn backend.main:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

### Start the Frontend

In a separate terminal, run:

```powershell
python -m http.server 5500 --directory frontend
```

Open:

http://127.0.0.1:5500

## Security and Cost Considerations

- Azure integration reads existing resources; it does not automatically deploy infrastructure.
- Keep database passwords and credentials in environment variables.
- Never commit `.env`, credentials, access tokens, or private keys.
- Review cloud costs before deploying additional resources.

## Current Limitations

- Terraform configuration and deployed Azure infrastructure may differ.
- Resource matching can require more sophisticated identity and configuration comparison.
- RAG answer quality depends on the available indexed context and retrieved evidence.
- Production deployment would require additional authentication, authorization, monitoring, and security hardening.

## Future Improvements

- Automated testing and continuous integration with GitHub Actions.
- Improved infrastructure drift detection.
- More detailed Terraform plan and state analysis.
- Better source citations and confidence indicators for RAG responses.
- Role-based access control and production monitoring.

## Project Goal

InfraTrace aims to make cloud infrastructure changes easier to understand by combining cloud inventory, infrastructure configuration, version history, and contextual question-answering in one platform.