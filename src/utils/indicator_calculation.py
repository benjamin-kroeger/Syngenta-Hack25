from datetime import datetime, timedelta

from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast

# Crop-specific temperature thresholds for nighttime heat stress
crop_night_thresholds = {
    "Soybean": (22, 28),
    "Corn": (22, 28),
    "Cotton": (20, 25),
    "Rice": (22, 28),
    "Wheat": (15, 20)
}




def calculate_heat_stress(daily_tmax, crop_lim_opt, crop_lim_max):
    """
    Calculate the diurnal heat stress risk for a given crop based on daily maximum temperature.

    :param tmax: Maximum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Heat stress risk (scale from 0 to 9)
    """

    # Apply the equation logic
    if daily_tmax <= crop_lim_opt:
        return 0  # No stress
    elif crop_lim_opt < daily_tmax < crop_lim_max:
        return round(9 * ((daily_tmax - crop_lim_opt) / (crop_lim_max - crop_lim_opt)), 2)  # Scaled stress
    else:
        return 9  # Maximum stress

def calculate_nighttime_heat_stress(daily_tmin, crop_lim_opt, crop_lim_max):
    """
    Calculate the nighttime heat stress risk for a given crop based on daily minimum temperature.

    :param tmin: Minimum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Nighttime heat stress risk (scale from 0 to 9)
    """

    # Apply the equation logic
    if daily_tmin < crop_lim_opt:
        return 0  # No stress
    elif crop_lim_opt <= daily_tmin < crop_lim_max:
        return round(9 * ((daily_tmin - crop_lim_opt) / (crop_lim_max - crop_lim_opt)), 2)  # Scaled stress
    else:
        return 9  # Maximum stress

def calculate_frost_stress(daily_tmin, crop_lim_opt, crop_lim_max):
    """
    Calculate the frost stress risk for a given crop based on daily minimum temperature.

    :param tmin: Minimum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Frost stress risk (scale from 0 to 9)
    """

    # Apply the equation logic
    if daily_tmin >= crop_lim_opt:
        return 0  # No frost stress
    elif crop_lim_max < daily_tmin < crop_lim_opt:
        return round(9 * (abs(daily_tmin - crop_lim_opt) / abs(crop_lim_max - crop_lim_opt)), 2)  # Scaled stress
    elif daily_tmin <= crop_lim_max:
        return 9  # Maximum frost stress
    else:
        return -10000

def calculate_drought_index(P, E, SM, T):
    """
    Compute the Drought Index (DI) based on rainfall, evaporation, soil moisture, and temperature.

    :param P: Cumulative rainfall (mm)
    :param E: Cumulative evaporation (mm)
    :param SM: Soil moisture content (mm or %)
    :param T: Average temperature (°C)
    :return: Drought Index (DI) and risk level
    """

    # Validate inputs to avoid division by zero
    if T == 0:
        raise ValueError("Temperature (T) cannot be zero to avoid division by zero.")

    # Corrected Drought Index formula
    DI = (P - E + 0.8) + (SM / T)

    # Interpret the Drought Index
    if DI > 1:
        risk = "No Risk"
    elif DI == 1:
        risk = "Medium Risk"
    else:  # DI < 1
        risk = "High Risk"

    return round(DI, 2), risk

days_until_harvest = {
    "Soybean": 120,
    "Corn": 105,
    "Cotton": 165,
    "Rice": 140,
    "Wheat": 135
}

reference_date = datetime.now() - timedelta(days=30)
seeding_date = {
    "Soybean": reference_date.strftime("%Y-%m-%d"),
    "Corn": reference_date.strftime("%Y-%m-%d"),
    "Cotton": reference_date.strftime("%Y-%m-%d"),
    "Rice": reference_date.strftime("%Y-%m-%d"),
    "Wheat": reference_date.strftime("%Y-%m-%d")
}


def calculate_pH_factor(actual_pH, optimal_pH):
    return actual_pH-optimal_pH

def calculate_nitrogen_factor(actual_nitrogen, optimal_nitrogen):
    return actual_nitrogen-optimal_nitrogen



def calculate_yield_risk(GDD, GDD_opt, P, P_opt, pH, pH_opt, N, N_opt, w1=0.3, w2=0.3, w3=0.2, w4=0.2):
    """
    Calculate the yield risk for a given crop based on Growing Degree Days (GDD), precipitation, soil pH, and nitrogen levels.

    :param GDD: Actual Growing Degree Days
    :param GDD_opt: Optimal Growing Degree Days
    :param P: Actual rainfall (mm)
    :param P_opt: Optimal rainfall for growth (mm)
    :param pH: Actual soil pH
    :param pH_opt: Optimal soil pH
    :param N: Actual available nitrogen in the soil (kg/ha)
    :param N_opt: Optimal nitrogen availability (kg/ha)
    :param w1: Weighting factor for GDD (default 0.3)
    :param w2: Weighting factor for precipitation (default 0.3)
    :param w3: Weighting factor for pH (default 0.2)
    :param w4: Weighting factor for nitrogen (default 0.2)
    :return: Yield risk value (scaled risk score)
    """

    yield_risk = (w1 * (GDD - GDD_opt) +
                  w2 * (P - P_opt) +
                  w3 * (pH - pH_opt) +
                  w4 * (N - N_opt))

    return round(yield_risk, 2)  # Return rounded risk value







if __name__ == "__main__":
    # Example usage heat stress
    tmax = 36  # Example maximum temperature
    crop = "Soybean"  # Example crop
    heat_stress = calculate_heat_stress(tmax, crop)

    print(f"Diurnal heat stress for {crop} at {tmax}°C: {heat_stress}")

    # Example usage night time
    tmin_value = 25  # Example minimum temperature
    crop_name = "Soybean"  # Example crop
    night_stress = calculate_nighttime_heat_stress(tmin_value, crop_name)

    print(f"Nighttime heat stress for {crop_name} at {tmin_value}°C: {night_stress}")

    # Example usage
    tmin_value = -2  # Example minimum temperature
    crop_name = "Soybean"  # Example crop
    frost_stress = calculate_frost_stress(tmin_value, crop_name)

    print(f"Frost stress for {crop_name} at {tmin_value}°C: {frost_stress}")

    # Example usage
    P_value = 100  # Example rainfall (mm)
    E_value = 50   # Example evaporation (mm)
    SM_value = 20  # Example soil moisture (%)
    T_value = 25   # Example temperature (°C)

    drought_index, risk_level = calculate_drought_index(P_value, E_value, SM_value, T_value)

    print(f"Drought Index: {drought_index}, Risk Level: {risk_level}")

    # Example usage:
    # calculate_yield_risk(GDD=2800, GDD_opt=2700, P=600, P_opt=700, pH=6.5, pH_opt=6.2, N=0.08, N_opt=0.077)


