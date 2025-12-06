import pytest

from data.loader import DataLoaderError, load_csv


def test_load_csv_with_expected_columns(tmp_path):
    csv_path = tmp_path / "cashflows.csv"
    csv_path.write_text("cashflow\n1\n2\n3\n", encoding="utf-8")

    loaded = load_csv(csv_path, expected_columns=["cashflow"])
    assert loaded == [{"cashflow": "1"}, {"cashflow": "2"}, {"cashflow": "3"}]


def test_load_csv_missing_columns(tmp_path):
    csv_path = tmp_path / "cashflows.csv"
    csv_path.write_text("value\n1\n2\n3\n", encoding="utf-8")

    with pytest.raises(DataLoaderError):
        load_csv(csv_path, expected_columns=["cashflow"])


def test_load_csv_missing_file():
    with pytest.raises(DataLoaderError):
        load_csv("/nonexistent/file.csv")
