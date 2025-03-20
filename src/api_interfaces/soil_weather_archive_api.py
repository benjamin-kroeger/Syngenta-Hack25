import logging
import asyncio
from datetime import datetime, timedelta
from readline import set_startup_hook
import numpy as np

import meteoblue_dataset_sdk
import pandas as pd


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


def query_all_gdd(seeding_date: datetime, latitude: float, longitude: float, gdd_base: int, grow_time: int, number_past_years: int = 6):
    gdd_query = {"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
                 "codes": [{"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": gdd_base, "gddLimit": 30}]}

    past_data = []
    for i in range(number_past_years):
        start_year = seeding_date.year - i - 1
        start_date = seeding_date.replace(year=start_year)

        end_date = start_date + timedelta(days=grow_time)
        past_gdd_data = query_historical_archive(latitude, longitude, start_date=start_date, end_date=end_date, query=gdd_query)

        past_data.append(np.array(past_gdd_data.geometries[0].codes[0].timeIntervals[0].data))

    pd.DataFrame(past_data).to_csv(f"{gdd_base}_past_gdd.csv")


if __name__ == "__main__":
    print(query_historical_archive(latitude=47, longitude=7.5, start_date=datetime.now() - timedelta(days=40),
                                   end_date=datetime.now() - timedelta(days=10),
                                   query={"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
                                          "codes": [
                                              {"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": 8, "gddLimit": 30}]}))

    query_all_gdd(seeding_date=datetime.fromisoformat("2023-01-01"), longitude=7.5, latitude=47, gdd_base=8, grow_time=60)
