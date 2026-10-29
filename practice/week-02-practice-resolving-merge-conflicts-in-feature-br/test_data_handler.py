"""
Unit tests for DataHandler class.
Validates both teammate's modifications and new feature methods work correctly together.
"""
import pytest
import pandas as pd
from data_handler import DataHandler


@pytest.fixture
def sample_records():
    return [
        {"id": 1, "name": "  Alice  ", "score": 85.0, "age": 28},
        {"id": 2, "name": "Bob", "score": 92.5, "age": 34},
        {"id": 3, "name": "Charlie", "score": None, "age": 22},
        {"id": 4, "name": "Diana ", "score": 78.0, "age": 31},
    ]


def test_initialization():
    handler = DataHandler()
    assert handler.data == []
    assert handler.to_dict_records() == []


def test_teammate_modification_validate_and_clean(sample_records):
    """
    Test the teammate's modification: validate_and_clean with required fields and whitespace strip.
    """
    handler = DataHandler(sample_records)
    cleaned_df = handler.validate_and_clean(required_fields=["id", "score"])

    # ID 3 has None for score, should be dropped
    assert len(cleaned_df) == 3
    assert set(cleaned_df["id"]) == {1, 2, 4}

    # Whitespace in name should be stripped
    alice_name = cleaned_df[cleaned_df["id"] == 1]["name"].iloc[0]
    assert alice_name == "Alice"


def test_teammate_modification_missing_required_field(sample_records):
    """
    Ensure validate_and_clean raises ValueError when required field is missing.
    """
    handler = DataHandler(sample_records)
    with pytest.raises(ValueError, match="Missing required fields"):
        handler.validate_and_clean(required_fields=["non_existent_column"])


def test_new_feature_summary_statistics(sample_records):
    """
    Test the new method added in feature branch: get_summary_statistics.
    """
    handler = DataHandler(sample_records)
    handler.load_data(sample_records)
    stats = handler.get_summary_statistics(numeric_columns=["age", "score"])

    assert "age" in stats
    assert stats["age"]["count"] == 4.0
    assert stats["age"]["min"] == 22.0
    assert stats["age"]["max"] == 34.0
    assert stats["age"]["mean"] == (28 + 34 + 22 + 31) / 4.0

    assert "score" in stats
    assert stats["score"]["count"] == 3.0  # None is dropped in stats calculation


def test_both_changes_combined(sample_records):
    """
    Success criteria: verify both teammate's cleaning and feature branch statistics
    coexist and work harmoniously on the same dataset.
    """
    handler = DataHandler(sample_records)
    # 1. Teammate's method cleans data
    cleaned_df = handler.validate_and_clean(required_fields=["score"])
    assert len(cleaned_df) == 3

    # 2. Feature method computes summary on cleaned data
    stats = handler.get_summary_statistics(["score"])
    assert stats["score"]["count"] == 3.0
    assert stats["score"]["min"] == 78.0
    assert stats["score"]["max"] == 92.5

