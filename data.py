import time
import yaml
import yfinance as yf
import pandas as pd


def load_config(path="config.yaml"):
    '''
    Loads the YAML config file containing portfolio presets and date range.
    Parameters:
    path (str): Path to the config file
    Returns:
    dict: Parsed config dictionary
    '''
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_portfolio_prices(portfolio_name, config, max_retries=3):
    '''
    Fetches daily closing prices for a chosen portfolio's tickers.
    Retries on rate limiting and raises a clear error if data is unavailable.
    Parameters:
    portfolio_name (str): Key identifying the portfolio preset
    config (dict): Loaded config dictionary
    max_retries (int): Number of retry attempts on failure
    Returns:
    pandas.DataFrame: Daily closing prices, indexed by date, one column per ticker
    '''
    portfolio = config["portfolios"][portfolio_name]
    tickers = portfolio["tickers"]
    start = config["date_range"]["start"]
    end = config["date_range"]["end"]

    for attempt in range(max_retries):
        prices = yf.download(tickers, start=start, end=end)["Close"]
        if not prices.empty:
            return prices
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s

    raise ValueError(
        f"No data returned for {tickers} between {start} and {end}. "
        "This is likely a Yahoo Finance rate limit — please try again shortly."
    )


if __name__ == "__main__":
    config = load_config()
    prices = get_portfolio_prices("growth", config)
    print(prices.head())
    print(prices.shape)
