from __future__ import annotations

import argparse
from typing import Sequence

from data.loader import DataLoaderError, load_csv
from reporting.visualization import plot_npv_distribution, plot_sensitivity_heatmap
from valuation.models import DiscountedCashFlowResult, ValuationError, comparable_valuation, discounted_cash_flow, gordon_growth_model


def _parse_cashflows(file_path: str) -> Sequence[float]:
    rows = load_csv(file_path, expected_columns=["cashflow"])
    try:
        return [float(row["cashflow"]) for row in rows]
    except (TypeError, ValueError, KeyError) as exc:
        raise DataLoaderError("Cashflow column must contain numeric values.") from exc


def _linspace(start: float, stop: float, *, num: int) -> list[float]:
    if num < 2:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def run_dcf(args: argparse.Namespace) -> DiscountedCashFlowResult:
    cashflows = _parse_cashflows(args.cashflows)
    result = discounted_cash_flow(
        cashflows,
        args.discount,
        terminal_growth_rate=args.terminal_growth,
    )

    if args.npv_chart:
        plot_npv_distribution(result.npv_series, args.npv_chart)

    if args.sensitivity_chart:
        discount_rates = _linspace(args.discount * 0.8, args.discount * 1.2, num=5)
        growth_rates = _linspace(
            (args.terminal_growth or 0) * 0.5, (args.terminal_growth or 0.02) * 1.5, num=5
        )
        terminal_grid: list[list[float]] = []
        last_cf = cashflows[-1]
        for dr in discount_rates:
            row: list[float] = []
            for gr in growth_rates:
                if dr > gr:
                    row.append((last_cf * (1 + gr)) / (dr - gr))
                else:
                    row.append(0.0)
            terminal_grid.append(row)
        plot_sensitivity_heatmap(discount_rates, growth_rates, terminal_grid, args.sensitivity_chart)

    return result


def run_gordon(args: argparse.Namespace) -> float:
    return gordon_growth_model(args.dividend, args.discount, args.growth)


def run_comps(args: argparse.Namespace) -> float:
    metrics = _parse_cashflows(args.multiples)
    return comparable_valuation(args.metric, metrics, outlier_threshold=args.outlier_threshold)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valuation toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dcf_parser = subparsers.add_parser("value-dcf", help="Run discounted cash flow valuation")
    dcf_parser.add_argument("--cashflows", required=True, help="Path to CSV with a 'cashflow' column")
    dcf_parser.add_argument("--discount", required=True, type=float, help="Discount rate (e.g., 0.1 for 10%)")
    dcf_parser.add_argument("--terminal-growth", dest="terminal_growth", type=float, help="Terminal growth rate")
    dcf_parser.add_argument("--npv-chart", dest="npv_chart", help="Path to save NPV bar chart")
    dcf_parser.add_argument("--sensitivity-chart", dest="sensitivity_chart", help="Path to save sensitivity heatmap")
    dcf_parser.set_defaults(func=run_dcf)

    gordon_parser = subparsers.add_parser("value-gordon", help="Run Gordon growth valuation")
    gordon_parser.add_argument("--dividend", required=True, type=float, help="Current dividend")
    gordon_parser.add_argument("--discount", required=True, type=float, help="Discount rate")
    gordon_parser.add_argument("--growth", required=True, type=float, help="Dividend growth rate")
    gordon_parser.set_defaults(func=run_gordon)

    comps_parser = subparsers.add_parser("value-comps", help="Comparable company analysis")
    comps_parser.add_argument("--metric", required=True, type=float, help="Target company financial metric (e.g., EBITDA)")
    comps_parser.add_argument("--multiples", required=True, help="CSV containing peer multiples in a 'cashflow' column")
    comps_parser.add_argument("--outlier-threshold", type=float, default=3.0, help="Z-score cutoff for outliers")
    comps_parser.set_defaults(func=run_comps)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except (DataLoaderError, ValuationError, ValueError) as exc:
        parser.error(str(exc))
        return 1

    if isinstance(result, DiscountedCashFlowResult):
        print(f"Present Value: {result.present_value:.2f}")
        print(f"Terminal Value: {result.terminal_value:.2f}")
    else:
        print(f"Valuation: {result:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
