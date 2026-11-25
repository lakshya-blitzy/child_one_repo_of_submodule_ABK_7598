# Child One — Customer Orders API

A small FastAPI service for registration, authentication, catalogue management and order fulfilment.

## Run
`pip install -r requirements.txt`
`uvicorn app.main:app --host 127.0.0.1 --port 8000`

## Existing tests
`pytest -q`

## Deliberate analysis gaps
The suite exercises individual routes through FastAPI TestClient. It does not yet prove a real HTTP customer purchase journey from a separately running service, nor a browser/storefront journey. Important untested behaviour includes invalid login, duplicate registration, stock decrement and computed order totals across the complete workflow.
