from src.utils.indicator_calculation import calculate_heat_stress, calculate_frost_stress, calculate_nighttime_heat_stress

import pandas as pd
from functools import partial
from collections import defaultdict


def calculate_stress_measures(forecast_data: pd.DataFrame) -> pd.DataFrame:
    # calculate heat stress

    # List of crops
    crops = ["Soybean", "Corn", "Cotton", "Rice", "Wheat"]

    indicator_functions = {
        "day_heat_stress": {"method": calculate_heat_stress,
                            "label": "TempAir_DailyMax (C)"},
        "nigh_heat_stress": {"method": calculate_nighttime_heat_stress,
                             "label": "TempAir_DailyMin (C)"},
        "freeze_stress": {"method": calculate_frost_stress,
                          "label": "TempAir_DailyMin (C)"}
    }

    stress_results = defaultdict(dict)

    # Apply the function for each crop
    for stress_measure,config in indicator_functions.items():
        for crop in crops:
            crop_daily_value_input = forecast_data.loc[forecast_data["measureLabel"] == config["label"],"dailyValue"]
            crop_stress_measure = partial(config["method"], crop=crop)

            stress_results[stress_measure][crop] = crop_daily_value_input.apply(crop_stress_measure)

    long_stress_results = []

    for stress_measure,crop_stresses in stress_results.items():
        for crop,stresses in crop_stresses.items():
            for idx, stress_value in stresses.items():
                long_stress_results.append({
                    "date": forecast_data.iloc[idx]["date"],  # Assuming the index represents dates
                    "crop": crop,
                    "measure": stress_measure,
                    "value": stress_value,
                })


    return pd.DataFrame(long_stress_results)


if __name__ == "__main__":
    df = calculate_stress_measures(pd.read_csv("../api_interfaces/example_df.csv"))
    df.to_csv("issues_df.csv",index=False)
    print()
