import pytest

from valuation.models import ValuationError, comparable_valuation, discounted_cash_flow, gordon_growth_model


def test_discounted_cash_flow_with_terminal_growth():
    cashflows = [100, 110, 121]
    result = discounted_cash_flow(cashflows, 0.1, terminal_growth_rate=0.02)
    assert pytest.approx(result.present_value, rel=1e-3) == 1431.82
    assert result.terminal_value > 0


def test_discounted_cash_flow_requires_positive_discount():
    with pytest.raises(ValuationError):
        discounted_cash_flow([100, 100], 0)


def test_gordon_growth_model():
    value = gordon_growth_model(2.0, 0.08, 0.03)
    assert pytest.approx(value, rel=1e-3) == 41.2


def test_comparable_valuation_filters_outliers():
    metric_value = 50
    peer_multiples = [8, 9, 7, 100]  # 100 should be filtered as outlier
    valuation = comparable_valuation(metric_value, peer_multiples, outlier_threshold=1.5)
    assert pytest.approx(valuation, rel=1e-3) == 400


def test_comparable_valuation_raises_when_filtered_empty():
    with pytest.raises(ValuationError):
        comparable_valuation(10, [1000], outlier_threshold=1.0)
