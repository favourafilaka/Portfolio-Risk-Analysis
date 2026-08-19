import streamlit as st
import pandas as pd
import numpy as np

from data import load_config, get_portfolio_prices, get_benchmark_prices
from portfolio import (
    normalise_weights,
    calculate_portfolio_returns,
    calculate_cumulative_returns,
    calculate_portfolio_value,
    calculate_correlation_matrix,
)
from risk import (
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_historical_var,
    calculate_cvar,
)
from monte_carlo import run_monte_carlo_simulation
from backtesting import (
    calculate_rolling_returns,
    calculate_rolling_volatility,
    generate_backtest_summary,
)
from stresstesting import generate_stress_summary
from benchmark import generate_benchmark_summary, compare_cumulative_performance
from commentary import generate_full_commentary
from excel_export import export_to_excel
from visualisations import (
    plot_cumulative_returns,
    plot_drawdown,
    plot_rolling_metrics,
    plot_var_cvar,
    plot_monte_carlo_fan_chart,
    plot_correlation_heatmap,
    plot_stress_test_impact,
)

st.set_page_config(page_title="Portfolio Risk & Strategy Platform", layout="wide")

# Cached data loading functions

@st.cache_data
def cached_load_config():
    return load_config()

@st.cache_data(ttl=3600, show_spinner="Fetching market data...")
def cached_get_portfolio_prices(portfolio_name, config):
    return get_portfolio_prices(portfolio_name, config)

@st.cache_data(ttl=3600, show_spinner="Fetching benchmark data...")
def cached_benchmark_prices(ticker, start, end):
    return get_benchmark_prices(ticker, start, end)


# Sidebar — inputs & configuration

st.sidebar.title("Portfolio Settings")

config = cached_load_config()
portfolio_names = list(config["portfolios"].keys())
portfolio_name = st.sidebar.selectbox(
    "Portfolio preset", portfolio_names,
    format_func=lambda name: config["portfolios"][name].get("name", name)
)

preset = config["portfolios"][portfolio_name]

# Custom ticker selection if preset is empty
if not preset.get("tickers"):
    st.sidebar.subheader("Custom tickers")
    ticker_input = st.sidebar.text_input(
        "Tickers (comma-separated)", value="AAPL, MSFT, GOOGL"
    )
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    config["portfolios"][portfolio_name]["tickers"] = tickers
else:
    tickers = preset["tickers"]

# Data Retrieval with Rate Limit & Error Handling
try:
    prices = cached_get_portfolio_prices(portfolio_name, config)
    if prices is None or prices.empty:
        st.error("⚠️ Failed to load price data. Yahoo Finance may be rate-limiting requests or returned no data. Please wait a few moments and try again.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error fetching price data: {e}")
    st.stop()

tickers = list(prices.columns)  # Keep in sync with returned yfinance columns

st.sidebar.subheader("Weights")
preset_weights = preset.get("weights") or []
equal_weight = round(1 / len(tickers), 4) if tickers else 0.0

preset_weight_lookup = (
    dict(zip(preset["tickers"], preset_weights))
    if preset_weights and len(preset_weights) == len(preset["tickers"])
    else {}
)

weights = {}
for ticker in tickers:
    default = preset_weight_lookup.get(ticker, equal_weight)
    weights[ticker] = st.sidebar.number_input(
        f"{ticker}", min_value=0.0, max_value=1.0, value=float(default), step=0.05
    )

initial_value = st.sidebar.number_input("Initial portfolio value (£)", value=100_000, step=10_000)
risk_free_rate = st.sidebar.slider("Risk-free rate", 0.0, 0.10, 0.04, step=0.005)
confidence_level = st.sidebar.slider("VaR/CVaR confidence level", 0.90, 0.99, 0.95, step=0.01)

default_benchmark = preset.get("benchmark") or "^GSPC"
benchmark_ticker = st.sidebar.text_input("Benchmark ticker", value=str(default_benchmark))

num_simulations = st.sidebar.slider("Monte Carlo simulations", 100, 5000, 1000, step=100)
num_days = st.sidebar.slider("Monte Carlo horizon (trading days)", 30, 504, 252, step=21)

# Core calculations with safety checks

weights = normalise_weights(weights)

portfolio_returns = calculate_portfolio_returns(prices, weights)

# Validate portfolio returns before passing to numpy/scipy calculations
if portfolio_returns.empty or portfolio_returns.dropna().empty:
    st.error("⚠️ Portfolio returns series is empty. Unable to compute risk metrics due to missing ticker data.")
    st.stop()

cumulative_returns = calculate_cumulative_returns(portfolio_returns)
portfolio_value = calculate_portfolio_value(cumulative_returns, initial_value)
correlation_matrix = calculate_correlation_matrix(prices)

volatility = calculate_volatility(portfolio_returns)
sharpe = calculate_sharpe_ratio(portfolio_returns, risk_free_rate)
sortino = calculate_sortino_ratio(portfolio_returns, risk_free_rate)
max_drawdown = calculate_max_drawdown(cumulative_returns)
var_value = calculate_historical_var(portfolio_returns, confidence_level)
cvar_value = calculate_cvar(portfolio_returns, confidence_level)

rolling_returns = calculate_rolling_returns(portfolio_returns)
rolling_volatility = calculate_rolling_volatility(portfolio_returns)
backtest_summary = generate_backtest_summary(portfolio_returns, cumulative_returns)

monte_carlo_results = run_monte_carlo_simulation(
    portfolio_returns,
    num_simulations=num_simulations,
    num_days=num_days,
    initial_value=initial_value,
)

stress_scenarios = {
    "Market crash (-30%)": -0.30,
    "Correction (-10%)": -0.10,
    "Rate shock (-15%)": -0.15,
    "Rally (+10%)": 0.10,
}
stress_summary = generate_stress_summary(portfolio_value.iloc[-1], stress_scenarios)

# Benchmark data loading & verification
try:
    benchmark_prices = cached_benchmark_prices(
        benchmark_ticker,
        config["date_range"]["start"],
        config["date_range"]["end"],
    )
    if benchmark_prices is None or benchmark_prices.empty:
        st.warning(f"⚠️ Benchmark data for '{benchmark_ticker}' could not be fetched.")
        benchmark_returns = pd.Series(dtype=float)
    else:
        benchmark_returns = benchmark_prices.pct_change().dropna()
        benchmark_returns = benchmark_returns.reindex(portfolio_returns.index).dropna()
except Exception as e:
    st.warning(f"⚠️ Could not load benchmark data: {e}")
    benchmark_returns = pd.Series(dtype=float)

aligned_portfolio_returns = portfolio_returns.reindex(benchmark_returns.index).dropna()

if not benchmark_returns.empty and not aligned_portfolio_returns.empty:
    benchmark_summary = generate_benchmark_summary(
        aligned_portfolio_returns, benchmark_returns, risk_free_rate
    )
    benchmark_cumulative_returns = calculate_cumulative_returns(benchmark_returns)
    cumulative_comparison = compare_cumulative_performance(
        cumulative_returns, benchmark_cumulative_returns
    )
else:
    benchmark_summary = {"beta": 0.0, "alpha": 0.0, "tracking_error": 0.0, "information_ratio": 0.0}
    benchmark_cumulative_returns = pd.Series(0, index=cumulative_returns.index)
    cumulative_comparison = {"portfolio": cumulative_returns, "benchmark": benchmark_cumulative_returns}

# Layout & Rendering

st.title("Portfolio Risk & Strategy Analysis Platform")
st.caption(f"Portfolio: {portfolio_name} | {len(tickers)} assets | "
           f"{prices.index[0].date()} to {prices.index[-1].date()}")

tab_overview, tab_risk, tab_benchmark, tab_backtest, tab_mc, tab_stress, tab_commentary = st.tabs(
    ["Overview", "Risk", "Benchmark", "Backtesting", "Monte Carlo", "Stress Testing", "Commentary"]
)

with tab_overview:
    col1, col2, col3 = st.columns(3)
    col1.metric("Current portfolio value", f"£{portfolio_value.iloc[-1]:,.0f}")
    col2.metric("Cumulative return", f"{cumulative_returns.iloc[-1]:.1%}")
    col3.metric("Annualised volatility", f"{volatility:.1%}")

    st.plotly_chart(
        plot_cumulative_returns(cumulative_returns, benchmark_cumulative_returns),
        use_container_width=True
    )
    st.plotly_chart(plot_correlation_heatmap(correlation_matrix), use_container_width=True)

    st.subheader("Weights")
    st.dataframe(pd.DataFrame.from_dict(weights, orient="index", columns=["Weight"]))

with tab_risk:
    col1, col2, col3 = st.columns(3)
    col1.metric("Sharpe ratio", f"{sharpe:.2f}")
    col2.metric("Sortino ratio", f"{sortino:.2f}")
    col3.metric("Max drawdown", f"{max_drawdown:.1%}")

    col4, col5 = st.columns(2)
    col4.metric(f"VaR ({confidence_level:.0%})", f"{var_value:.1%}")
    col5.metric(f"CVaR ({confidence_level:.0%})", f"{cvar_value:.1%}")

    st.plotly_chart(plot_drawdown(cumulative_returns), use_container_width=True)
    st.plotly_chart(
        plot_var_cvar(portfolio_returns, var_value, cvar_value), use_container_width=True
    )

with tab_benchmark:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Beta", f"{benchmark_summary['beta']:.2f}")
    col2.metric("Alpha", f"{benchmark_summary['alpha']:.1%}")
    col3.metric("Tracking error", f"{benchmark_summary['tracking_error']:.1%}")
    col4.metric("Information ratio", f"{benchmark_summary['information_ratio']:.2f}")

    st.plotly_chart(
        plot_cumulative_returns(
            cumulative_comparison["portfolio"], cumulative_comparison["benchmark"]
        ),
        use_container_width=True
    )

with tab_backtest:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annualised return", f"{backtest_summary['annualised_return']:.1%}")
    col2.metric("Calmar ratio", f"{backtest_summary['calmar_ratio']:.2f}")
    col3.metric("Win rate", f"{backtest_summary['win_rate']:.1%}")
    col4.metric("Max drawdown", f"{backtest_summary['max_drawdown']:.1%}")

    st.plotly_chart(
        plot_rolling_metrics(rolling_returns, rolling_volatility), use_container_width=True
    )

with tab_mc:
    summary = monte_carlo_results["summary"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected value", f"£{summary['mean']:,.0f}")
    col2.metric("5th percentile", f"£{summary['percentile_5']:,.0f}")
    col3.metric("95th percentile", f"£{summary['percentile_95']:,.0f}")

    st.plotly_chart(
        plot_monte_carlo_fan_chart(monte_carlo_results["percentile_paths"]),
        use_container_width=True
    )

with tab_stress:
    st.dataframe(stress_summary.style.format({
        "shocked_value": "£{:,.0f}",
        "absolute_impact": "£{:,.0f}",
        "percentage_impact": "{:.1%}",
    }))
    st.plotly_chart(plot_stress_test_impact(stress_summary), use_container_width=True)

with tab_commentary:
    all_metrics = {
        "annualised_return": backtest_summary["annualised_return"],
        "cumulative_return": cumulative_returns.iloc[-1],
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "var": var_value,
        "cvar": cvar_value,
        "confidence_level": confidence_level,
        "alpha": benchmark_summary["alpha"],
        "beta": benchmark_summary["beta"],
        "tracking_error": benchmark_summary["tracking_error"],
        "stress_summary": stress_summary,
        "simulation_summary": monte_carlo_results["summary"],
    }
    st.write(generate_full_commentary(all_metrics))

# Excel export

st.sidebar.subheader("Export")
if st.sidebar.button("Generate Excel report"):
    portfolio_data = [
        {
            "ticker": ticker,
            "weight": weights[ticker],
            "portfolio_value": portfolio_value.iloc[-1] * weights[ticker],
            "return": portfolio_returns.iloc[-1],
        }
        for ticker in tickers
    ]

    all_data = {
        "portfolio": portfolio_data,
        "risk": {
            "volatility": volatility,
            "sharpe": sharpe,
            "sortino": sortino,
            "var": var_value,
            "cvar": cvar_value,
            "drawdown": max_drawdown,
        },
        "benchmark": benchmark_summary,
        "backtesting": backtest_summary,
        "monte_carlo": monte_carlo_results["summary"],
        "stress_testing": stress_summary,
    }

    output_path = "portfolio_report.xlsx"
    export_to_excel(all_data, output_path)

    with open(output_path, "rb") as f:
        st.sidebar.download_button(
            "Download Excel report", f, file_name=output_path,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )