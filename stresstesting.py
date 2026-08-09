import pandas as pd

def apply_shock(portfolio_value, shock_size):
    '''
    Applies a percentage shock to the portfolio value.
    Parameters:
    portfolio_value (float): Current portfolio value
    shock_size (float): Percentage shock expressed as a decimal
    Returns:
    float: Portfolio value after the shock
    '''
    shocked_portfolio_value = portfolio_value * (1 + shock_size)
    return shocked_portfolio_value

def apply_historical_scenario(portfolio_value, scenario_returns):
    '''
    Applies a historical market scenario to the portfolio value.
    Parameters:
    portfolio_value (float): Current portfolio value
    scenario_returns (pandas.Series): Daily returns from a historical market scenario
    Returns:
    pandas.Series: Simulated portfolio values throughout the historical scenario
    '''
    growth_factors = (1 + scenario_returns).cumprod()
    simulated_portfolio_values = portfolio_value * growth_factors
    return simulated_portfolio_values

def run_custom_scenario(portfolio_value, shocked_days):
    '''
    Runs a custom stress scenario using a sequence of daily shocks.
    Parameters:
    portfolio_value (float): Current portfolio value
    shocked_days (list): Daily percentage shocks expressed as decimals
    Returns:
    pandas.Series: Simulated portfolio values throughout the custom scenario
    '''
    shocked_returns = pd.Series(shocked_days)
    growth_factors = (1 + shocked_returns).cumprod()
    simulated_portfolio_values = portfolio_value * growth_factors
    return simulated_portfolio_values

def calculate_stress_impact(portfolio_value, shocked_value):
    '''
    Calculates the impact of a stress scenario on the portfolio value.
    Parameters:
    portfolio_value (float): Portfolio value before the stress scenario
    shocked_value (float): Portfolio value after the stress scenario
    Returns:
    dict: Absolute and percentage impact of the stress scenario
    '''
    absolute_impact = shocked_value - portfolio_value
    percentage_impact = (shocked_value / portfolio_value) - 1
    stress_impact = {
        "absolute_impact": absolute_impact,
        "percentage_impact": percentage_impact
    }
    return stress_impact

def generate_stress_summary(portfolio_value, scenarios):
    '''
    Generates a summary of multiple stress testing scenarios.
    Parameters:
    portfolio_value (float): Current portfolio value
    scenarios (dict): Dictionary containing named stress scenarios
    Returns:
    pandas.DataFrame: Summary of stress testing results
    '''
    results = {}

    for name, scenario in scenarios.items():
        if isinstance(scenario, (float, int)):
            shocked_value = apply_shock(portfolio_value, scenario)

        elif isinstance(scenario, pd.Series):
            shocked_path = apply_historical_scenario(portfolio_value, scenario)
            shocked_value = shocked_path.iloc[-1]

        elif isinstance(scenario, list):
            shocked_path = run_custom_scenario(portfolio_value, scenario)
            shocked_value = shocked_path.iloc[-1]

        else:
            raise ValueError(f"Unsupported scenario type for '{name}': {type(scenario)}")

        impact = calculate_stress_impact(portfolio_value, shocked_value)

        results[name] = {
            "shocked_value": shocked_value,
            "absolute_impact": impact["absolute_impact"],
            "percentage_impact": impact["percentage_impact"]
        }

    stress_summary = pd.DataFrame(results).T
    return stress_summary
