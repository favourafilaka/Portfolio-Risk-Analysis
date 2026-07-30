import numpy as np
import pandas as pd

def validate_weights(weights):
    '''
    Checks whether portfolio weights are valid before calculations begin.
    Parameters:
    weights (dict): Dictionary mapping tickers to portfolio weights
    Returns:
    None: Raises a ValueError if the weights are invalid
    '''
    if not weights:
        raise ValueError("Weights dictionary is empty.")
    for ticker, weight in weights.items():
        if not isinstance(weight, (int, float)):
            raise ValueError(f"Weight for {ticker} is not numeric: {weight}")
        if weight < 0:
            raise ValueError(f"Negative weight for {ticker}: {weight}. Short positions are not supported.")
    total = sum(weights.values())
    if total == 0:
        raise ValueError("Weights sum to zero. Portfolio cannot be normalised.")

def normalise_weights(weights):
    '''
    Rescales portfolio weights so that they sum to 1.
    Parameters:
    weights (dict): Dictionary mapping tickers to portfolio weights
    Returns:
    dict: Dictionary containing normalised portfolio weights
    '''
    validate_weights(weights)
    total = sum(weights.values())
    return {ticker: weight / total for ticker, weight in weights.items()}

def calculate_portfolio_returns(price_data, weights):
    '''
    Calculates the daily returns of the portfolio using asset prices and portfolio weights.
    Parameters:
    price_data (pandas.DataFrame): Daily closing prices for each asset in the portfolio
    weights (dict): Dictionary mapping tickers to portfolio weights
    Returns:
    pandas.Series: Daily portfolio returns indexed by date
    '''
    missing = set(weights.keys()) - set(price_data.columns)
    if missing:
        raise ValueError(f"Tickers missing from price data: {missing}")
    weights = normalise_weights(weights)
    asset_returns = price_data[list(weights.keys())].pct_change().dropna()
    weight_vector = pd.Series(weights)
    portfolio_returns = asset_returns.mul(weight_vector, axis=1).sum(axis=1)
    portfolio_returns.name = "portfolio_return"
    return portfolio_returns

def calculate_cumulative_returns(portfolio_returns):
    '''
    Calculates the cumulative returns of the portfolio from the daily returns.
    Parameters:
    portfolio_returns (pandas.Series): Daily portfolio returns indexed by date
    Returns:
    pandas.Series: Cumulative portfolio returns indexed by date
    '''
    cumulative_returns = (1 + portfolio_returns).cumprod() - 1
    cumulative_returns.name = "cumulative_return"
    return cumulative_returns

def calculate_portfolio_value(cumulative_returns, initial_value=100_000):
    '''
    Calculates the portfolio value over time using cumulative returns.
    Parameters:
    cumulative_returns (pandas.Series): Cumulative portfolio returns indexed by date
    initial_value (float): Starting value of the portfolio
    Returns:
    pandas.Series: Portfolio value indexed by date
    '''
    portfolio_value = initial_value * (1 + cumulative_returns)
    portfolio_value.name = "portfolio_value"
    return portfolio_value

def calculate_correlation_matrix(price_data):
    '''
    Calculates the correlation matrix between assets in the portfolio.
    Parameters:
    price_data (pandas.DataFrame): Daily asset prices indexed by date
    Returns:
    pandas.DataFrame: Correlation matrix of asset daily returns
    '''
    asset_returns = price_data.pct_change().dropna()
    correlation_matrix = asset_returns.corr()
    return correlation_matrix