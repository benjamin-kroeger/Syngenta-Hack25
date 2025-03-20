import logging
import asyncio
import time
from datetime import datetime, timedelta

import numpy as np

import meteoblue_dataset_sdk
import pandas as pd

from src.utils.indicator_calculation import calculate_drought_index


async def query_historical_archive(latitude: float, longitude: float, start_date: datetime, end_date: datetime, query: dict):
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
    result = await client.query(query)
    # result is a structured object containing timestamps and data
    return result


def query_all_gdd(seeding_date: datetime, latitude: float, longitude: float, gdd_base: int, grow_time: int, number_past_years: int = 6):
    gdd_query = {"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
                 "codes": [{"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": gdd_base, "gddLimit": 45}]}

    past_data = []
    for i in range(number_past_years):
        start_year = seeding_date.year - i - 1
        start_date = seeding_date.replace(year=start_year)

        end_date = start_date + timedelta(days=grow_time)
        past_gdd_data = query_historical_archive(latitude, longitude, start_date=start_date, end_date=end_date, query=gdd_query)

        past_data.append(np.array(past_gdd_data.geometries[0].codes[0].timeIntervals[0].data))

    gdd_df = pd.DataFrame(past_data).T

    return gdd_df


def query_all_percipitation(seeding_date: datetime, latitude: float, longitude: float, grow_time: int, number_past_years: int = 6):
    gdd_query = {"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily",
                 "codes": [{"code": 61, "level": "sfc", "aggregation": "sum"}]}

    past_data = []
    for i in range(number_past_years):
        start_year = seeding_date.year - i - 1
        start_date = seeding_date.replace(year=start_year)

        end_date = start_date + timedelta(days=grow_time)
        past_percipitation = query_historical_archive(latitude, longitude, start_date=start_date, end_date=end_date, query=gdd_query)

        past_data.append(np.array(past_percipitation.geometries[0].codes[0].timeIntervals[0].data))

    percipitation_df = pd.DataFrame(past_data).T

    return percipitation_df


def get_soil_Ph(longitude: float, latitude: float):
    actual_soil_Ph = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                              end_date=datetime.now() - timedelta(days=335),
                                              query={"domain": "WISE30", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "static",
                                                     "codes": [{"code": 812, "level": "aggregated"}]}
                                              )
    # print(average_Temperature)
    return actual_soil_Ph


def get_actual_nitrogen(longitude: float, latitude: float):
    actual_nitrogen = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                               end_date=datetime.now() - timedelta(days=335),
                                               query={"domain": "WISE30", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "static",
                                                      "codes": [{"code": 817, "level": "aggregated"}]}

                                               )
    # print(average_Temperature)
    return actual_nitrogen


def combined_static_soil_data(longitude: float, latitude: float):
    soil_Ph_data = get_soil_Ph(longitude, latitude)
    nitrogen_data = get_actual_nitrogen(longitude, latitude)
    soil_Ph_values = np.array(soil_Ph_data.geometries[0].codes[0].timeIntervals[0].data)
    nitrogen_data = np.array(nitrogen_data.geometries[0].codes[0].timeIntervals[0].data)

    df = pd.DataFrame({
        'Actual Soil Ph': soil_Ph_values,
        'Actual Nitrogen': nitrogen_data
    })
    return df


async def combine_drought_risk_data(longitude: float, latitude: float):
    # Get data from individual API calls
    rainfall_data = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                             end_date=datetime.now() - timedelta(days=335),
                                             query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily",
                                                    "codes": [{"code": 61, "level": "sfc", "aggregation": "sum"}]}
                                             )
    evapotranspiration_data = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                                       end_date=datetime.now() - timedelta(days=335),
                                                       query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily",
                                                              "codes": [{"code": 261, "level": "sfc", "aggregation": "sum"}]}
                                                       )
    soil_moisture_data = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                                  end_date=datetime.now() - timedelta(days=335),
                                                  query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily",
                                                         "codes": [{"code": 144, "level": "0-7 cm down", "aggregation": "mean"}]}
                                                  )
    temperature_data = query_historical_archive(latitude=latitude, longitude=longitude, start_date=datetime.now() - timedelta(days=365),
                                                end_date=datetime.now() - timedelta(days=335),
                                                query={"domain": "ERA5T", "gapFillDomain": "NEMSGLOBAL", "timeResolution": "daily",
                                                       "codes": [{"code": 11, "level": "2 m above gnd", "aggregation": "mean"}]}
                                                )

    results = await asyncio.gather(
        rainfall_data,
        evapotranspiration_data,
        soil_moisture_data,
        temperature_data
    )

    rainfall_data, evapotranspiration_data, soil_moisture_data, temperature_data = results

    # Extract start and end date for the time series
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now() - timedelta(days=335)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Extract data lists from API responses
    rainfall_values = np.array(rainfall_data.geometries[0].codes[0].timeIntervals[0].data)
    evapotranspiration_values = np.array(evapotranspiration_data.geometries[0].codes[0].timeIntervals[0].data)
    soil_moisture_values = np.array(soil_moisture_data.geometries[0].codes[0].timeIntervals[0].data)
    temperature_values = np.array(temperature_data.geometries[0].codes[0].timeIntervals[0].data)

    df = pd.DataFrame({
        'Date': date_range,
        'Rainfall (mm)': rainfall_values,
        'Evapotranspiration (mm)': evapotranspiration_values,
        'Soil Moisture (m³/m³)': soil_moisture_values,
        'Average Temperature (°C)': temperature_values
    })

    # Apply the function to each row in the dataframe
    df[['Drought Index', 'Risk Level']] = df.apply(
        lambda row: calculate_drought_index(row['Rainfall (mm)'],
                                            row['Evapotranspiration (mm)'],
                                            row['Soil Moisture (m³/m³)'],
                                            row['Average Temperature (°C)']), axis=1, result_type='expand'
    )

    # df.to_csv("drought_risk_data.csv")
    return df


if __name__ == "__main__":
    # print(query_historical_archive(latitude=47, longitude=7.5, start_date=datetime.now() - timedelta(days=40),
    #                              end_date=datetime.now() - timedelta(days=10),
    #                             query={"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
    #                                   "codes": [
    #                                      {"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": 8, "gddLimit": 30}]}))

    # query_all_gdd(seeding_date=datetime.fromisoformat("2023-01-01"), longitude=7.5, latitude=47, gdd_base=8, grow_time=60)

    combined_Date = combine_drought_risk_data(10, 52)
    combined_static_soil_data(78, 21)
    # print(get_cummulative_rainfall())
