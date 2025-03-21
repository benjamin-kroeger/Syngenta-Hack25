from datetime import datetime
from idlelib.query import Query

import pandas as pd
from fastapi import FastAPI
from fastapi import status

from src.api_interfaces.soil_weather_archive_api import combine_drought_risk_data
from src.models import User, BiologicalApplication
from src.utils.profile_creation import write_user, get_user_info
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.utils.calc_issues import calculate_stress_measures, filter_alerts, indicator_functions, determine_drought_risk
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5501",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:5500",
    "http://localhost:63343",
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
    write_user(user.name, user.longitude, user.latitude, user.crops)
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

    drought_data = await combine_drought_risk_data(user_info["longitude"], user_info["latitude"])
    drought_index = determine_drought_risk(drought_data)

    if drought_index[0] <= 1:
        drought_alerts = []
        for crop in user_info["crops"]:
            drought_alerts.append({'crop': crop, 'measure': "drought_risk", 'biological_category': "Stress Buster"})

        drought_alert_df = pd.DataFrame(drought_alerts)

        alerts = pd.concat([alerts, drought_alert_df]).reset_index(drop=True)
    # include yiel_booster for example pruposes since formular is shit and GDD shows linear trend for last six years independent of period and region
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
        crop: str,
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
    drought_data = await combine_drought_risk_data(user_info["longitude"], user_info["latitude"])
    drought_index = determine_drought_risk(drought_data)
    return drought_index[0]





@app.post("/biological/apply", status_code=status.HTTP_201_CREATED)
def apply_biological(biological_application: BiologicalApplication):
    user_info = get_user_info()

    user_info["applied_biologicals"].append(biological_application.model_dump())

    write_user(**user_info)

    return {}


effectiveness_map_cond = {
    "day_heat_stress": 8,
    "night_heat_stress": 5,
    "freeze_stress": 5,
    "drought_risk": 5.1
}

effectiveness_map_crop = {
    "wheat":6,
    "cotton":11,
    "rice":9,

}


@app.get("/biological/profit", status_code=status.HTTP_200_OK)
def calculate_all_benefits():
    user_info = get_user_info()
    used_biologicals = user_info["applied_biologicals"]
    user_crops = user_info["crops"]

    total_benefit = {}
    for crop in user_crops:
        total_benefit[crop] = {"yield_booster": 0,
                               "stress_buster": 0}

    for application in used_biologicals:
        if application["biological"] == "stress_buster":
            total_benefit[application["crop"]][application["biological"]] += effectiveness_map_cond[application["issue"]]

        if application["biological"] == "yield_booster":
            total_benefit[application["crop"]][application["biological"]] += effectiveness_map_crop[application["crop"]]


    return total_benefit

@app.get("/profit/get_yield_increase_percentage", status_code=status.HTTP_200_OK)
async def get_yield_increase(
        biological: str,
        crop: str ,
        issue: str

):
    """
    if biological is yiel_booster, then yield increase according to crop is returned
    if biliogical is not "yiel_booster" then the respective value for the Stress buster according to issue / indicator is returned
    valid crops("Soybean", "cotton", "rice", "wheat"
    valid issues("day_heat_stress", "nigh_heat_stress", "freeze_stress")

    """

    if biological == "yield_booster":
        return effectiveness_map_crop[crop]
    else:
        return effectiveness_map_cond[issue]