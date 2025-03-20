from datetime import datetime, timedelta

from src.api_interfaces.indicator_calculation import calculate_heat_stress
from src.api_interfaces.forecast_api import reqeust_daily_forecast


def detect_heat_stress_risk(df, crop, threshold=6):
    """
    Check if there are three consecutive days where the heat stress exceeds a threshold.

    :param df: Pandas DataFrame containing forecast data
    :param crop: The crop type for which to calculate heat stress
    :param threshold: Stress threshold above which we check for consecutive days
    :return: List of date ranges where stress exceeds the threshold for 3 consecutive days
    """

    # ✅ Step 1: Filter DataFrame to only include "TempAir_DailyMin (C)" rows
    df_filtered = df[df["measureLabel"] == "TempAir_DailyMin (C)"].copy()

    # ✅ Step 2: Rename the "dailyValue" column to "TMAX" for calculation
    df_filtered.rename(columns={"dailyValue": "TMAX"}, inplace=True)

    # ✅ Step 3: Apply heat stress calculation to each row
    df_filtered["heat_stress"] = df_filtered["TMAX"].apply(lambda x: calculate_heat_stress(x, crop))

    # ✅ Step 4: Find indices where stress exceeds the threshold
    exceed_indices = df_filtered[df_filtered["heat_stress"] > threshold].index

    # ✅ Step 5: Check for three consecutive days
    consecutive_days = []
    for i in range(len(exceed_indices) - 2):
        if (exceed_indices[i + 1] == exceed_indices[i] + 1) and (exceed_indices[i + 2] == exceed_indices[i] + 2):
            consecutive_days.append((df_filtered.loc[exceed_indices[i], "date"],
                                     df_filtered.loc[exceed_indices[i + 2], "date"]))

    return consecutive_days


if __name__ == "__main__":
    # Example usage
    forecast_df = reqeust_daily_forecast(longitude=7, latitude=14, date=datetime.today() + timedelta(days=4), number_of_days=5)

    if forecast_df is not None and not forecast_df.empty:
        # Detect heat stress risk for Soybean
        heat_stress_periods = detect_heat_stress_risk(forecast_df, crop="Soybean", threshold=6)

        if heat_stress_periods:
            print("Warning! Heat stress risk detected for these periods:")
            for period in heat_stress_periods:
                print(f"From {period[0]} to {period[1]}")
        else:
            print("No significant heat stress detected.")
