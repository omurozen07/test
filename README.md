# Valuation Toolkit

A lightweight CLI toolkit for equity valuation supporting discounted cash flow (DCF), Gordon growth, and comparable company analysis. Data can be provided via CSV uploads, with hooks for future API integrations. Visualizations are emitted as CSV summaries so the project works without third-party dependencies.

## Features
- **Data loading** from CSV via `data.loader` with validation and clear errors.
- **Valuation models** in `valuation.models` including DCF (with terminal growth), Gordon growth model, and comparable multiples with outlier handling.
- **CLI** entry point `valuation` (see `pyproject.toml`) providing commands:
- `value-dcf --cashflows data/sample_cashflows.csv --discount 0.1 --terminal-growth 0.02 --npv-chart npv.csv --sensitivity-chart heatmap.csv`
  - `value-gordon --dividend 2 --discount 0.08 --growth 0.03`
  - `value-comps --metric 50 --multiples data/sample_multiples.csv`
- **Visualization** utilities that write NPV series and sensitivity grids to CSV files (no plotting libraries required).
- **Testing** with pytest covering loaders, valuation models, and chart generation.

## Data format
Cash flow and multiples CSVs should include a `cashflow` column, e.g.:

```csv
cashflow
100
110
121
```

> Note: Excel loading and chart image generation are intentionally disabled in this offline-friendly build. Use CSV inputs and
> the CSV report outputs shown above.

## Development
Install in editable mode (no third-party dependencies needed) and run tests:

```bash
pip install -e .[dev]
pytest
```
