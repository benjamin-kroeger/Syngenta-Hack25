import logging
import asyncio
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import meteoblue_dataset_sdk


def query_historical_archive(latitude: float, longitude: float, start_date: datetime, end_date: datetime, query: dict):
    query = {
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude],
            "fallbackToNearestNeighbour": True
        },
        "format": "json",
        "timeIntervals": [f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"],
        "timeIntervalsAlignment": "none",
        "queries": [
            query
        ],
    }
    client = meteoblue_dataset_sdk.Client(apikey="9c579db416ae")  # ask for key
    result = client.querySync(query)
    # result is a structured object containing timestamps and data
    return result


def get_cummulative_rainfall():
    cummulative_rainfall_data = query_historical_archive(latitude=20, longitude=75, start_date=datetime.now() - timedelta(days=365), end_date=datetime.now() - timedelta(days=335),
                                                         query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily", "codes": [ { "code": 61, "level": "sfc", "aggregation": "sum"} ]}
                                                         )
    #print(cummulative_rainfall_data)
    return cummulative_rainfall_data
def get_cumulative_Evapotranspiration():
    cummulative_Evapotranspiration_data = query_historical_archive(latitude=20, longitude=75, start_date=datetime.now() - timedelta(days=365), end_date=datetime.now() - timedelta(days=335),
                                                         query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily", "codes": [ { "code": 261, "level": "sfc", "aggregation": "sum"} ]}
                                                         )
    #print(cummulative_Evapotranspiration_data)
    return cummulative_Evapotranspiration_data

def get_cumulative_Soil_Moisture():
    cummulative_Soil_Moisture_data = query_historical_archive(latitude=20, longitude=75, start_date=datetime.now() - timedelta(days=365), end_date=datetime.now() - timedelta(days=335),
                                                                   query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily", "codes": [ { "code": 144, "level": "0-7 cm down", "aggregation": "mean"} ]}
                                                              )
    #print(cummulative_Soil_Moisture_data)
    return cummulative_Soil_Moisture_data
def get_average_Temperature():
    average_Temperature = query_historical_archive(latitude=20, longitude=75, start_date=datetime.now() - timedelta(days=365), end_date=datetime.now() - timedelta(days=335),
                                                              query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily", "codes": [ { "code": 11, "level": "2 m above gnd", "aggregation": "mean"} ]}
                                                   )
    #print(average_Temperature)
    return get_average_Temperature

def combine_drought_risk_data():
    # Get data from individual API calls
    rainfall_data = get_cummulative_rainfall()
    evapotranspiration_data = get_cumulative_Evapotranspiration()
    soil_moisture_data = get_cumulative_Soil_Moisture()
    temperature_data = get_average_Temperature()

    # Extract start and end date for the time series
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now() - timedelta(days=335)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Extract data lists from API responses
    rainfall_values = np.array(rainfall_data.geometries[0].codes[0].timeintervals[0].data)
    evapotranspiration_values = np.array(evapotranspiration_data.geometries[0].codes[0].timeintervals[0].data)
    soil_moisture_values = np.array(soil_moisture_data.geometries[0].codes[0].timeintervals[0].data)
    temperature_values = np.array(temperature_data.geometries[0].codes[0].timeintervals[0].data)

    # Create DataFrame
    df = pd.DataFrame({
        'Date': date_range,
        'Rainfall (mm)': rainfall_values,
        'Evapotranspiration (mm)': evapotranspiration_values,
        'Soil Moisture (m³/m³)': soil_moisture_values,
        'Average Temperature (°C)': temperature_values
    })

    return df

if __name__ == "__main__":
    #print(query_historical_archive(latitude=47, longitude=7.5, start_date=datetime.now() - timedelta(days=40), end_date=datetime.now() - timedelta(days=10),
    #                               query={"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
    #
    #                                      "codes": [{"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": 8, "gddLimit": 30}]}))
    combined_data = combine_drought_risk_data()
    combined_data.to_csv("combined_drought_data.csv")
