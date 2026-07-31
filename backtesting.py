import numpy as np
import pandas as pd
from risk import calculate_max_drawdown

TRADING_DAYS_PER_YEAR = 252

def calculate_annualised_return(portfolio_returns):
    '''
    Calculates the annualised return of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    Returns:
    float: Annualised portfolio return expressed as a decimal
    '''
    total_growth = (1 + portfolio_returns).prod()
    num_years = len(portfolio_returns) / TRADING_DAYS_PER_YEAR
    if num_years == 0:
        return np.nan
    annualised_return = total_growth ** (1 / num_years) - 1
    return annualised_return

def calculate_rolling_returns(portfolio_returns, window=30):
    '''
    Calculates the rolling returns of the portfolio over a specified window.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    window (int): Rolling window length in trading days
    Returns:
    pandas.Series: Rolling portfolio returns indexed by date
    '''
    rolling_growth = (1 + portfolio_returns).rolling(window).apply(lambda x: x.prod(), raw=True)
    rolling_returns = rolling_growth - 1
    return rolling_returns

def calculate_rolling_volatility(portfolio_returns, window=30):
    '''
    Calculates the rolling annualised volatility of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    window (int): Rolling window length in trading days
    Returns:
    pandas.Series: Rolling annualised portfolio volatility indexed by date
    '''
    rolling_standard_deviation = portfolio_returns.rolling(window).std()
    rolling_volatility = rolling_standard_deviation * np.sqrt(TRADING_DAYS_PER_YEAR)
    return rolling_volatility

def calculate_calmar_ratio(portfolio_returns, cumulative_returns):
    '''
    Calculates the Calmar Ratio of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    cumulative_returns (pandas.Series): Cumulative portfolio returns indexed by date
    Returns:
    float: Portfolio Calmar Ratio
    '''
    annualised_return = calculate_annualised_return(portfolio_returns)
    maximum_drawdown = calculate_max_drawdown(cumulative_returns)
    if maximum_drawdown == 0:
        return np.nan
    calmar_ratio = annualised_return / abs(maximum_drawdown)
    return calmar_ratio

def calculate_win_rate(portfolio_returns):
    '''
    Calculates the win rate of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    Returns:
    float: Proportion of trading days with a positive return
    '''
    winning_days = (portfolio_returns > 0).sum()
    total_days = len(portfolio_returns)
    if total_days == 0:
        return np.nan
    win_rate = winning_days / total_days
    return win_rate

def compare_periods(portfolio_returns, period_1, period_2):
    '''
    Compares portfolio performance across two different time periods.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    period_1 (tuple): Start and end dates for the first period
    period_2 (tuple): Start and end dates for the second period
    Returns:
    dict: Performance metrics for each period
    '''
    def summarise(start, end):
        subset = portfolio_returns.loc[start:end]
        return {
            "annualised_return": calculate_annualised_return(subset),
            "volatility": subset.std() * np.sqrt(TRADING_DAYS_PER_YEAR),
            "win_rate": calculate_win_rate(subset)
        }
    comparison = {
        "period_1": summarise(*period_1),
        "period_2": summarise(*period_2)
    }
    return comparison

def generate_backtest_summary(portfolio_returns, cumulative_returns):
    '''
    Generates a summary of the portfolio backtesting results.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    cumulative_returns (pandas.Series): Cumulative portfolio returns indexed by date
    Returns:
    dict: Summary of the portfolio backtesting metrics
    '''
    backtest_summary = {
        "annualised_return": calculate_annualised_return(portfolio_returns),
        "calmar_ratio": calculate_calmar_ratio(portfolio_returns, cumulative_returns),
        "win_rate": calculate_win_rate(portfolio_returns),
        "max_drawdown": calculate_max_drawdown(cumulative_returns)
    }
    return backtest_summary