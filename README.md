# Child One — Customer Orders API

A small FastAPI service for registration, authentication, catalogue management and order fulfilment.

## Run
`pip install -r requirements.txt`
`uvicorn app.main:app --host 127.0.0.1 --port 8000`

## Existing tests
Unit suite with line coverage:
`python -m pytest tests/unit --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=50`

Whole suite:
`python -m pytest`

## Deliberate analysis gaps
The suite has two layers: a unit suite that drives the seven handlers in process, and `tests/test_routes.py`, which remains the only evidence for the HTTP envelope of status codes produced through request validation and response serialisation. Neither layer proves a real HTTP customer purchase journey from a separately running service, nor a browser/storefront journey.
