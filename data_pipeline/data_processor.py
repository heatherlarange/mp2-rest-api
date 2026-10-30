import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    result = df.drop_duplicates()
    logger.debug("remove_duplicates: %d -> %d rows", before, len(result))
    return result

def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        before = len(df)
        result = df.dropna(axis=0)
        logger.debug("handle_missing: %d -> %d rows", before, len(result))
    elif axis == "columns":
        before = df.shape[1]
        result = df.dropna(axis=1)
        logger.debug("handle_missing: %d -> %d columns", before, result.shape[1])
    else:
        logger.error("Unsupported axis: %s", axis)
        raise ValueError(f"Unsupported axis: {axis}")
    return result

def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df
    for col in columns:
        if col not in result.columns:
            logger.warning("Outlier column not found: %s", col)
            continue
        if not pd.api.types.is_numeric_dtype(result[col]):
            logger.warning("Outlier column is not numeric: %s", col)
            continue

        series = result[col]
        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            is_outlier = (series < lower) | (series > upper)
        else:  # zscore
            std = series.std()
            if std == 0 or pd.isna(std):
                is_outlier = pd.Series(False, index=series.index)
            else:
                z = (series - series.mean()) / std
                is_outlier = z.abs() > threshold
            lower = upper = None

        removed = int(is_outlier.sum())
        result = result[~is_outlier]
        if method == "iqr":
            logger.debug(
                "%s: method=%s, threshold=%s, lower=%s, upper=%s, removed=%d",
                col, method, threshold, lower, upper, removed,
            )
        else:
            logger.debug(
                "%s: method=%s, threshold=%s, removed=%d",
                col, method, threshold, removed,
            )
    return result

def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]

    if processing.get("remove_duplicates", False):
        df = remove_duplicates(df)

    missing = processing.get("missing", {})
    if missing.get("enabled", False):
        df = handle_missing(df, axis=missing["axis"])

    outliers = processing.get("outliers", {})
    if outliers.get("enabled", False):
        df = remove_outliers(
            df,
            columns=outliers["columns"],
            method=outliers["method"],
            threshold=outliers["threshold"],
        )
    return df

def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before, columns_before = df_before.shape
    rows_after, columns_after = df_after.shape
    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }