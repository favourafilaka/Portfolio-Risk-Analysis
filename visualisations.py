import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def plot_cumulative_returns(cumulative_returns: pd.Series,
                            benchmark_cumulative_returns: pd.Series = None) -> go.Figure:
    '''
    Plots cumulative portfolio returns.
    Parameters:
    cumulative_returns (pd.Series): Cumulative portfolio returns indexed by date
    benchmark_cumulative_returns (pd.Series): Optional cumulative benchmark returns
    Returns:
    go.Figure: Line chart of cumulative returns
    '''
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cumulative_returns.index,
        y=cumulative_returns.values,
        name="Portfolio",
        mode="lines"
    ))
    if benchmark_cumulative_returns is not None:
        fig.add_trace(go.Scatter(
            x=benchmark_cumulative_returns.index,
            y=benchmark_cumulative_returns.values,
            name="Benchmark",
            mode="lines"
        ))
    fig.update_layout(
        title="Cumulative Return",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        yaxis_tickformat=".0%"
    )
    return fig


def plot_drawdown(cumulative_returns: pd.Series) -> go.Figure:
    '''
    Plots portfolio drawdown through time.
    Parameters:
    cumulative_returns (pd.Series): Cumulative portfolio returns indexed by date
    Returns:
    go.Figure: Filled area chart of portfolio drawdown
    '''
    wealth_index = 1 + cumulative_returns
    running_max = wealth_index.cummax()
    drawdown = (wealth_index - running_max) / running_max
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown.values,
        fill="tozeroy",
        name="Drawdown",
        line=dict(color="red")
    ))
    fig.update_layout(
        title="Portfolio Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis_tickformat=".0%"
    )
    return fig


def plot_rolling_metrics(rolling_returns: pd.Series,
                         rolling_volatility: pd.Series) -> go.Figure:
    '''
    Plots rolling return and volatility.
    Parameters:
    rolling_returns (pd.Series): Rolling period returns indexed by date
    rolling_volatility (pd.Series): Rolling annualised volatility indexed by date
    Returns:
    go.Figure: Dual-axis chart of rolling metrics
    '''
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rolling_returns.index,
        y=rolling_returns.values,
        name="Rolling Return",
        yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=rolling_volatility.index,
        y=rolling_volatility.values,
        name="Rolling Volatility",
        yaxis="y2"
    ))
    fig.update_layout(
        title="Rolling Return vs Rolling Volatility",
        xaxis_title="Date",
        yaxis=dict(title="Rolling Return", tickformat=".0%"),
        yaxis2=dict(title="Rolling Volatility", tickformat=".0%",
                    overlaying="y", side="right")
    )
    return fig


def plot_var_cvar(portfolio_returns: pd.Series,
                  var_value: float,
                  cvar_value: float) -> go.Figure:
    '''
    Plots return distribution with VaR and CVaR.
    Parameters:
    portfolio_returns (pd.Series): Daily portfolio returns
    var_value (float): VaR threshold from risk.py
    cvar_value (float): CVaR threshold from risk.py
    Returns:
    go.Figure: Histogram with VaR and CVaR lines
    '''
    fig = px.histogram(portfolio_returns, nbins=50, title="Return Distribution: VaR & CVaR")
    fig.add_vline(x=var_value, line_color="orange", line_dash="dash",
                  annotation_text="VaR")
    fig.add_vline(x=cvar_value, line_color="red", line_dash="dash",
                  annotation_text="CVaR")
    fig.update_layout(
        xaxis_title="Daily Return",
        yaxis_title="Frequency",
        showlegend=False
    )
    return fig


def plot_monte_carlo_fan_chart(percentile_paths: pd.DataFrame) -> go.Figure:
    '''
    Plots Monte Carlo percentile paths.
    Parameters:
    percentile_paths (pd.DataFrame): Percentile paths from monte_carlo.py
    Returns:
    go.Figure: Fan chart of simulated portfolio outcomes
    '''
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=percentile_paths.index, y=percentile_paths["percentile_95"],
        name="95th Percentile", line=dict(color="lightblue")
    ))
    fig.add_trace(go.Scatter(
        x=percentile_paths.index, y=percentile_paths["percentile_50"],
        name="Median", line=dict(color="blue")
    ))
    fig.add_trace(go.Scatter(
        x=percentile_paths.index, y=percentile_paths["percentile_5"],
        name="5th Percentile", line=dict(color="lightblue"),
        fill="tonexty"
    ))
    fig.update_layout(
        title="Monte Carlo Simulation: Portfolio Value Range",
        xaxis_title="Day",
        yaxis_title="Portfolio Value"
    )
    return fig


def plot_correlation_heatmap(correlation_matrix: pd.DataFrame) -> go.Figure:
    '''
    Plots the asset correlation matrix.
    Parameters:
    correlation_matrix (pd.DataFrame): Asset correlation matrix from risk.py
    Returns:
    go.Figure: Heatmap of asset correlations
    '''
    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Asset Correlation Matrix"
    )
    return fig


def plot_stress_test_impact(stress_summary: pd.DataFrame) -> go.Figure:
    '''
    Plots stress test impact by scenario.
    Parameters:
    stress_summary (pd.DataFrame): Stress scenario results from stress_testing.py
    Returns:
    go.Figure: Bar chart of scenario percentage impacts
    '''
    sorted_summary = stress_summary.sort_values("percentage_impact")
    fig = go.Figure(go.Bar(
        x=sorted_summary.index,
        y=sorted_summary["percentage_impact"],
        marker_color=["red" if v < 0 else "green"
                      for v in sorted_summary["percentage_impact"]]
    ))
    fig.update_layout(
        title="Stress Test Impact by Scenario",
        xaxis_title="Scenario",
        yaxis_title="Percentage Impact",
        yaxis_tickformat=".0%"
    )
    return fig