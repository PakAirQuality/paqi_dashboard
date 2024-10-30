import asyncio
import os
import sys
from datetime import datetime
from typing import List, Tuple

import pandas as pd
from pyairvisual.cloud_api import CloudAPI

# set debug = True for testing
# otherwise print statements get added to the final csv
DEBUG = False

# air visual API
AIRVISUAL_KEY = os.environ.get("AIRVISUAL_KEY")
cloud_api = CloudAPI(AIRVISUAL_KEY)


async def main():
    start_time = datetime.now()

    # countries = await cloud_api.supported.countries()
    states = await cloud_api.supported.states("Pakistan")
    cities = await get_cities()

    # make the final df
    air_quality_df = await get_air_quality_data(cities)

    # save to csv for testing
    current_date = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"air_quality_data_{current_date}.csv"
    air_quality_df.to_csv(filename, index=False)

    end_time = datetime.now()
    duration = end_time - start_time
    if DEBUG:
        print(f"\nFinished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # for observable, write to stdout
    air_quality_df.to_csv(sys.stdout)


# list of cities for a given country


async def get_cities(country: str = "Pakistan") -> List[Tuple[str, str]]:
    """returns a list of (City, State) for every city in a given country
    This func makes a simultaneous call for each state in a country"""

    cities = []

    try:
        states = await cloud_api.supported.states(country)

        async def fetch_cities_for_state(state: str) -> List[Tuple[str, str]]:
            try:
                city_list = await cloud_api.supported.cities(country, state)
                return [(city, state) for city in city_list]
            except Exception as e:
                if DEBUG:
                    print(f"Error fetching cities for state {state}: {e}")
                return []

        # Fetch cities for all states concurrently
        city_lists = await asyncio.gather(
            *[fetch_cities_for_state(state) for state in states]
        )
        cities = [city for sublist in city_lists for city in sublist]

    except Exception as e:
        if DEBUG:
            print(f"Error fetching states for country {country}: {e}")

    if DEBUG:
        print(
            f"Found {len(cities)} cities for {country}: {', '.join([c[0] for c in cities])}"
        )
    return cities


# get data for a city


async def get_city_data(
    city: str = "Karachi", state: str = "Sindh", country: str = "Pakistan"
) -> dict:
    """Get data for a single city"""
    try:
        data = await cloud_api.air_quality.city(city=city, state=state, country=country)
        return {city: data}
    except Exception as e:
        if DEBUG:
            print(f"Error fetching data for {city}: {str(e)}")
        return {city: None}


async def get_cities_data(
    cities: List[Tuple[str, str]], country: str = "Pakistan", max_concurrent: int = 7
) -> dict:
    """Get data for multiple cities concurrently"""

    results = {}
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(city: str, state: str):
        async with semaphore:
            return await get_city_data(city, state, country)

    tasks = [fetch_with_semaphore(city, state) for city, state in cities]
    city_data_list = await asyncio.gather(*tasks)

    for city_data in city_data_list:
        results.update(city_data)

    return results


# get all stations data for a given city


async def get_stations_data(city, state, country):
    """
    Get air quality data for all stations in a city

    Args:
        city: City name (e.g., "Karachi")
        state: State name (e.g., "Sindh")
        country: Country name (e.g., "Pakistan")

    Returns:
        Dictionary with station names as keys and their data as values
    """
    stations_data = {}

    try:
        stations = await cloud_api.supported.stations(city, state, country)

        for station_info in stations:
            station_name = station_info["station"]
            try:
                station_data = await cloud_api.air_quality.station(
                    station=station_name, city=city, state=state, country=country
                )
                stations_data[station_name] = station_data
            except Exception as e:
                if DEBUG:
                    print(f"Error getting data for station {station}: {e}")
                continue

    except Exception as e:
        if DEBUG:
            print(f"Error getting stations for {city}, {state}, {country}: {e}")
        return None

    return stations_data


# get data afor all stations in a country


async def get_all_stations_data(
    cities: List[Tuple[str, str]], country: str = "Pakistan", max_concurrent: int = 8
) -> dict:
    """
    Get data for all stations in multiple cities concurrently

    Args:
        cities: List of (city, state) tuples
        country: Country name (default: "Pakistan")
        max_concurrent: Maximum number of concurrent requests

    Returns:
        Dictionary with station names as keys and their data as values
    """
    results = {}
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_stations_with_semaphore(city: str, state: str):
        async with semaphore:
            return await get_stations_data(city, state, country)

    tasks = [fetch_stations_with_semaphore(city, state) for city, state in cities]
    all_stations_data = await asyncio.gather(*tasks)

    # Organize results by station
    for city_stations in all_stations_data:
        if city_stations:
            for station_name, station_data in city_stations.items():
                results[f"{station_data['city']}_{station_name}"] = station_data

    if DEBUG:
        print(f"Fetched data for {len(results)} stations.")
    return results


# convert a city or stations nested json data into a flat dataframe


def create_combined_dataframe(data):
    """
    Create a DataFrame from either city or station air quality data, optimized for visualization
    """
    # Extract location information
    location_info = {
        "station": data.get("name", ""),
        "city": data["city"],
        "state": data["state"],
        "country": data["country"],
        "data_source": "station" if "name" in data else "city",
        "longitude": data["location"]["coordinates"][0],
        "latitude": data["location"]["coordinates"][1],
    }

    # Initialize lists for each data type
    all_data = []

    # Helper function to process weather and pollution data
    def process_measurements(entry, data_type):
        return {
            # Metadata
            **location_info,
            "data_type": data_type,
            "ts": pd.to_datetime(entry["ts"]),
            # Air Quality
            "aqius": entry.get("aqius"),
            "aqicn": entry.get("aqicn"),
            "pm25": (
                entry.get("p2", {}).get("conc")
                if data_type != "forecast"
                else entry.get("pm25")
            ),
            "pm10": (
                entry.get("p1", {}).get("conc")
                if data_type != "forecast"
                else entry.get("pm10")
            ),
            # Weather
            "tp": entry.get("tp"),
            "tp_min": entry.get("tp_min"),
            "hu": entry.get("hu"),
            "pr": entry.get("pr"),
            "ws": entry.get("ws"),
            "wd": entry.get("wd"),
            "pop": entry.get("pop", 0),
            "ic": entry.get("ic"),
        }

    # Process historical data
    for p, w in zip(data["history"]["pollution"], data["history"]["weather"]):
        # Process pollution and weather separately
        pollution_data = process_measurements(p, "history")
        weather_data = process_measurements(w, "history")

        combined = {
            **location_info,
            "data_type": "history",
            "ts": pd.to_datetime(p["ts"]),  # using pollution timestamp
            # Air Quality fields from pollution data
            "aqius": pollution_data["aqius"],
            "aqicn": pollution_data["aqicn"],
            "pm25": pollution_data["pm25"],
            "pm10": pollution_data["pm10"],
            # Weather fields from weather data
            "tp": weather_data["tp"],
            "tp_min": weather_data["tp_min"],
            "hu": weather_data["hu"],
            "pr": weather_data["pr"],
            "ws": weather_data["ws"],
            "wd": weather_data["wd"],
            "pop": weather_data["pop"],
            "ic": weather_data["ic"],
        }
        all_data.append(combined)

    # Process forecast data
    for f in data["forecasts"]:
        all_data.append(process_measurements(f, "forecast"))

    # Process current data
    current_p = data["current"]["pollution"]
    current_w = data["current"]["weather"]

    # Process pollution and weather separately and then combine specific fields
    pollution_data = process_measurements(current_p, "current")
    weather_data = process_measurements(current_w, "current")

    # Create combined current data keeping relevant fields from each
    combined_current = {
        **location_info,
        "data_type": "current",
        "ts": pd.to_datetime(current_p["ts"]),  # using pollution timestamp
        # Air Quality fields from pollution data
        "aqius": pollution_data["aqius"],
        "aqicn": pollution_data["aqicn"],
        "pm25": pollution_data["pm25"],
        "pm10": pollution_data["pm10"],
        # Weather fields from weather data
        "tp": weather_data["tp"],
        "tp_min": weather_data["tp_min"],
        "hu": weather_data["hu"],
        "pr": weather_data["pr"],
        "ws": weather_data["ws"],
        "wd": weather_data["wd"],
        "pop": weather_data["pop"],
        "ic": weather_data["ic"],
    }

    all_data.append(combined_current)

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Convert timestamp to datetime if not already
    df["ts"] = pd.to_datetime(df["ts"])

    # Add some useful derived columns
    df["hour"] = df["ts"].dt.hour
    df["date"] = df["ts"].dt.date
    df["weekday"] = df["ts"].dt.day_name()

    # Set multi-index
    # index_cols = ["timestamp", "city"]
    # if location_info["data_source"] == "station":
    #    index_cols.append("station")

    # df.set_index(index_cols, inplace=True)
    # df.sort_index(inplace=True)

    return df


# output final air quality dataframe
# col data_source contains city or station
# col data_type contains historical, current or forecast


async def get_air_quality_data(cities: List[Tuple[str, str]]):
    """Get both city-level and station-level air quality data and combine into one DataFrame"""

    # Get both types of data
    station_readings = await get_all_stations_data(cities, max_concurrent=10)
    city_readings = await get_cities_data(cities)

    # Combine all data into one DataFrame
    dfs = []

    # Process station data
    if station_readings:  # Check if not None
        for station_data in station_readings.values():
            if station_data:  # Check if individual station data is not None
                try:
                    df = create_combined_dataframe(station_data)
                    dfs.append(df)
                except Exception as e:
                    if DEBUG:
                        print(f"Error processing station data: {e}")

    # Process city data
    if city_readings:  # Check if not None
        for city_data in city_readings.values():
            if city_data:  # Check if individual city data is not None
                try:
                    df = create_combined_dataframe(city_data)
                    dfs.append(df)
                except Exception as e:
                    if DEBUG:
                        print(f"Error processing city data: {e}")

    if not dfs:
        if DEBUG:
            print("No data was successfully processed")
        return None

    # Combine all into one DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Sort by timestamp and location
    # combined_df.sort_values(["ts", "city", "station"], inplace=True)

    # Print some info
    if DEBUG:
        print(f"Processed {len(dfs)} datasets")
        print(f"Total rows in DataFrame: {len(combined_df)}")
        print(f"Date range: {combined_df['ts'].min()} to {combined_df['ts'].max()}")

    return combined_df


if __name__ == "__main__":
    asyncio.run(main())
