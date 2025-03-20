from src.utils.indicator_calculation import calculate_heat_stress, calculate_frost_stress, \
    calculate_nighttime_heat_stress, calculate_drought_index

import pandas as pd
from functools import partial
from collections import defaultdict

from src.utils.profile_creation import get_user_info

biological_mapping = {
    "day_heat_stress": "Stress Buster",
    "freeze_stress": "Stress Buster",
    "nigh_heat_stress": "Stress Buster",
    "drought risk": "Stress Buster",
    "nitrogen stress": "Nutrient Booster",
    "phosphorus stress": "Nutrient Booster",
    "yield risk": "Yield Booster"
}

indicator_functions = {
    "day_heat_stress": {"method": calculate_heat_stress,
                        "label": "TempAir_DailyMax (C)",
                        "thresholds":
                            {
                                "soybean": {"crop_lim_opt": 32, "crop_lim_max": 45},
                                "corn": {"crop_lim_opt": 33, "crop_lim_max": 44},
                                "cotton": {"crop_lim_opt": 32, "crop_lim_max": 38},
                                "rice": {"crop_lim_opt": 32, "crop_lim_max": 38},
                                "wheat": {"crop_lim_opt": 25, "crop_lim_max": 32},
                            }

                        },
    "night_heat_stress": {"method": calculate_nighttime_heat_stress,
                         "label": "TempAir_DailyMin (C)",
                         "thresholds":
                             {
                                 "soybean": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                 "corn": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                 "cotton": {"crop_lim_opt": 20, "crop_lim_max": 25},
                                 "rice": {"crop_lim_opt": 22, "crop_lim_max": 28},
                                 "wheat": {"crop_lim_opt": 15, "crop_lim_max": 20}
                             }

                         },
    "freeze_stress": {"method": calculate_frost_stress,
                      "label": "TempAir_DailyMin (C)",
                      "thresholds": {
                          "coybean": {"crop_lim_opt": 4, "crop_lim_max": -3},
                          "corn": {"crop_lim_opt": 4, "crop_lim_max": -3},
                          "cotton": {"crop_lim_opt": 4, "crop_lim_max": -3},
                      }}
}
def determine_drought_risk(df):

    # Compute required values
    total_rainfall = df["Rainfall (mm)"].sum()
    total_evapotranspiration = df["Evapotranspiration (mm)"].sum()
    avg_soil_moisture = df["Soil Moisture (m³/m³)"].mean()
    avg_temperature = df["Average Temperature (°C)"].mean()


    drought_index = calculate_drought_index(total_rainfall,total_evapotranspiration,avg_soil_moisture,avg_temperature)

    return drought_index


def filter_alerts(df):

    results = []

    # Ensure sorting within the function
    df = df.sort_values(by=['crop', 'measure', 'date'])

    # Group by crop and measure
    for (crop, measure), group in df.groupby(['crop', 'measure']):
        # Directly check the condition for the entire group
        trigger = (group['value'] >= 9).any() or (group['value'] >= 6).sum() >= 4
        # Get biological category, default to "error" if not found
        biological_category = biological_mapping.get(measure, "error")

        # Only keep rows where trigger is True
        if trigger:
            results.append({'crop': crop, 'measure': measure, 'biological_category': biological_category})


    return pd.DataFrame(results)


def calculate_stress_measures(forecast_data: pd.DataFrame) -> pd.DataFrame:
    # calculate heat stress
    user_info = get_user_info()


    stress_results = defaultdict(dict)

    # Apply the function for each crop
    for stress_measure, config in indicator_functions.items():
        for crop, limits in config["thresholds"].items():
            if crop.lower() not in user_info["crops"]:
                continue

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
    #calculate_stress_measures(pd.read_csv("../api_interfaces/example_df.csv")).to_csv("issues_df.csv")
    determine_drought_risk(pd.read_csv("../api_interfaces/drought_risk_data.csv"))
