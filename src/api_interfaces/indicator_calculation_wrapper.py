from datetime import timedelta, datetime
import pandas as pd
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.api_interfaces.indicator_calculation import calculate_heat_stress


def return_indicator_dictionary():
    df_daily_forecast = reqeust_daily_temp_forecast(longitude=7, latitude=14, date=datetime.today() + timedelta(days=4), number_of_days=5)
    #df_hourly_forecast = reqeust_hourly_forecast
    # Convert dailyValue to numeric (in case it's stored as a string)
    df_daily_forecast["dailyValue"] = pd.to_numeric(df_daily_forecast["dailyValue"])

    # Retrieve the maximum value from the dailyValue column
    max_value = df_daily_forecast["dailyValue"].max()
    #for testing
    max_value = 33

    print("Maximum dailyValue:", max_value)

    crops = ['Soybean', 'Corn', 'Cotton', 'Rice', 'Wheat']

    # Initialize an empty dictionary for storing stress scores
    crop_data = {crop: {} for crop in crops}

    # Calculate heat stress for each crop and store it in the dictionary
    for crop in crops:
        crop_data[crop]["heat_stress"] = calculate_heat_stress(max_value, crop)
    # Print the dictionary
    print(crop_data)
    return crop_data  # Return the populated dictionary






if __name__ == "__main__":
    return_indicator_dictionary()