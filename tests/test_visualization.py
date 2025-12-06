from reporting.visualization import plot_npv_distribution, plot_sensitivity_heatmap


def test_plot_npv_distribution_creates_file(tmp_path):
    output_path = tmp_path / "npv.csv"
    plot_npv_distribution([1, 2, 3], output_path)
    assert output_path.exists()
    content = output_path.read_text().strip().splitlines()
    assert content[0] == "period,discounted_cashflow"


def test_plot_sensitivity_heatmap_creates_file(tmp_path):
    output_path = tmp_path / "heatmap.csv"
    drates = [0.08, 0.1]
    grates = [0.02, 0.03, 0.04]
    terminal_values = [[1.0 for _ in grates] for _ in drates]
    plot_sensitivity_heatmap(drates, grates, terminal_values, output_path)
    assert output_path.exists()
    lines = output_path.read_text().strip().splitlines()
    assert lines[0].startswith("discount_rate\\terminal_growth")
