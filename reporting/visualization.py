from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def plot_npv_distribution(npv_series: Iterable[float], output_path: str) -> str:
    values = [float(v) for v in npv_series]
    if not values:
        raise ValueError("npv_series cannot be empty.")

    output = Path(output_path)
    with output.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["period", "discounted_cashflow"])
        for idx, value in enumerate(values, start=1):
            writer.writerow([idx, value])
    return str(output)


def plot_sensitivity_heatmap(
    discount_rates: Iterable[float],
    growth_rates: Iterable[float],
    terminal_values: list[list[float]],
    output_path: str,
) -> str:
    drates = [float(d) for d in discount_rates]
    grates = [float(g) for g in growth_rates]
    if not drates or not grates:
        raise ValueError("discount_rates and growth_rates cannot be empty.")
    if len(terminal_values) != len(drates) or any(
        len(row) != len(grates) for row in terminal_values
    ):
        raise ValueError(
            "terminal_values must match shape (len(discount_rates), len(growth_rates))."
        )

    output = Path(output_path)
    with output.open("w", newline="") as handle:
        writer = csv.writer(handle)
        header = ["discount_rate\\terminal_growth", *grates]
        writer.writerow(header)
        for rate, row in zip(drates, terminal_values):
            writer.writerow([rate, *row])
    return str(output)
