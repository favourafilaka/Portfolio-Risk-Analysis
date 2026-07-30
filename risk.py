import numpy as np 
import pandas as pd
from scipy.stats import norm

TRADING_DAYS_PER_YEAR = 252

def calculate_volatility(portfolio_returns):
    '''
    Calculates the annualised volatility of the portfolio returns.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    Returns:
    float: Annualised portfolio volatility
    '''
    daily_volatility = portfolio_returns.std()
    annualised_volatility = daily_volatility * np.sqrt(TRADING_DAYS_PER_YEAR)
    return annualised_volatility

def calculate_sharpe_ratio(portfolio_returns, risk_free_rate=0.0):
    '''
    Calculates the annualised Sharpe Ratio of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    risk_free_rate (float): Annual risk-free rate expressed as a decimal
    Returns:
    float: Annualised Sharpe Ratio
    '''
    daily_risk_free_rate = risk_free_rate / TRADING_DAYS_PER_YEAR
    excess_returns = portfolio_returns - daily_risk_free_rate
    mean_excess_return = excess_returns.mean()
    standard_deviation = excess_returns.std()
    if standard_deviation == 0:
        return np.nan
    sharpe_ratio = (mean_excess_return / standard_deviation) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return sharpe_ratio

def calculate_sortino_ratio(portfolio_returns, risk_free_rate=0.0):
    '''
    Calculates the annualised Sortino Ratio of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    risk_free_rate (float): Annual risk-free rate expressed as a decimal
    Returns:
    float: Annualised Sortino Ratio
    '''
    daily_risk_free_rate = risk_free_rate / TRADING_DAYS_PER_YEAR
    excess_returns = portfolio_returns - daily_risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    downside_standard_deviation = downside_returns.std()
    if downside_standard_deviation == 0 or pd.isna(downside_standard_deviation):
        return np.nan
    sortino_ratio = (excess_returns.mean() / downside_standard_deviation) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return sortino_ratio

def calculate_max_drawdown(cumulative_returns):
    '''
    Calculates the maximum drawdown of the portfolio.
    Parameters:
    cumulative_returns (pandas.Series): Cumulative portfolio returns indexed by date
    Returns:
    float: Maximum portfolio drawdown expressed as a decimal
    '''
    wealth_index = 1 + cumulative_returns
    running_max = wealth_index.cummax()
    drawdown = (wealth_index - running_max) / running_max
    maximum_drawdown = drawdown.min()
    return maximum_drawdown

def calculate_historical_var(portfolio_returns, confidence_level=0.95):
    '''
    Calculates the Historical Value at Risk (VaR) of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    confidence_level (float): Confidence level expressed as a decimal
    Returns:
    float: Historical Value at Risk expressed as a decimal
    '''
    percentile = (1 - confidence_level) * 100
    historical_var = np.percentile(portfolio_returns, percentile)
    return historical_var

def calculate_parametric_var(portfolio_returns, confidence_level=0.95):
    '''
    Calculates the Parametric Value at Risk (VaR) of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    confidence_level (float): Confidence level expressed as a decimal
    Returns:
    float: Parametric Value at Risk expressed as a decimal
    '''
    mean_return = portfolio_returns.mean()
    standard_deviation = portfolio_returns.std()
    z_score = norm.ppf(1 - confidence_level)
    parametric_var = mean_return + (z_score * standard_deviation)
    return parametric_var

def calculate_cvar(portfolio_returns, confidence_level=0.95):
    '''
    Calculates the Conditional Value at Risk (CVaR) of the portfolio.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    confidence_level (float): Confidence level expressed as a decimal
    Returns:
    float: Conditional Value at Risk expressed as a decimal
    '''
    var_threshold = calculate_historical_var(portfolio_returns, confidence_level)
    tail_losses = portfolio_returns[portfolio_returns <= var_threshold]
    if tail_losses.empty:
        return var_threshold
    cvar = tail_losses.mean()
    return cvar

