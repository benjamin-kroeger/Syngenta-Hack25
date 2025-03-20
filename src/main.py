from datetime import datetime

from fastapi import FastAPI
from fastapi import status
from src.models import User
from src.utils.profile_creation import create_user,get_user_info
from src.api_interfaces.forecast_api import reqeust_daily_temp_forecast
from src.utils.calc_issues import calculate_stress_measures
app = FastAPI()


@app.get("/")
async def get_all_alerts():


    return {"message": "hi"}


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user_enntry(user: User):
    create_user(user.name, user.longitude, user.latitude, user.crops)
    return {"id",1}

@app.get("/alerts/getall", status_code=status.HTTP_200_OK)
async def get_all_alerts():

    user_info = get_user_info()

    temperature_forecast = reqeust_daily_temp_forecast(
        longitude=user_info["longitude"],
        latitude=user_info["latitude"],
        date=datetime.now(),
    )

    compute_issues = calculate_stress_measures(temperature_forecast)

    return "success"



