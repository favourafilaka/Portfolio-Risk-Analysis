import numpy as np
import pandas as pd


def simulate_returns(portfolio_returns, num_simulations=1000, num_days=252, random_seed=None):
    '''
    Simulates future daily portfolio returns using a normal distribution.
    Parameters:
    portfolio_returns (pandas.Series): Historical daily portfolio returns indexed by date
    num_simulations (int): Number of simulation paths to generate
    num_days (int): Number of trading days to simulate
    random_seed (int): Optional random seed for reproducible results
    Returns:
    numpy.ndarray: Simulated daily returns for each simulation path
    '''
    if random_seed is not None:
        np.random.seed(random_seed)
    daily_mean = portfolio_returns.mean()
    daily_standard_deviation = portfolio_returns.std()
    simulated_returns = np.random.normal(loc=daily_mean, scale=daily_standard_deviation, size=(num_simulations, num_days))
    return simulated_returns


def calculate_simulated_values(simulated_returns, initial_value=100_000):
    '''
    Calculates simulated portfolio values from simulated daily returns.
    Parameters:
    simulated_returns (numpy.ndarray): Simulated daily returns for each simulation path
    initial_value (float): Starting portfolio value
    Returns:
    numpy.ndarray: Simulated portfolio values for each simulation path
    '''
    growth_factors = 1 + simulated_returns
    cumulative_growth = np.cumprod(growth_factors, axis=1)
    simulated_values = initial_value * cumulative_growth
    return simulated_values


def calculate_simulation_summary(simulated_values):
    '''
    Summarises Monte Carlo simulation outcomes using final-day portfolio values.
    Parameters:
    simulated_values (numpy.ndarray): Simulated portfolio values for each simulation path
    Returns:
    dict: Summary statistics — mean, median, best_case, worst_case, percentile_5, percentile_95
    '''
    final_values = simulated_values[:, -1]
    simulation_summary = {
        "mean": final_values.mean(),
        "median": np.percentile(final_values, 50),
        "best_case": final_values.max(),
        "worst_case": final_values.min(),
        "percentile_5": np.percentile(final_values, 5),
        "percentile_95": np.percentile(final_values, 95),
    }
    return simulation_summary


def calculate_simulation_percentiles(simulated_values):
    '''
    Calculates the 5th, 50th and 95th percentile simulation paths.
    Parameters:
    simulated_values (numpy.ndarray): Simulated portfolio values for each simulation path
    Returns:
    pandas.DataFrame: Percentile simulation paths through time
    '''
    percentile_5 = np.percentile(simulated_values, 5, axis=0)
    percentile_50 = np.percentile(simulated_values, 50, axis=0)
    percentile_95 = np.percentile(simulated_values, 95, axis=0)
    percentile_paths = pd.DataFrame({
        "percentile_5": percentile_5,
        "percentile_50": percentile_50,
        "percentile_95": percentile_95
    })
    return percentile_paths


def run_monte_carlo_simulation(portfolio_returns, num_simulations=1000, num_days=252, initial_value=100_000, random_seed=None):
    '''
    Runs the complete Monte Carlo simulation workflow.
    Parameters:
    portfolio_returns (pandas.Series): Historical daily portfolio returns indexed by date
    num_simulations (int): Number of simulation paths to generate
    num_days (int): Number of trading days to simulate
    initial_value (float): Starting portfolio value
    random_seed (int): Optional random seed for reproducible results
    Returns:
    dict: Simulated portfolio values, simulation summary and percentile paths
    '''
    simulated_returns = simulate_returns(portfolio_returns, num_simulations, num_days, random_seed)
    simulated_values = calculate_simulated_values(simulated_returns, initial_value)
    summary = calculate_simulation_summary(simulated_values)
    percentile_paths = calculate_simulation_percentiles(simulated_values)
    monte_carlo_results = {
        "simulated_values": simulated_values,
        "summary": summary,
        "percentile_paths": percentile_paths
    }
    return monte_carlo_results
