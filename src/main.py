from datetime import datetime
from idlelib.query import Query

from fastapi import FastAPI
from fastapi import status
from src.models import User
from src.utils.profile_creation import create_user, get_user_info
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.utils.calc_issues import calculate_stress_measures, filter_alerts, indicator_functions

app = FastAPI()


@app.get("/")
async def get_all_alerts():
    return {"message": "hi"}


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user_enntry(user: User):
    create_user(user.name, user.longitude, user.latitude, user.crops)
    return {"id", 1}


@app.get("/alerts/getall", status_code=status.HTTP_200_OK)
async def get_all_alerts():
    user_info = get_user_info()

    temperature_forecast = reqeust_daily_temp_forecast(
        longitude=user_info["longitude"],
        latitude=user_info["latitude"],
        date=datetime.now(),
    )

    compute_issues = calculate_stress_measures(temperature_forecast)

    alerts = filter_alerts(compute_issues)

    return alerts.to_dict()


@app.get("/weather/test", status_code=status.HTTP_200_OK)
async def get_data_for_temperature_curve():
    user_info = get_user_info()

    temperature_forecast = reqeust_daily_temp_forecast(
        longitude=user_info["longitude"],
        latitude=user_info["latitude"],
        date=datetime.now(),
    )

    min_temps = temperature_forecast.loc[temperature_forecast["measureLabel"] == "TempAir_DailyMin (C)", ["date", "dailyValue"]]
    max_temps = temperature_forecast.loc[temperature_forecast["measureLabel"] == "TempAir_DailyMax (C)", ["date", "dailyValue"]]

    assert min_temps["date"].to_list() == max_temps["date"].to_list(), "whoops"

    return {"date": min_temps["date"].to_list(), "max_temps": max_temps["dailyValue"].to_list(), "min_temps": min_temps["dailyValue"].to_list()}




@app.get("/weather/testTimWithOptAndMax", status_code=status.HTTP_200_OK)
async def get_data_for_temperature_curve(
        crop: str ,
        issue: str
):
    """
    Fetch temperature data and thresholds for a given crop and issue.
    """
    user_info = get_user_info()

    # Request temperature forecast
    temperature_forecast = reqeust_daily_temp_forecast(
        longitude=user_info["longitude"],
        latitude=user_info["latitude"],
        date=datetime.now(),
    )

    # Filter temperature values
    min_temps = temperature_forecast.loc[
        temperature_forecast["measureLabel"] == "TempAir_DailyMin (C)", ["date", "dailyValue"]
    ]
    max_temps = temperature_forecast.loc[
        temperature_forecast["measureLabel"] == "TempAir_DailyMax (C)", ["date", "dailyValue"]
    ]

    # Ensure the dates align
    assert min_temps["date"].to_list() == max_temps["date"].to_list(), "whoops"

    # Validate issue
    if issue not in indicator_functions:
        return {"error": "Invalid issue type. Choose from: " + ", ".join(indicator_functions.keys())}

    # Validate crop
    if crop not in indicator_functions[issue]["thresholds"]:
        return {"error": f"Crop {crop} not found in thresholds for issue {issue}"}

    # Retrieve threshold values
    crop_thresholds = indicator_functions[issue]["thresholds"][crop]
    crop_lim_opt = crop_thresholds["crop_lim_opt"]
    crop_lim_max = crop_thresholds["crop_lim_max"]

    # Return results
    return {
        "date": min_temps["date"].to_list(),
        "max_temps": max_temps["dailyValue"].to_list(),
        "min_temps": min_temps["dailyValue"].to_list(),
        "issue": issue,
        "crop": crop,
        "thresholds": {
            "opt": crop_lim_opt,
            "max": crop_lim_max
        }
    }
