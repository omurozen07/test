from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable, Sequence


class ValuationError(Exception):
    """Raised when valuation inputs are invalid."""


def _ensure_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValuationError(f"{name} must be positive. Received {value}.")


def _ensure_growth_less_than_discount(growth_rate: float, discount_rate: float) -> None:
    if growth_rate >= discount_rate:
        raise ValuationError("Growth rate must be less than discount rate for convergence.")


def _to_list(values: Iterable[float], name: str) -> list[float]:
    try:
        items = [float(v) for v in values]
    except (TypeError, ValueError) as exc:
        raise ValuationError(f"{name} must be numeric.") from exc
    if not items:
        raise ValuationError(f"{name} cannot be empty.")
    return items


@dataclass
class DiscountedCashFlowResult:
    present_value: float
    npv_series: list[float]
    terminal_value: float


def discounted_cash_flow(
    cashflows: Sequence[float],
    discount_rate: float,
    *,
    terminal_growth_rate: float | None = None,
) -> DiscountedCashFlowResult:
    """Compute DCF valuation with optional terminal growth.

    Args:
        cashflows: Projected free cash flows by period (annual).
        discount_rate: Required rate of return (e.g., 0.1 for 10%).
        terminal_growth_rate: Perpetual growth applied to final cash flow.
    """
    _ensure_positive(discount_rate, "discount_rate")
    cashflow_list = _to_list(cashflows, "cashflows")

    npv_series: list[float] = []
    present_value = 0.0
    for idx, cf in enumerate(cashflow_list, start=1):
        discount_factor = (1 + discount_rate) ** idx
        discounted = cf / discount_factor
        npv_series.append(discounted)
        present_value += discounted

    terminal_value = 0.0
    if terminal_growth_rate is not None:
        _ensure_growth_less_than_discount(terminal_growth_rate, discount_rate)
        last_cashflow = cashflow_list[-1]
        terminal_value = (last_cashflow * (1 + terminal_growth_rate)) / (
            discount_rate - terminal_growth_rate
        )
        present_value += terminal_value / ((1 + discount_rate) ** len(cashflow_list))

    return DiscountedCashFlowResult(
        present_value=float(present_value),
        npv_series=npv_series,
        terminal_value=float(terminal_value),
    )


def gordon_growth_model(
    dividend: float,
    discount_rate: float,
    growth_rate: float,
) -> float:
    """Value equity using the Gordon growth (Dividend Discount) model."""
    _ensure_positive(dividend, "dividend")
    _ensure_positive(discount_rate, "discount_rate")
    _ensure_growth_less_than_discount(growth_rate, discount_rate)
    return dividend * (1 + growth_rate) / (discount_rate - growth_rate)


def comparable_valuation(
    metric_value: float,
    peer_multiples: Iterable[float],
    *,
    outlier_threshold: float | None = 3.0,
) -> float:
    """Estimate value using comparable company multiples.

    Args:
        metric_value: The target company's financial metric (e.g., EBITDA).
        peer_multiples: Collection of peer multiples.
        outlier_threshold: Z-score cutoff for removing extreme multiples.
    """
    _ensure_positive(metric_value, "metric_value")
    multiples = _to_list(peer_multiples, "peer_multiples")
    avg = sum(multiples) / len(multiples)
    _ensure_positive(avg, "peer_multiples mean")

    filtered = multiples
    if outlier_threshold is not None:
        variance = sum((m - avg) ** 2 for m in multiples) / len(multiples)
        stdev = variance**0.5
        if stdev == 0:
            filtered = []
        else:
            filtered = [
                m
                for m in multiples
                if abs((m - avg) / stdev) <= outlier_threshold
            ]
        if not filtered:
            raise ValuationError("All peer multiples filtered out as outliers.")

    representative_multiple = float(median(filtered))
    return representative_multiple * metric_value
