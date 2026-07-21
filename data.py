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


def get_portfolio_prices(portfolio_name, config):
    '''
    Fetches daily closing prices for a chosen portfolio's tickers.
    Parameters:
    portfolio_name (str): Key identifying the portfolio preset
    config (dict): Loaded config dictionary
    Returns:
    pandas.DataFrame: Daily closing prices, indexed by date, one column per ticker
    '''
    portfolio = config["portfolios"][portfolio_name]
    tickers = portfolio["tickers"]
    start = config["date_range"]["start"]
    end = config["date_range"]["end"]
    prices = yf.download(tickers, start=start, end=end)["Close"]
    return prices


if __name__ == "__main__":
    config = load_config()
    prices = get_portfolio_prices("growth", config)
    print(prices.head())
    print(prices.shape)
