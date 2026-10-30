# MP2: Data Processing REST API

This project is a FastAPI application that wraps the data-cleaning pipeline from MP1 in a REST API. Users can upload a CSV file with `POST /upload`, which stores it in memory and returns its metadata; retrieve stored rows with `GET /datasets/{id}` (with an optional `limit`); and validate and clean a dataset with `POST /datasets/{id}/process`, which accepts a JSON configuration for required and numeric columns, duplicate removal, missing-value handling, and outlier removal, then returns a cleaning report. `GET /health` reports the API's status. Every request is logged with a unique request ID, status code, and duration, and the ID is returned in the `X-Request-ID` header. Tests are written with pytest and FastAPI's TestClient.

## Running

    python -m pip install -r requirements.txt
    python -m uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs.

## Testing

    python -m pytest tests -v