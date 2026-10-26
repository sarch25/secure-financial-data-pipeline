# Secure Financial Data Ingestion Pipeline & Execution Gateway

A hardened, event-driven Python architecture demonstrating secure API authentication, strict data schema validation, idempotency controls, and cryptographic audit logging. This repository serves as a sanitized architectural blueprint modeled directly after real-world multi-market (Stocks, Futures, Options) automated trading ingestion layers.

**Core Technical Stack:** Python · Flask · SQLite · Docker (Non-Root Execution) · PowerShell CLI · REST APIs

## Architectural Framework & Data Flow

```text
[ Secure Upstream Client ] 
           |
     HTTP POST Request (Enforced TLS-Ready)
     Headers: X-API-Key (Cryptographic Authentication)
           |
           v
  [ Flask Ingress API ]
           |
           +---> [ Cryptographic Key Validation ]
           +---> [ Input Schema Enforcement & Injection Defense ]
           +---> [ Idempotency Check / Duplicate ID Prevention ]
           |
           v
  [ Hardened SQLite Database ] ---> Enforced Database Isolation Layer
           |
           v
  [ Post-Ingestion Workflow ] ---> State Machine: Evaluation / Approval / Rejection
           |
           v
  [ Immutable Audit History Logs ] ---> Forensic Event Replays & Logging
```

The gateway exposes a highly secure REST interface engineered to receive high-throughput financial telemetry events. It natively enforces strict boundary controls to prevent duplicate event ingestion, ensures transaction atomicity within SQLite, and logs a tamper-evident audit history of all post-ingestion workflow decisions.

## Verified Security & Infrastructure Controls

*   **Cryptographic API Ingress Protection:** Enforces strict API token validation via standard `X-API-Key` request headers, completely dropping unauthenticated external packets before hitting internal pipeline components.
*   **Idempotency & Replay Attack Defense:** Implements an enforced state validation layer that automatically rejects repeated event IDs, mitigating duplicate order routing and network-level replay vectors.
*   **Data Integrity & Injection Mitigation:** Utilizes robust parameterization and strict schema enforcement prior to database commit operations, preventing SQL injection (SQLi) and data corruption.
*   **Principle of Least Privilege Containerization:** The accompanying Docker runtime is explicitly configured to drop superuser capabilities, executing exclusively as a **non-root user**.
*   **Host-Level Network Segmentation:** Containerized network mapping binds the application daemon strictly to the local loopback interface (`127.0.0.1`), entirely reducing the external network attack surface.
*   **Persistent Storage Security:** Enforces detached Docker named volumes to maintain transactional records and historical audit trails across container destruction and deployment cycles.

## Testing, Validation & Verification Lifecycle

The application framework undergoes a rigorous local sandbox testing lifecycle to verify architectural resiliency. 

**Completed Operational Verification:**
*   **Unit & Integration Testing:** Automated test suites successfully passed, validating critical state transitions.
*   **Idempotency Reinforcement:** Confirmed absolute rejection of duplicated real-time event signatures.
*   **State Persistence Audit:** Verified full data integrity and SQLite retention following hard restarts of the container runtime.

To execute the automated unit-test suite locally, invoke the following command:
```powershell
python -m unittest discover -s tests -v
```

## Quick Start Deployment Guide (Windows PowerShell)

### 1. Local Environment Provisioning
Initialize an isolated Python virtual environment, activate the runtime environment, and deploy project dependencies:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Runtime Configuration & Gateway Initiation
Generate a secure, dynamic runtime token and execute the primary API gateway daemon:
```powershell
\$env:PIPELINE_API_KEY = [guid]::NewGuid().ToString("N")
python app.py
```

### 3. Ingress Pipeline Verification
Open a secondary administrative terminal, map the active access token, and transmit a sample data payload:
```powershell
\$headers = @{ "X-API-Key" = "your-generated-api-key-here" }
\$event = Get-Content .\examples\sample_event.json -Raw

Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:5000/events `
    -Headers \$headers `
    -ContentType application/json `
    -Body \$event
```
*Note: To validate the integrated idempotency layers, resubmitting the identical token or payload will trigger an immediate, automated rejection protocol.*

## Containerized Production Deployment (Docker)

To containerize the pipeline using a hardened host configuration, execute the following commands:

```powershell
# 1. Build the production application layer
docker build -t secure-financial-data-pipeline .

# 2. Provision isolated persistent data volumes
docker volume create financial-events-data

# 3. Instantiate the non-root container with loopback binding boundaries
docker run --rm `
    -p 127.0.0.1:5000:5000 `
    -e PIPELINE_API_KEY="generate-high-entropy-production-key-here" `
    -v financial-events-data:/data `
    secure-financial-data-pipeline
```

## API Reference Directory

| HTTP Method | Route Endpoint | Tactical Ingress Purpose | Security Access Tier |
| :--- | :--- | :--- | :---: |
| **GET** | `/health` | Core Application Resiliency & Health Check | Open (Unauthenticated) |
| **POST** | `/events` | Validate, Sanitize, and Ingest Real-Time Events | Enforced `X-API-Key` |
| **GET** | `/events/<id>` | Secure Retrieval of a Historic Stored Record | Enforced `X-API-Key` |
| **POST** | `/events/<id>/decision` | Execute State Decisions (Approve/Reject Workflow) | Enforced `X-API-Key` |
| **GET** | `/events/<id>/audit` | Forensic Audit Log Retrieval for Targeted IDs | Enforced `X-API-Key` |

## Scope, Limitations & Production Hardening Roadmap

This project is a sanitized, standalone architectural blueprint designed to illustrate robust software engineering and security controls; it does not connect to a live public brokerage execution desk. 

**Planned Security Roadmap Integrations:**
*   **Transport Layer Security:** Enforcing absolute edge-termination of HTTPS/TLS 1.3 to mitigate sniffing.
*   **Rate Limiting & Throttling:** Deploying Nginx or Flask-Limiter controls to stop API abuse and Denial of Service (DoS).
*   **Enterprise Identity Management:** Transitioning from static API keys to asymmetric cryptographic signatures or temporary JWT/OAuth2 authentication tokens.
*   **Centralized SIEM Aggregation:** Offloading structured application event logs to cloud-native monitoring suites (e.g., Microsoft Sentinel Azure) for forensic tracking.

