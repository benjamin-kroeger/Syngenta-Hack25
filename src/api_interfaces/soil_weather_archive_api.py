import logging
import asyncio
from datetime import datetime, timedelta

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


if __name__ == "__main__":
    print(query_historical_archive(latitude=47, longitude=7.5, start_date=datetime.now() - timedelta(days=40), end_date=datetime.now() - timedelta(days=10),
                                   query={"domain": "ERA5T", "gapFillDomain": None, "timeResolution": "daily",
                                          "codes": [{"code": 730, "level": "2 m above gnd", "aggregation": "sum", "gddBase": 8, "gddLimit": 30}]}))
