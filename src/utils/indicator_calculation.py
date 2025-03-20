
from src.api_interfaces.forecast_api import reqeust_daily_forecast
def calculate_heat_stress(tmax, crop):
    """
    Calculate the diurnal heat stress risk for a given crop based on daily maximum temperature.

    :param tmax: Maximum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Heat stress risk (scale from 0 to 9)
    """

    # Crop-specific temperature thresholds
    crop_thresholds = {
        "Soybean": (32, 45),
        "Corn": (33, 44),
        "Cotton": (32, 38),
        "Rice": (32, 38),
        "Wheat": (25, 32)
    }

    # Validate crop input
    if crop not in crop_thresholds:
        raise ValueError(f"Invalid crop name: {crop}. Choose from {list(crop_thresholds.keys())}")

    # Extract the TMaxOptimum and TmaxLimit values for the selected crop
    tmax_optimum, tmax_limit = crop_thresholds[crop]

    # Apply the equation logic
    if tmax <= tmax_optimum:
        return 0  # No stress
    elif tmax_optimum < tmax < tmax_limit:
        return round(9 * ((tmax - tmax_optimum) / (tmax_limit - tmax_optimum)), 2)  # Scaled stress
    else:
        return 9  # Maximum stress

def calculate_nighttime_heat_stress(tmin, crop):
    """
    Calculate the nighttime heat stress risk for a given crop based on daily minimum temperature.

    :param tmin: Minimum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Nighttime heat stress risk (scale from 0 to 9)
    """

    # Crop-specific temperature thresholds for nighttime heat stress
    crop_night_thresholds = {
        "Soybean": (22, 28),
        "Corn": (22, 28),
        "Cotton": (20, 25),
        "Rice": (22, 28),
        "Wheat": (15, 20)
    }

    # Validate crop input
    if crop not in crop_night_thresholds:
        raise ValueError(f"Invalid crop name: {crop}. Choose from {list(crop_night_thresholds.keys())}")

    # Extract the TMinOptimum and TMinLimit values for the selected crop
    tmin_optimum, tmin_limit = crop_night_thresholds[crop]

    # Apply the equation logic
    if tmin < tmin_optimum:
        return 0  # No stress
    elif tmin_optimum <= tmin < tmin_limit:
        return round(9 * ((tmin - tmin_optimum) / (tmin_limit - tmin_optimum)), 2)  # Scaled stress
    else:
        return 9  # Maximum stress

def calculate_frost_stress(tmin, crop):
    """
    Calculate the frost stress risk for a given crop based on daily minimum temperature.

    :param tmin: Minimum daily air temperature (°C)
    :param crop: Name of the crop (Soybean, Corn, Cotton, Rice, Wheat)
    :return: Frost stress risk (scale from 0 to 9)
    """

    # Crop-specific temperature thresholds for frost stress
    crop_frost_thresholds = {
        "Soybean": (4, -3),
        "Corn": (4, -3),
        "Cotton": (4, -3),
        "Rice": (None, None),  # NA values
        "Wheat": (None, None)  # NA values
    }

    # Validate crop input
    if crop not in crop_frost_thresholds:
        raise ValueError(f"Invalid crop name: {crop}. Choose from {list(crop_frost_thresholds.keys())}")

    # Extract the TMinNoFrost and TMinFrost values for the selected crop
    tmin_no_frost, tmin_frost = crop_frost_thresholds[crop]

    # If the crop does not have frost stress values (Rice, Wheat), return None
    if tmin_no_frost is None or tmin_frost is None:
        return None  # No frost stress calculation for this crop

    # Apply the equation logic
    if tmin >= tmin_no_frost:
        return 0  # No frost stress
    elif tmin_frost < tmin < tmin_no_frost:
        return round(9 * (abs(tmin - tmin_no_frost) / abs(tmin_frost - tmin_no_frost)), 2)  # Scaled stress
    elif tmin <= tmin_frost:
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
    DI = (P - E) + (SM / T)

    # Interpret the Drought Index
    if DI > 1:
        risk = "No Risk"
    elif DI == 1:
        risk = "Medium Risk"
    else:  # DI < 1
        risk = "High Risk"

    return round(DI, 2), risk









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


