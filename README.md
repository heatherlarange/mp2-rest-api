# MP2: Data Processing REST API

My API combines the MP1 data-cleaning pipeline in a FastAPI application. By uploading a raw CSV, the API stores it in memory, and you can then clean it by sending a JSON configuration. That configuration works like MP1's YAML file. The API validates and cleans the stored dataset, replaces it with the cleaned version and returns a cleaning report. Data moves through it in a particular order. `POST /upload` checks that the file has a `.csv` extension, parses it with pandas, and returns 400 if the file is empty, cannot be parsed, or is not UTF-8. A valid file gets a new integer ID, and the response is its metadata. `POST /datasets/{id}/process` checks the config against a Pydantic model, confirms that the dataset exists and has the numeric columns listed, then validates and cleans the data and saves the result back under the same ID. `GET /datasets/{id}` returns the stored rows, with an optional `limit` that defaults to 100, plus the total row count. `GET /health` reports the API's status and version.

The `data_pipeline` package is the MP1 code reused without changes. data_validator.py checks that all required columns are present, removes rows whose numeric columns have non-numeric values, and converts those columns to a numeric type. data_processor.py applies the cleaning steps turned on in the config: it removes duplicate rows, drops rows or columns with missing values, removes outliers using the IQR or z-score method, and builds the cleaning report. The `src` package holds the API-specific code. models.py defines the Pydantic models for requests and responses, and every config field has a default, so an empty `{}` body is valid. storage.py is an in-memory store that hands out increasing IDs and returns copies of each DataFrame, so a request can never change stored data by accident. middleware.py logs every request with a unique request ID, method, path, status code and duration. It also returns that ID in the `X-Request-ID` header and turns unhandled exceptions into a 500 response. utils.py sets up logging.


To run:

    python -m pip install -r requirements.txt
    python -m uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs to try the endpoints in the browser.


To test:

    python -m pytest tests -v



Example Input:

    curl -X POST http://127.0.0.1:8000/upload -F "file=@fixtures/sample_data.csv"

    curl -X POST http://127.0.0.1:8000/datasets/1/process -H "Content-Type: application/json" -d '{"validation": {"required_columns": ["student_id", "score"], "numeric_columns": ["score"]}, "processing": {"remove_duplicates": true, "missing": {"enabled": true, "axis": "rows"}, "outliers": {"enabled": false, "columns": [], "method": "iqr", "threshold": 1.5}}}'

    curl "http://127.0.0.1:8000/datasets/1?limit=5"


Example Output:

    18:45:27 DEBUG    src.storage - Stored dataset: id=1, rows=6
    18:45:27 INFO     main - Uploaded dataset: id=1, filename=sample_data.csv, rows=6
    18:45:27 DEBUG    src.storage - Retrieved metadata: id=1
    18:45:27 INFO     src.middleware - request_id=9d26d948 POST /upload status=200 duration=5.7ms
    18:45:27 DEBUG    src.storage - Retrieved dataset copy: id=1, rows=6
    18:45:27 WARNING  data_pipeline.data_validator - Invalid numeric value in column 'score' at row 4: 'unknown'
    18:45:27 DEBUG    data_pipeline.data_validator - Validation complete: 5 valid rows, 1 rows removed
    18:45:27 INFO     main - Validated dataset: id=1, rows 6 → 5
    18:45:27 DEBUG    data_pipeline.data_processor - remove_duplicates: 5 -> 4 rows
    18:45:27 DEBUG    data_pipeline.data_processor - handle_missing: 4 -> 3 rows
    18:45:27 DEBUG    src.storage - Updated dataset: id=1, rows=3
    18:45:27 INFO     main - Processed dataset: id=1, validation_removed=1, rows_before=5, rows_after=3
    18:45:27 INFO     src.middleware - request_id=44fa6fbd POST /datasets/1/process status=200 duration=8.5ms
    18:45:27 DEBUG    src.storage - Retrieved dataset copy: id=1, rows=3
    18:45:27 INFO     main - Retrieved dataset: id=1, returned_rows=3
    18:45:27 INFO     src.middleware - request_id=476625f3 GET /datasets/1 status=200 duration=3.5ms

Upload response:

    {"id": 1, "filename": "sample_data.csv", "rows": 6, "columns": 2, "column_names": ["student_id", "score"]}

Process response:

    {"id": 1,
     "validation_rows_removed": 1,
     "cleaning_report": {"rows_before": 5,
                         "rows_after": 3,
                         "rows_removed": 2,
                         "columns_before": 2,
                         "columns_after": 2,
                         "columns_removed": 0}}

Retrieve response:

    {"id": 1,
     "data": [{"student_id": 1, "score": 80.0},
              {"student_id": 2, "score": 90.0},
              {"student_id": 5, "score": 85.0}],
     "total_rows": 3}
