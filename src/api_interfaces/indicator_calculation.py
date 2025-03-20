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
if __name__ == "__main__":
    # Example usage
    tmax = 36  # Example maximum temperature
    crop = "Soybean"  # Example crop
    heat_stress = calculate_heat_stress(tmax, crop)

    print(f"Diurnal heat stress for {crop} at {tmax}°C: {heat_stress}")
