from src.api_interfaces.indicator_calculation import calculate_heat_stress, calculate_frost_stress, calculate_nighttime_heat_stress

import pandas as pd
from functools import partial


def calculate_stress_measures(forecast_data:pd.DataFrame) -> pd.DataFrame:

    # calculate heat stress

    max_temp_entries = forecast_data.loc[forecast_data["measureLabel"] == "TempAir_DailyMax (C)"]
    min_temp_entries = forecast_data.loc[forecast_data["measureLabel"] == "TempAir_DailyMin (C)"]

    # List of crops
    crops = ["Soybean", "Corn", "Cotton", "Rice", "Wheat"]

    # Dictionary to store results
    heat_stress_results = {}
    frost_stress_results = {}
    nighttime_heat_stress_results = {}

    # Apply the function for each crop
    for crop in crops:
        heat_stress_func = partial(calculate_heat_stress, crop=crop)
        frost_stress_func = partial(calculate_frost_stress, crop=crop)
        nighttime_heat_stress_func = partial(calculate_nighttime_heat_stress, crop=crop)

        heat_stress_results[crop] = max_temp_entries["dailyValue"].apply(heat_stress_func)
        frost_stress_results[crop] = min_temp_entries["dailyValue"].apply(frost_stress_func)
        nighttime_heat_stress_results[crop] = min_temp_entries["dailyValue"].apply(nighttime_heat_stress_func)










    print("hi")



if __name__ == "__main__":

    calculate_stress_measures(pd.read_csv("example_df.csv"))



