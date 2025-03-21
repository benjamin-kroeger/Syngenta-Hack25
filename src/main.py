from datetime import datetime
from idlelib.query import Query

import pandas as pd
from fastapi import FastAPI
from fastapi import status

from src.api_interfaces.soil_weather_archive_api import combine_drought_risk_data
from src.models import User
from src.utils.profile_creation import create_user, get_user_info
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.utils.calc_issues import calculate_stress_measures, filter_alerts, indicator_functions, determine_drought_risk
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://rebecca-kerber.de",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def get_all_alerts():
    return {"message": "hi"}


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user_enntry(user: User):
    create_user(user.name, user.longitude, user.latitude, user.crops)
    return {}


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

    drought_data = await combine_drought_risk_data(user_info["longitude"],user_info["latitude"])
    drought_index = determine_drought_risk(drought_data)

    if drought_index[0] <= 1:
        drought_alerts = []
        for crop in user_info["crops"]:
            drought_alerts.append({'crop': crop, 'measure': "drought_risk", 'biological_category': "Stress Buster"})

        drought_alert_df = pd.DataFrame(drought_alerts)

        alerts = pd.concat([alerts, drought_alert_df]).reset_index(drop=True)
    #include yiel_booster for example pruposes since formular is shit and GDD shows linear trend for last six years independent of period and region
    yield_alerts = []
    yield_alerts.append({'crop': "Wheat", 'measure': "yield_risk", 'biological_category': "Yield Booster"})
    yield_alert_df = pd.DataFrame(yield_alerts)

    alerts = pd.concat([alerts, yield_alert_df]).reset_index(drop=True)

    return alerts.to_dict()


@app.get("/weather/temp_forecast", status_code=status.HTTP_200_OK)
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
    valid crops("Soybean", "Corn "Cotton", "Rice", "Wheat"
    valid issues("day_heat_stress", "nigh_heat_stress", "freeze_stress")

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

@app.get("/issues/get_drougth_index", status_code=status.HTTP_200_OK)
async def get_drought_index():

    user_info = get_user_info()
    drought_data = await combine_drought_risk_data(user_info["longitude"],user_info["latitude"])
    drought_index = determine_drought_risk(drought_data)
    return drought_index[0]






