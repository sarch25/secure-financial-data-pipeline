# Secure Financial Data Pipeline

A standalone, sanitized Python portfolio demonstration of authenticated event ingestion, validation, deduplication, review decisions, SQLite persistence, and audit history. Uses fictional data and **does not execute trades**.

This is a new educational implementation inspired by general engineering patterns used in cloud-hosted applications, **not** a copy of a production trading system.

## Architecture

Synthetic event → Flask API (API key + validation) → SQLite event record → approval/rejection → audit history

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PIPELINE_API_KEY = "replace-with-a-long-random-value"
python app.py
```

In a second PowerShell terminal, from the repository directory:

```powershell
$headers = @{ "X-API-Key" = "replace-with-a-long-random-value" }
$event = Get-Content .\examples\sample_event.json -Raw
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/events -Headers $headers -ContentType application/json -Body $event
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/events/demo-001/decision -Headers $headers -ContentType application/json -Body '{"decision":"approved"}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/events/demo-001/audit -Headers $headers
```

The same `event_id` cannot be submitted twice. Repeated demo runs should use a new `event_id` or delete the local database while the app is stopped.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Docker

```powershell
docker build -t secure-financial-data-pipeline .
docker volume create financial-events-data
docker run --rm -p 127.0.0.1:5000:5000 -e PIPELINE_API_KEY="replace-with-a-long-random-value" -v financial-events-data:/data secure-financial-data-pipeline
```

The container runs as a non-root user. Data is stored in a named Docker volume.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health response (no authentication) |
| POST | `/events` | Validate and ingest event |
| GET | `/events/<event_id>` | Retrieve event |
| POST | `/events/<event_id>/decision` | Approve or reject pending event |
| GET | `/events/<event_id>/audit` | View event audit history |

All routes except `/health` require the `X-API-Key` header.

## Security and scope

This is a local demo, not a production-ready service. Use HTTPS, managed secrets, request size limits, rate limiting, observability, and a robust identity/authorization system before considering public deployment. API keys in example commands are placeholders. The approval operation is a workflow status change only, not an instruction to any broker.
