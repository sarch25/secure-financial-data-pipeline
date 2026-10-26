# Secure Financial Data Pipeline

A standalone Python application demonstrating authenticated event processing, workflow management, persistent data storage, and audit logging.

The project uses fictional financial events to demonstrate engineering patterns used in event-driven applications. It does not execute trades or contain proprietary trading strategies.

**Technologies:** Python · Flask · REST API · SQLite · Docker · PowerShell

## Architecture at a glance

```text
        Synthetic Event
               |
               v
       Flask REST API
       API Key Authentication
               |
               v
      Event Validation
      Duplicate Prevention
               |
               v
        SQLite Database
               |
               v
       Workflow Decision
       Approve / Reject
               |
               v
        Audit History
```

The application receives events through an authenticated API, validates incoming data, prevents duplicate event IDs, and stores accepted events in SQLite.

Events can then be reviewed and approved or rejected. Workflow actions are recorded in an audit history.

## Verified implementation

- **API authentication:** API key verification using the `X-API-Key` request header.
- **Event validation:** Incoming event data is checked before storage.
- **Duplicate prevention:** Repeated event IDs are rejected.
- **Workflow management:** Pending events can be approved or rejected.
- **Persistent storage:** SQLite retains event records and audit history.
- **Audit logging:** Event creation and workflow decisions are recorded.
- **Containerization:** Docker image runs the application as a non-root user.
- **Persistent Docker storage:** A named volume preserves SQLite data across container recreation.

## Testing and validation

The application was tested locally on Windows and inside Docker.

**Completed verification:**

- Four automated Python tests passed.
- Flask health endpoint responded successfully.
- Authenticated event ingestion and retrieval succeeded.
- Duplicate event submission was rejected.
- Approval workflow and audit history were verified.
- SQLite records persisted after restarting the Flask application.
- Docker image built successfully.
- Event records were retrieved following Docker container recreation.

Run the automated tests:

```powershell
python -m unittest discover -s tests -v
```

## Quick start (Windows PowerShell)

Create a Python virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure an API key and start the application:

```powershell
$env:PIPELINE_API_KEY = [guid]::NewGuid().ToString("N")
python app.py
```

In a second PowerShell terminal, use the same API key to authenticate requests:

```powershell
$headers = @{ "X-API-Key" = "your-generated-api-key" }

$event = Get-Content .\examples\sample_event.json -Raw

Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:5000/events `
    -Headers $headers `
    -ContentType application/json `
    -Body $event
```

Replace the example API key with the key generated in the first terminal.

Each event must have a unique `event_id`. Repeated demonstrations should use a new event ID.

## Docker deployment

Build the Docker image:

```powershell
docker build -t secure-financial-data-pipeline .
```

Create persistent storage:

```powershell
docker volume create financial-events-data
```

Start the container:

```powershell
docker run --rm `
    -p 127.0.0.1:5000:5000 `
    -e PIPELINE_API_KEY="replace-with-a-long-random-value" `
    -v financial-events-data:/data `
    secure-financial-data-pipeline
```

The container runs as a non-root user. The application port is bound to localhost, and SQLite data is stored in a named Docker volume.

## API reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health check |
| POST | `/events` | Validate and ingest events |
| GET | `/events/<event_id>` | Retrieve a stored event |
| POST | `/events/<event_id>/decision` | Approve or reject an event |
| GET | `/events/<event_id>/audit` | Retrieve event audit history |

All endpoints except `/health` require an `X-API-Key` header.

## Security and scope

The project implements API key authentication, input validation, duplicate prevention, non-root container execution, and localhost-bound Docker networking.

It is an educational demonstration, not a production-ready financial service.

Potential production improvements include HTTPS enforcement, managed secrets, request size limits, rate limiting, centralized monitoring, and more robust identity and authorization controls.

The application uses synthetic data and does not connect to a brokerage or execute financial transactions. It is an independent implementation inspired by general software engineering patterns, not a copy of a production trading system.
