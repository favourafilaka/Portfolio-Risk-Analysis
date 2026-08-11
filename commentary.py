def describe_performance(annualised_return: float,
                         cumulative_return: float) -> str:
    '''
    Describes overall portfolio performance.
    Parameters:
    annualised_return (float): Annualised portfolio return
    cumulative_return (float): Cumulative portfolio return
    Returns:
    str: Plain-English performance commentary
    '''
    return (
        f"The portfolio returned {annualised_return:.1%} annually, "
        f"with a cumulative return of {cumulative_return:.1%}."
    )


def describe_risk(volatility: float,
                  max_drawdown: float) -> str:
    '''
    Describes the portfolio risk profile.
    Parameters:
    volatility (float): Annualised portfolio volatility
    max_drawdown (float): Maximum portfolio drawdown
    Returns:
    str: Plain-English risk commentary
    '''
    if volatility < 0.10:
        risk_level = "low"
    elif volatility < 0.20:
        risk_level = "moderate"
    else:
        risk_level = "high"
    return (
        f"Portfolio volatility of {volatility:.1%} suggests {risk_level} risk, "
        f"with a maximum drawdown of {max_drawdown:.1%}."
    )


def describe_var_cvar(var_value: float,
                      cvar_value: float,
                      confidence_level: float) -> str:
    '''
    Describes portfolio VaR and CVaR.
    Parameters:
    var_value (float): Value at Risk threshold
    cvar_value (float): Conditional Value at Risk threshold
    confidence_level (float): VaR confidence level
    Returns:
    str: Plain-English VaR and CVaR commentary
    '''
    tail_probability = 1 - confidence_level
    return (
        f"There is a {tail_probability:.0%} chance of losing more than "
        f"{abs(var_value):.1%} in a single day, with average losses beyond "
        f"this threshold reaching {abs(cvar_value):.1%}."
    )


def describe_benchmark_comparison(alpha: float,
                                  beta: float,
                                  tracking_error: float) -> str:
    '''
    Describes portfolio benchmark performance.
    Parameters:
    alpha (float): Portfolio alpha relative to benchmark
    beta (float): Portfolio beta relative to benchmark
    tracking_error (float): Portfolio tracking error
    Returns:
    str: Plain-English benchmark commentary
    '''
    if alpha > 0:
        performance = "outperformed"
    elif alpha < 0:
        performance = "underperformed"
    else:
        performance = "performed in line with"
    return (
        f"The portfolio {performance} the benchmark, with an alpha of "
        f"{alpha:.1%}, a beta of {beta:.2f}, and tracking error of "
        f"{tracking_error:.1%}."
    )


def describe_stress_test(stress_summary) -> str:
    '''
    Describes the most severe stress scenario.
    Parameters:
    stress_summary (pd.DataFrame): Stress scenario results
    Returns:
    str: Plain-English stress test commentary
    '''
    worst_scenario = stress_summary["percentage_impact"].idxmin()
    worst_impact = stress_summary["percentage_impact"].min()
    return (
        f"Under the most severe scenario modelled, {worst_scenario}, "
        f"the portfolio would lose approximately {abs(worst_impact):.1%}."
    )


def describe_monte_carlo(simulation_summary) -> str:
    '''
    Describes Monte Carlo simulation outcomes.
    Parameters:
    simulation_summary (dict): Monte Carlo simulation summary
    Returns:
    str: Plain-English Monte Carlo commentary
    '''
    lower_bound = simulation_summary["percentile_5"]
    upper_bound = simulation_summary["percentile_95"]
    return (
        f"In 90% of simulated outcomes, the portfolio value falls between "
        f"{lower_bound:.1f} and {upper_bound:.1f} after one year."
    )


def generate_full_commentary(all_metrics: dict) -> str:
    '''
    Generates combined portfolio commentary.
    Parameters:
    all_metrics (dict): Portfolio analysis metrics
    Returns:
    str: Combined portfolio commentary
    '''
    performance = describe_performance(
        all_metrics["annualised_return"],
        all_metrics["cumulative_return"]
    )
    risk = describe_risk(
        all_metrics["volatility"],
        all_metrics["max_drawdown"]
    )
    var_cvar = describe_var_cvar(
        all_metrics["var"],
        all_metrics["cvar"],
        all_metrics["confidence_level"]
    )
    benchmark = describe_benchmark_comparison(
        all_metrics["alpha"],
        all_metrics["beta"],
        all_metrics["tracking_error"]
    )
    stress = describe_stress_test(all_metrics["stress_summary"])
    monte_carlo = describe_monte_carlo(all_metrics["simulation_summary"])
    return " ".join([
        performance,
        risk,
        var_cvar,
        benchmark,
        stress,
        monte_carlo
    ])