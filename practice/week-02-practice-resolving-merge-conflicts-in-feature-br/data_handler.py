"""
DataHandler module.
Demonstrates clean implementation of DataHandler with both teammate's updates and new feature method preserved.
"""
import pandas as pd
from typing import List, Dict, Any, Optional


class DataHandler:
    """
    Handles data ingestion, validation, processing, and export for data pipelines.
    """

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the DataHandler with optional initial records.
        """
        self.data: List[Dict[str, Any]] = data if data is not None else []
        self._df: Optional[pd.DataFrame] = None

    def load_data(self, records: List[Dict[str, Any]]) -> None:
        """
        Load records into the handler.
        """
        if not isinstance(records, list):
            raise TypeError("Records must be provided as a list of dictionaries.")
        self.data = records
        self._df = pd.DataFrame(records) if records else pd.DataFrame()

    # -------------------------------------------------------------------------
    # Teammate's Modification:
    # Enhanced validation and data cleaning logic with stricter type/null checks
    # -------------------------------------------------------------------------
    def validate_and_clean(self, required_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Validate records against required fields, drop nulls, and clean whitespace.
        (Teammate's enhancement to original DataHandler)
        """
        if self._df is None or self._df.empty:
            if self.data:
                self._df = pd.DataFrame(self.data)
            else:
                return pd.DataFrame()

        df = self._df.copy()

        # Check required fields
        if required_fields:
            missing = [field for field in required_fields if field not in df.columns]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
            # Drop rows with null values in required fields
            df = df.dropna(subset=required_fields)

        # Strip whitespace for string columns
        str_cols = df.select_dtypes(include=["object"]).columns
        for col in str_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        self._df = df
        return self._df

    # -------------------------------------------------------------------------
    # Feature Branch Addition:
    # New method to compute summary metrics and aggregate statistics
    # -------------------------------------------------------------------------
    def get_summary_statistics(self, numeric_columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate summary statistics (mean, median, std, min, max, count) for numeric fields.
        (New method added on feature branch)
        """
        if self._df is None or self._df.empty:
            if self.data:
                self._df = pd.DataFrame(self.data)
            else:
                return {}

        df = self._df
        target_cols = numeric_columns if numeric_columns else df.select_dtypes(include=["number"]).columns.tolist()

        stats: Dict[str, Dict[str, float]] = {}
        for col in target_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                series = df[col].dropna()
                if not series.empty:
                    stats[col] = {
                        "count": float(series.count()),
                        "mean": float(series.mean()),
                        "std": float(series.std()) if len(series) > 1 else 0.0,
                        "min": float(series.min()),
                        "median": float(series.median()),
                        "max": float(series.max()),
                    }
        return stats

    # -------------------------------------------------------------------------
    # Additional processing & export methods preserved
    # -------------------------------------------------------------------------
    def filter_by_condition(self, column: str, min_value: Any) -> pd.DataFrame:
        """
        Filter dataset rows where column >= min_value.
        """
        if self._df is None or self._df.empty:
            return pd.DataFrame()
        if column not in self._df.columns:
            raise KeyError(f"Column '{column}' not found.")
        filtered_df = self._df[self._df[column] >= min_value]
        return filtered_df

    def to_dict_records(self) -> List[Dict[str, Any]]:
        """
        Export internal dataframe back to a list of dicts.
        """
        if self._df is None or self._df.empty:
            return []
        return self._df.to_dict(orient="records")

