from src.utils.indicator_calculation import calculate_heat_stress, calculate_frost_stress, calculate_nighttime_heat_stress

import pandas as pd
from functools import partial
from collections import defaultdict


def calculate_stress_measures(forecast_data: pd.DataFrame) -> pd.DataFrame:
    # calculate heat stress

    indicator_functions = {
        "day_heat_stress": {"method": calculate_heat_stress,
                            "label": "TempAir_DailyMax (C)",
                            "thresholds":
                                {
                                    "Soybean": {"crop_lim_opt": 32, "crop_lim_max": 45},
                                    "Corn": {"crop_lim_opt": 33, "crop_lim_max": 44},
                                    "Cotton": {"crop_lim_opt": 32, "crop_lim_max": 38},
                                    "Rice": {"crop_lim_opt": 32, "crop_lim_max": 38},
                                    "Wheat": {"crop_lim_opt": 25, "crop_lim_max": 32},
                                }

                            },
        "nigh_heat_stress": {"method": calculate_nighttime_heat_stress,
                             "label": "TempAir_DailyMin (C)",
                             "thresholds":
                                 {
                                     "Soybean": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                     "Corn": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                     "Cotton": {"crop_lim_opt": 20, "crop_lim_max": 25},
                                     "Rice": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                     "Wheat": {"crop_lim_opt": 15, "crop_lim_max": 20}
                                 }

                             },
        "freeze_stress": {"method": calculate_frost_stress,
                          "label": "TempAir_DailyMin (C)",
                          "thresholds": {
                              "Soybean": {"crop_lim_opt": 4, "crop_lim_max": -3},
                              "Corn": {"crop_lim_opt": 4, "crop_lim_max": -3},
                              "Cotton": {"crop_lim_opt": 4, "crop_lim_max": -3},
                          }}
    }

    stress_results = defaultdict(dict)

    # Apply the function for each crop
    for stress_measure, config in indicator_functions.items():
        for crop, limits in config["thresholds"].items():
            crop_daily_value_input = forecast_data.loc[forecast_data["measureLabel"] == config["label"], "dailyValue"]
            crop_stress_measure = partial(config["method"], **limits)

            stress_results[stress_measure][crop] = crop_daily_value_input.apply(crop_stress_measure)

    long_stress_results = []

    for stress_measure, crop_stresses in stress_results.items():
        for crop, stresses in crop_stresses.items():
            for idx, stress_value in stresses.items():
                long_stress_results.append({
                    "date": forecast_data.iloc[idx]["date"],  # Assuming the index represents dates
                    "crop": crop,
                    "measure": stress_measure,
                    "value": stress_value,
                })

    return pd.DataFrame(long_stress_results)


if __name__ == "__main__":
    calculate_stress_measures(pd.read_csv("../api_interfaces/example_df.csv")).to_csv("final.csv")
