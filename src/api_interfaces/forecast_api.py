from typing import Any

import requests
import os
from datetime import datetime, timedelta
import pandas as pd

base_url = "https://services.cehub.syngenta-ais.com"
api_key = "4a8a11bc-2c85-41f5-9a68-13965191123e"


def query_forecast_api_general(
        longitude: float,
        latitude: float,
        start_date: datetime,
        end_date: datetime,
        measurement_label: list[str],
        endpoint: str,
        top: int = 100
) -> dict | None:
    assert isinstance(start_date, datetime), "The start date must be python datetime format"
    assert isinstance(end_date, datetime), "The end date must be python datetime format"


    params = {
        "longitude": longitude,
        "latitude": latitude,
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "supplier": "Meteoblue",
        "measureLabel": ";".join(measurement_label),
        "top": top,
        "format": "json"
    }
    headers = {
        "ApiKey": api_key,
    }

    response = requests.get(base_url + endpoint, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def reqeust_daily_temp_forecast(longitude: float, latitude: float, date: datetime, number_of_days:int=14):
    """
    Get the daily forecast for a given date and number of days.
    """

    assert date.date() >= datetime.now().date(), "The requested date must be in the future"

    api_query_results = query_forecast_api_general(
        longitude=longitude,
        latitude=latitude,
        start_date=date,
        end_date=date + timedelta(days=number_of_days),
        measurement_label=["TempAir_DailyMin (C)","TempAir_DailyMax (C)"],
        endpoint="/api/Forecast/ShortRangeForecastDaily"
    )

    forecast_df = pd.DataFrame(data=api_query_results)
    forecast_df["dailyValue"] = pd.to_numeric(forecast_df["dailyValue"])
    return forecast_df

def reqeust_yield_risk_data(longitude: float, latitude: float, date: datetime, number_of_days:int=14):
    """
    Get the daily forecast for a given date and number of days.
    """

    assert date.date() >= datetime.now().date(), "The requested date must be in the future"

    api_query_results = query_forecast_api_general(
        longitude=longitude,
        latitude=latitude,
        start_date=date,
        end_date=date + timedelta(days=number_of_days),
        measurement_label=["TempAir_DailyMax (C)","Precip_DailySum (mm)"],
        endpoint="/api/Forecast/ShortRangeForecastDaily"
    )

    forecast_df = pd.DataFrame(data=api_query_results)
    forecast_df["dailyValue"] = pd.to_numeric(forecast_df["dailyValue"])
    return forecast_df



if __name__ == "__main__":
    #example_df = reqeust_daily_temp_forecast(longitude=75, latitude=25, date=datetime.today())
    example_df_yield_risk = reqeust_yield_risk_data(longitude=75, latitude=25, date=datetime.today())


    example_df_yield_risk.to_csv("yiel_risk_data.csv",index=False)

