"""
Unit tests for production DataPipeline module.
Verifies base operations, branch-specific enhancements, conflict resolution integration, and database loading.
"""

import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from pipeline import DataPipeline, PipelineError, ValidationError, ExtractionError


@pytest.fixture
def sample_records():
    """Provides a realistic set of records with duplicates and missing values."""
    return [
        {"Record ID": 1, "User Name": "Alice", "score": 95.5},
        {"Record ID": 2, "User Name": "Bob", "score": None},       # Null value row
        {"Record ID": 3, "User Name": "Charlie", "score": 82.0},
        {"Record ID": 1, "User Name": "Alice", "score": 95.5},       # Duplicate row
    ]


def test_pipeline_initialization():
    """Verify default pipeline initialization and status."""
    pipe = DataPipeline("TestPipeline")
    assert pipe.name == "TestPipeline"
    assert pipe.raw_data is None
    assert pipe.transformed_data is None
    assert pipe.execution_status == "INITIALIZED"


def test_extraction_empty_records_raises_error():
    """Extraction must raise ExtractionError if given an empty record set."""
    pipe = DataPipeline()
    with pytest.raises(ExtractionError, match="Cannot extract from empty record list"):
        pipe.extract_from_records([])


def test_extraction_valid_records(sample_records):
    """Valid records must be loaded into raw_data DataFrame."""
    pipe = DataPipeline()
    df = pipe.extract_from_records(sample_records)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4
    assert pipe.execution_status == "EXTRACTED"


def test_transform_unextracted_raises_error():
    """Transforming before extraction must raise PipelineError."""
    pipe = DataPipeline()
    with pytest.raises(PipelineError, match="No data to transform"):
        pipe.transform()


def test_main_branch_schema_validation(sample_records):
    """Main branch requirement: Verify required schema columns exist."""
    pipe = DataPipeline()
    pipe.extract_from_records(sample_records)

    # Valid schema validation passes
    transformed = pipe.transform(required_columns=["record_id", "user_name"])
    assert "record_id" in transformed.columns
    assert "user_name" in transformed.columns

    # Missing column raises ValidationError
    with pytest.raises(ValidationError, match="Missing required columns in dataset"):
        pipe.transform(required_columns=["missing_column"])


def test_main_branch_drop_nulls(sample_records):
    """Main branch requirement: Drop rows with null values."""
    pipe = DataPipeline()
    pipe.extract_from_records(sample_records)

    # With drop_nulls=True, the row with score=None must be dropped
    transformed = pipe.transform(drop_nulls=True, add_metadata=False)
    assert len(transformed) == 2  # 4 rows -> 1 duplicate dropped, 1 null dropped = 2 rows
    assert transformed["score"].isna().sum() == 0

    # With drop_nulls=False, null rows are kept
    transformed_keep = pipe.transform(drop_nulls=False, add_metadata=False)
    assert len(transformed_keep) == 3


def test_feature_branch_audit_metadata(sample_records):
    """Feature branch requirement: Enriched audit columns added to records."""
    pipe = DataPipeline("AuditPipeline")
    pipe.extract_from_records(sample_records)

    transformed = pipe.transform(add_metadata=True, drop_nulls=False)
    assert "processed_at" in transformed.columns
    assert "pipeline_run_id" in transformed.columns
    assert "record_index" in transformed.columns
    assert (transformed["pipeline_run_id"] == "AuditPipeline_run").all()
    assert list(transformed["record_index"]) == [1, 2, 3]


def test_feature_branch_batch_configuration(sample_records):
    """Feature branch requirement: Support batch size parameter."""
    pipe = DataPipeline()
    pipe.extract_from_records(sample_records)
    transformed = pipe.transform(batch_size=10)
    assert isinstance(transformed, pd.DataFrame)


def test_combined_resolved_transform(sample_records):
    """
    Conflict Resolution Verification:
    Both teammate's validation/cleaning (main) AND feature audit metadata (feature branch)
    execute harmoniously in the resolved method.
    """
    pipe = DataPipeline("MergedPipeline")
    pipe.extract_from_records(sample_records)

    transformed = pipe.transform(
        required_columns=["record_id", "score"],
        drop_nulls=True,
        add_metadata=True,
        batch_size=25,
    )

    # Main branch features verified:
    assert len(transformed) == 2
    assert "record_id" in transformed.columns
    assert "score" in transformed.columns
    assert transformed["score"].isna().sum() == 0

    # Feature branch features verified:
    assert "processed_at" in transformed.columns
    assert "pipeline_run_id" in transformed.columns
    assert "record_index" in transformed.columns
    assert list(transformed["record_index"]) == [1, 2]


def test_load_to_sqlite(sample_records):
    """Verify SQL loading via SQLAlchemy into in-memory SQLite database."""
    pipe = DataPipeline("SQLLoadPipeline")
    pipe.extract_from_records(sample_records)
    pipe.transform(drop_nulls=True, add_metadata=True)

    engine = create_engine("sqlite:///:memory:")
    rows = pipe.load_to_sqlite("users_table", db_url_or_engine=engine)
    assert rows == 2
    assert pipe.execution_status == "LOADED"

    # Query back using the same engine connection pool to verify persistence
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users_table")).scalar()
        assert result == 2


def test_load_untransformed_raises_error():
    """Loading before transforming must raise PipelineError."""
    pipe = DataPipeline()
    with pytest.raises(PipelineError, match="No transformed data available"):
        pipe.load_to_sqlite("dummy_table")


def test_end_to_end_run_workflow(sample_records):
    """Verify complete end-to-end pipeline run method."""
    pipe = DataPipeline("EndToEndPipeline")
    summary = pipe.run(
        records=sample_records,
        table_name="final_output",
        required_columns=["record_id", "user_name"],
        drop_nulls=True,
        add_metadata=True,
    )

    assert summary["pipeline"] == "EndToEndPipeline"
    assert summary["status"] == "LOADED"
    assert summary["rows_processed"] == 2
    assert "processed_at" in summary["columns"]
    assert "pipeline_run_id" in summary["columns"]
