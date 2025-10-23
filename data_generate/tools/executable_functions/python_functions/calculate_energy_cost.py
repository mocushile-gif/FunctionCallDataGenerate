def calculate_energy_cost(
    power_kw: float,
    usage_hours_per_day: float,
    rate_per_kwh: float,
    days_in_month: int = 30
) -> float:
    """
    Calculates the monthly energy cost for an appliance.

    Parameters:
    - power_kw (float): Power of the appliance in kilowatts.
    - usage_hours_per_day (float): Daily usage time in hours.
    - rate_per_kwh (float): Cost per kilowatt-hour.
    - days_in_month (int): Number of days in the month. Defaults to 30.

    Returns:
    - float: The total monthly cost in currency.
    """
    if power_kw <= 0 or usage_hours_per_day <= 0 or rate_per_kwh <= 0 or days_in_month <= 0:
        raise ValueError("All inputs must be positive values.")

    monthly_cost = power_kw * usage_hours_per_day * rate_per_kwh * days_in_month
    return round(monthly_cost, 2)


# 示例调用
if __name__ == "__main__":
    result = calculate_energy_cost(power_kw=1.5, usage_hours_per_day=5, rate_per_kwh=0.12)
    print(result)
    # 输出：27.0
