from datetime import datetime

from fastapi import FastAPI
from fastapi import status
from src.models import User
from src.utils.profile_creation import create_user, get_user_info
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.utils.calc_issues import calculate_stress_measures, filter_alerts

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
