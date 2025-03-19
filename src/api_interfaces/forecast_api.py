import requests
import os
from datetime import datetime, timedelta
import pandas as pd

base_url = "https://services.cehub.syngenta-ais.com"

def reqeust_daily_forecast(logitude: float, latitude:float,date:datetime,number_of_days):
    assert date > datetime.now(), "The requested date must be in the future"

    endpoint = "/api/Forecast/ShortRangeForecastDaily"
    params = {
        "longitude":logitude,
        "latitude":latitude,
        "startDate": date.strftime("%Y-%m-%d"),
        "endDate": (date + timedelta(days=number_of_days)).strftime("%Y-%m-%d"),
        "supplier": "Meteoblue",
        "measureLabel": "TempAir_DailyMin (C)",
        "top": 5,
        "format": "json"
    }
    headers = {
        "ApiKey": "4a8a11bc-2c85-41f5-9a68-13965191123e"
    }

    response = requests.get(base_url + endpoint, headers=headers, params=params)

    forecast_df = pd.DataFrame(data=response.json())
    if response.status_code == 200:
        return forecast_df
    else:
        response.raise_for_status()


if __name__ == "__main__":
    print(reqeust_daily_forecast(logitude=7,latitude=14,date=datetime.today() + timedelta(days=4), number_of_days=5))
