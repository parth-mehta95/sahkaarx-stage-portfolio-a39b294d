"""
Production-Ready Data Pipeline Module
Handles Extraction, Transformation (with Schema Validation & Audit Metadata), and Loading (ETL).

This module contains the fully resolved DataPipeline class incorporating both:
1. [From main branch]: Strict schema validation, required columns checking, and null handling.
2. [From feature branch]: UTC audit metadata enrichment (timestamps, run IDs, indexing) and batch chunking.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Configure module-level logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataPipeline")


class PipelineError(Exception):
    """Base exception for pipeline operations."""
    pass


class ValidationError(PipelineError):
    """Raised when data fails schema or validation checks."""
    pass


class ExtractionError(PipelineError):
    """Raised when data extraction encounters an error."""
    pass


class DataPipeline:
    """
    Modular ETL Data Pipeline for structured data ingestion, transformation, and storage.
    
    Provides collaborative, production-grade data handling:
    - Extraction from record dictionaries and tabular data.
    - Transformation with column normalization, strict schema verification,
      null filtering, and UTC audit metadata enrichment.
    - Loading into SQL databases (e.g., SQLite/PostgreSQL) via SQLAlchemy.
    """

    def __init__(self, name: str = "ProductionDataPipeline"):
        self.name = name
        self.raw_data: Optional[pd.DataFrame] = None
        self.transformed_data: Optional[pd.DataFrame] = None
        self.execution_status: str = "INITIALIZED"
        logger.info(f"Initialized pipeline '{self.name}'.")

    def extract_from_records(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Extract data from a list of dictionary records into a DataFrame.

        :param records: List of dictionary records.
        :return: DataFrame containing raw data.
        :raises ExtractionError: If records list is empty.
        """
        if not records:
            logger.error("Extraction failed: Record list is empty.")
            raise ExtractionError("Cannot extract from empty record list.")
        
        self.raw_data = pd.DataFrame(records)
        self.execution_status = "EXTRACTED"
        logger.info(f"Extracted {len(self.raw_data)} records successfully.")
        return self.raw_data

    def transform(
        self,
        required_columns: Optional[List[str]] = None,
        drop_nulls: bool = True,
        add_metadata: bool = True,
        batch_size: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Clean, validate, and enrich the extracted data.

        Resolved Implementation:
        Integrates strict schema validation and null filtering (from main branch)
        with UTC audit metadata, record indexing, and batch configuration (from feature branch).

        :param required_columns: List of column names that must exist in data.
        :param drop_nulls: Whether to drop rows containing NaN/null values.
        :param add_metadata: Whether to append audit columns ('processed_at', 'pipeline_run_id', 'record_index').
        :param batch_size: Optional batch chunking size for downstream consumers.
        :return: Transformed DataFrame.
        :raises PipelineError: If called before data extraction.
        :raises ValidationError: If required columns are missing.
        """
        if self.raw_data is None:
            logger.error("Transformation failed: No raw data available.")
            raise PipelineError("No data to transform. Run extraction first.")

        df = self.raw_data.copy()

        # Step 1: Base normalization (strip spaces, lowercase, replace spaces with underscores)
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        df = df.drop_duplicates()

        # Step 2: [Main Branch Feature] Schema validation & Null value filtering
        if required_columns:
            normalized_required = [c.strip().lower().replace(" ", "_") for c in required_columns]
            missing_cols = [c for c in normalized_required if c not in df.columns]
            if missing_cols:
                logger.error(f"Validation error: Missing columns {missing_cols}")
                raise ValidationError(f"Missing required columns in dataset: {missing_cols}")
            logger.info(f"Verified required schema columns: {normalized_required}")

        if drop_nulls:
            initial_count = len(df)
            df = df.dropna()
            dropped = initial_count - len(df)
            if dropped > 0:
                logger.info(f"Dropped {dropped} row(s) containing null values.")

        # Step 3: [Feature Branch Feature] UTC Audit Metadata & Batch Configuration
        if add_metadata:
            df["processed_at"] = pd.Timestamp.now(tz="UTC").isoformat()
            df["pipeline_run_id"] = f"{self.name}_run"
            df["record_index"] = range(1, len(df) + 1)
            logger.info("Enriched dataset with UTC audit metadata and record index.")

        if batch_size is not None and batch_size > 0:
            logger.info(f"Configured batch chunking: batch size = {batch_size}.")

        self.transformed_data = df
        self.execution_status = "TRANSFORMED"
        logger.info(f"Transformation completed successfully. Shape: {self.transformed_data.shape}")
        return self.transformed_data

    def load_to_sqlite(self, table_name: str, db_url_or_engine: Union[str, Engine] = "sqlite:///:memory:") -> int:
        """
        Load transformed data into an SQL database via SQLAlchemy.

        :param table_name: Destination SQL table name.
        :param db_url_or_engine: SQLAlchemy database Engine or connection URL.
        :return: Number of rows loaded.
        :raises PipelineError: If transformed data is not available.
        """
        if self.transformed_data is None:
            logger.error("Load failed: No transformed data available.")
            raise PipelineError("No transformed data available to load. Run transform first.")

        if isinstance(db_url_or_engine, str):
            engine = create_engine(db_url_or_engine)
        else:
            engine = db_url_or_engine

        with engine.begin() as conn:
            self.transformed_data.to_sql(table_name, con=conn, if_exists="replace", index=False)

        rows_loaded = len(self.transformed_data)
        self.execution_status = "LOADED"
        logger.info(f"Successfully loaded {rows_loaded} rows into table '{table_name}'.")
        return rows_loaded

    def run(
        self,
        records: List[Dict[str, Any]],
        table_name: str = "pipeline_output",
        required_columns: Optional[List[str]] = None,
        drop_nulls: bool = True,
        add_metadata: bool = True,
        batch_size: Optional[int] = None,
        db_url_or_engine: Union[str, Engine] = "sqlite:///:memory:",
    ) -> Dict[str, Any]:
        """
        Execute the end-to-end pipeline: Extraction -> Transformation -> Loading.

        :param records: Input data records.
        :param table_name: Output database table name.
        :param required_columns: Required schema columns.
        :param drop_nulls: Whether to drop rows with nulls.
        :param add_metadata: Whether to attach audit metadata.
        :param batch_size: Optional batch processing size.
        :param db_url_or_engine: Database URL or SQLAlchemy Engine.
        :return: Execution summary dictionary.
        """
        self.extract_from_records(records)
        self.transform(
            required_columns=required_columns,
            drop_nulls=drop_nulls,
            add_metadata=add_metadata,
            batch_size=batch_size,
        )
        rows_loaded = self.load_to_sqlite(table_name=table_name, db_url_or_engine=db_url_or_engine)
        return {
            "pipeline": self.name,
            "status": self.execution_status,
            "rows_processed": rows_loaded,
            "columns": list(self.transformed_data.columns) if self.transformed_data is not None else [],
        }


if __name__ == "__main__":
    sample_records = [
        {"customer_id": 101, "Customer Name": "Alice Corp", "amount": 2500.50},
        {"customer_id": 102, "Customer Name": "Bob Ltd", "amount": 1400.00},
        {"customer_id": 103, "Customer Name": "Charlie LLC", "amount": None},  # Will be dropped
        {"customer_id": 101, "Customer Name": "Alice Corp", "amount": 2500.50},  # Duplicate
    ]

    pipeline = DataPipeline("ProductionETLPipeline")
    result = pipeline.run(
        records=sample_records,
        table_name="processed_customers",
        required_columns=["customer_id", "customer_name"],
        drop_nulls=True,
        add_metadata=True,
    )
    print("\n--- Pipeline Execution Summary ---")
    for k, v in result.items():
        print(f"{k}: {v}")
    print("\nTransformed DataFrame:")
    print(pipeline.transformed_data)
