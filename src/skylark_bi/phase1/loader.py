"""
Dataset loading utilities for Phase 1.

Responsibilities:
- Validate dataset paths.
- Detect CSV/XLSX input.
- Load datasets into pandas DataFrames.
- Normalize column headers.
- Perform basic structural validation.

This module does NOT perform business-level cleaning.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}


class DatasetLoadError(Exception):
    """Raised when a dataset cannot be loaded."""


def validate_dataset_path(path: str | Path) -> Path:
    """
    Validate that the dataset exists and has a supported format.

    Args:
        path: Dataset file path.

    Returns:
        Validated Path object.

    Raises:
        FileNotFoundError: If the file does not exist.
        DatasetLoadError: If the file format is unsupported.
    """
    dataset_path = Path(path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    if not dataset_path.is_file():
        raise DatasetLoadError(
            f"Dataset path is not a file: {dataset_path}"
        )

    suffix = dataset_path.suffix.lower()

    if suffix not in SUPPORTED_SUFFIXES:
        raise DatasetLoadError(
            f"Unsupported dataset format: {suffix}. "
            f"Supported formats: {sorted(SUPPORTED_SUFFIXES)}"
        )

    return dataset_path


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV dataset."""
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise DatasetLoadError(
            f"Failed to read CSV dataset: {path}"
        ) from exc


def load_excel(path: Path) -> pd.DataFrame:
    """Load an Excel dataset."""
    try:
        return pd.read_excel(path)
    except Exception as exc:
        raise DatasetLoadError(
            f"Failed to read Excel dataset: {path}"
        ) from exc


def normalize_column_name(column: object) -> str:
    """
    Normalize a column name without changing its semantic meaning.

    Example:
        "  Deal   Name  " -> "Deal Name"
    """
    return " ".join(str(column).strip().split())


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column headers.

    The original DataFrame is not mutated.
    """
    normalized = df.copy()

    normalized.columns = [
        normalize_column_name(column)
        for column in normalized.columns
    ]

    return normalized


def validate_dataframe(df: pd.DataFrame, dataset_name: str) -> None:
    """
    Perform basic structural validation.

    This deliberately does not reject missing values because
    the assignment explicitly requires graceful handling of
    messy/incomplete data.
    """
    if df.empty:
        raise DatasetLoadError(
            f"{dataset_name} contains no records."
        )

    if len(df.columns) == 0:
        raise DatasetLoadError(
            f"{dataset_name} contains no columns."
        )

    duplicate_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    if duplicate_columns:
        raise DatasetLoadError(
            f"{dataset_name} contains duplicate column names: "
            f"{duplicate_columns}"
        )


def load_dataset(
    path: str | Path,
    *,
    dataset_name: str | None = None,
    normalize_headers_flag: bool = True,
) -> pd.DataFrame:
    """
    Load and validate a dataset.

    Args:
        path: CSV/XLSX dataset path.
        dataset_name: Human-readable dataset name for errors.
        normalize_headers_flag: Whether to normalize column headers.

    Returns:
        Loaded pandas DataFrame.
    """
    dataset_path = validate_dataset_path(path)

    name = dataset_name or dataset_path.stem

    suffix = dataset_path.suffix.lower()

    if suffix == ".csv":
        df = load_csv(dataset_path)
    elif suffix in {".xlsx", ".xls"}:
        df = load_excel(dataset_path)
    else:
        # Defensive guard; validate_dataset_path already checks this.
        raise DatasetLoadError(
            f"Unsupported dataset format: {suffix}"
        )

    if normalize_headers_flag:
        df = normalize_headers(df)

    validate_dataframe(df, name)

    return df
