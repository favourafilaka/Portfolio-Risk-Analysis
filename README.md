# Portfolio Risk & Strategy Analysis Platform

An interactive Python/Streamlit platform for evaluating portfolio performance alongside the risk taken to achieve it — combining historical, benchmark-relative and forward-looking analysis in one workflow.

## What it does

- **Performance & risk metrics**: cumulative return, annualised volatility, Sharpe/Sortino ratios, maximum drawdown, VaR/CVaR
- **Benchmark comparison**: beta, alpha, tracking error, information ratio vs. a chosen benchmark
- **Backtesting**: rolling return and volatility analysis over time
- **Monte Carlo simulation**: 1,000-path forward-looking distribution of portfolio outcomes
- **Stress testing**: portfolio impact under predefined market and rate shocks
- **Automated commentary**: plain-English interpretation of results
- **Excel export**: multi-sheet workbook with a formula-driven dashboard and chart
- **Streamlit app**: interactive UI to adjust weights, benchmark, and risk assumptions

## Example output

Tested on a concentrated tech portfolio (AAPL, MSFT, NVDA, AMZN, GOOGL), Jan 2019–Aug 2026:

- Cumulative Return: 1,024.9% (~37.5% CAGR)
- Sharpe / Sortino: 1.11 / 1.52
- Max Drawdown: -40.2%
- Alpha vs. QQQ: 9.4%

Full methodology, results and discussion are in [`report.pdf`](./report/report.pdf).

## Stack

Python, Streamlit, pandas, NumPy, openpyxl

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

Twelve modules covering data handling, risk metrics, benchmarking, backtesting, Monte Carlo, stress testing, commentary generation, and Excel export, plus a flat `app.py` Streamlit entry point.

