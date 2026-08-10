import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

def calculate_beta(portfolio_returns, benchmark_returns):
    '''
    Calculates the beta of the portfolio relative to a benchmark.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    benchmark_returns (pandas.Series): Daily benchmark returns indexed by date
    Returns:
    float: Portfolio beta relative to the benchmark
    '''
    aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    aligned_returns.columns = ["portfolio", "benchmark"]
    covariance = aligned_returns["portfolio"].cov(aligned_returns["benchmark"])
    benchmark_variance = aligned_returns["benchmark"].var()
    if benchmark_variance == 0:
        return np.nan
    beta = covariance / benchmark_variance
    return beta

def calculate_alpha(portfolio_returns, benchmark_returns, risk_free_rate=0.0):
    '''
    Calculates the portfolio alpha relative to a benchmark.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    benchmark_returns (pandas.Series): Daily benchmark returns indexed by date
    risk_free_rate (float): Annualised risk-free rate expressed as a decimal
    Returns:
    float: Portfolio alpha relative to the benchmark
    '''
    beta = calculate_beta(portfolio_returns, benchmark_returns)
    aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    aligned_returns.columns = ["portfolio", "benchmark"]
    portfolio_annual_return = aligned_returns["portfolio"].mean() * TRADING_DAYS_PER_YEAR
    benchmark_annual_return = aligned_returns["benchmark"].mean() * TRADING_DAYS_PER_YEAR
    expected_return = risk_free_rate + beta * (benchmark_annual_return - risk_free_rate)
    alpha = portfolio_annual_return - expected_return
    return alpha

def calculate_tracking_error(portfolio_returns, benchmark_returns):
    '''
    Calculates the annualised tracking error of the portfolio relative to a benchmark.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    benchmark_returns (pandas.Series): Daily benchmark returns indexed by date
    Returns:
    float: Annualised tracking error expressed as a decimal
    '''
    aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    aligned_returns.columns = ["portfolio", "benchmark"]
    return_differences = aligned_returns["portfolio"] - aligned_returns["benchmark"]
    tracking_error = return_differences.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return tracking_error

def calculate_information_ratio(portfolio_returns, benchmark_returns):
    '''
    Calculates the information ratio of the portfolio relative to a benchmark.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    benchmark_returns (pandas.Series): Daily benchmark returns indexed by date
    Returns:
    float: Information ratio of the portfolio
    '''
    aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    aligned_returns.columns = ["portfolio", "benchmark"]
    return_differences = aligned_returns["portfolio"] - aligned_returns["benchmark"]
    annualised_excess_return = return_differences.mean() * TRADING_DAYS_PER_YEAR
    tracking_error = calculate_tracking_error(portfolio_returns, benchmark_returns)
    if tracking_error == 0:
        return np.nan
    information_ratio = annualised_excess_return / tracking_error
    return information_ratio

def compare_cumulative_performance(portfolio_cumulative_returns, benchmark_cumulative_returns):
    '''
    Compares cumulative portfolio performance against a benchmark.
    Parameters:
    portfolio_cumulative_returns (pandas.Series): Cumulative portfolio returns indexed by date
    benchmark_cumulative_returns (pandas.Series): Cumulative benchmark returns indexed by date
    Returns:
    pandas.DataFrame: Portfolio and benchmark cumulative returns aligned by date
    '''
    comparison = pd.concat(
        [portfolio_cumulative_returns, benchmark_cumulative_returns],
        axis=1
    ).dropna()
    comparison.columns = ["portfolio", "benchmark"]
    return comparison

def generate_benchmark_summary(portfolio_returns, benchmark_returns, risk_free_rate=0.0):
    '''
    Generates a summary of benchmark-relative portfolio metrics.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    benchmark_returns (pandas.Series): Daily benchmark returns indexed by date
    risk_free_rate (float): Annualised risk-free rate expressed as a decimal
    Returns:
    dict: Summary of benchmark comparison metrics
    '''
    benchmark_summary = {
        "beta": calculate_beta(portfolio_returns, benchmark_returns),
        "alpha": calculate_alpha(portfolio_returns, benchmark_returns, risk_free_rate),
        "tracking_error": calculate_tracking_error(portfolio_returns, benchmark_returns),
        "information_ratio": calculate_information_ratio(portfolio_returns, benchmark_returns)
    }
    return benchmark_summary