from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional


class DataLoaderError(Exception):
    """Custom exception for data loading errors."""


def _validate_path(path: Path) -> Path:
    if not path.exists():
        raise DataLoaderError(f"File not found: {path}")
    if not path.is_file():
        raise DataLoaderError(f"Path is not a file: {path}")
    return path


def load_csv(filepath: str, *, expected_columns: Optional[list[str]] = None) -> list[dict[str, str]]:
    """Load a CSV file into a list of row dictionaries with optional column validation."""

    path = _validate_path(Path(filepath))
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if expected_columns:
            missing = [col for col in expected_columns if col not in reader.fieldnames]
            if missing:
                raise DataLoaderError(
                    f"Missing expected columns in CSV: {', '.join(missing)}"
                )
        return list(reader)


def load_excel(
    filepath: str, sheet_name: str | int = 0, *, expected_columns: Optional[list[str]] = None
) -> list[dict[str, str]]:
    """Explicitly signal that Excel loading is unavailable without external dependencies."""

    raise DataLoaderError(
        "Excel loading requires optional dependencies and is disabled in the lightweight build."
    )


def load_api_data(endpoint: str, *, api_key: Optional[str] = None) -> list[dict[str, str]]:
    """Placeholder for API-based loading.

    In a production setting, this function would make authenticated requests
    to a financial data provider. Here we raise a clear error to signal the
    feature is not yet implemented.
    """
    raise DataLoaderError(
        "API loading is not implemented. Use CSV uploads or extend load_api_data."
    )
