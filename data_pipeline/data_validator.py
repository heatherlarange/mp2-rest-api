import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.
    
    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be
    numeric."""
    # Check that every required column exists
    for col in required_columns:
        if col not in df.columns:
            logger.error("Missing required column: %s", col)
            raise ValueError(f"Missing required column: {col}")

    rows_before = len(df)
    df = df.copy()  # avoid modifying the caller's DataFrame

    for col in numeric_columns:
        if col not in df.columns:
            logger.warning("Numeric column not found: %s", col)
            continue

        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid numeric value in column '%s' at row %s: %r",
                        col, i, value,
                    )
                    invalid_rows.append(i)

        # Remove the invalid rows
        df = df.drop(index=invalid_rows)

        # Convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

    rows_after = len(df)
    logger.debug(
        "Validation complete: %d valid rows, %d rows removed",
        rows_after, rows_before - rows_after,
    )
    return df
