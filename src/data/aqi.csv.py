import asyncio
import os
import sys
from datetime import datetime
from typing import List, Tuple

import llm
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

    end_time = datetime.now()
    duration = end_time - start_time
    if DEBUG:
        print(f"\nFinished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # save to csv for debugging / testing
        current_date = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"air_quality_data_{current_date}.csv"
        air_quality_df.to_csv(filename, index=False)

    else:
        # for observable, write to stdout
        air_quality_df.to_csv(sys.stdout)


# Define the AQI levels as a list of dictionaries
aqi_levels = [
    {"level": "Good", "min": 0, "max": 50, "color": "#97C93D"},
    {"level": "Moderate", "min": 51, "max": 100, "color": "#FFCF01"},
    {
        "level": "Unhealthy for Sensitive Groups",
        "min": 101,
        "max": 150,
        "color": "#FF9933",
    },
    {"level": "Unhealthy", "min": 151, "max": 200, "color": "#FF3333"},
    {"level": "Very Unhealthy", "min": 201, "max": 300, "color": "#A35DB5"},
    {"level": "Hazardous", "min": 301, "max": float("inf"), "color": "#8B3F3F"},
]


# Function to get level and color based on AQI value
def get_aqi_info(aqi_value):
    for level in aqi_levels:
        if level["min"] <= aqi_value <= level["max"]:
            return level["level"], level["color"]
    return "Unknown", "#000000"  # Default return if no range matches


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
    cities: List[Tuple[str, str]], country: str = "Pakistan", max_concurrent: int = 10
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
    cities: List[Tuple[str, str]], country: str = "Pakistan", max_concurrent: int = 12
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


def get_aqi_averages(combined_df, current_city_mask, current_date):
    """Calculate average PM2.5 and AQI values for yesterday and tomorrow.

    Args:
        combined_df (pd.DataFrame): DataFrame containing historical and forecast data
        current_city_mask (pd.Series): Boolean mask for current city's rows
        current_date (pd.Timestamp): Reference date for calculating yesterday/tomorrow

    Returns:
        tuple: Two pd.Series containing mean PM2.5 and AQI values for:
            - yesterday_avgs: Previous day's averages with city name as index
            - tomorrow_avgs: Next day's forecast averages with city name as index
    """
    # Get city name from current data
    city_name = combined_df[current_city_mask]["city"].iloc[0]

    # Create mask for this city (all data types)
    city_mask = combined_df["city"] == city_name

    # Get yesterday's data
    yesterday_data = combined_df[
        city_mask
        & (combined_df["data_type"] == "history")
        & (combined_df["date"] == current_date - pd.Timedelta(days=1))
    ]
    yesterday_avgs = yesterday_data[["pm25", "aqius"]].mean().round(1)
    yesterday_avgs["city"] = city_name

    # Get tomorrow's forecast
    tomorrow_data = combined_df[
        city_mask
        & (combined_df["data_type"] == "forecast")
        & (combined_df["date"] == current_date + pd.Timedelta(days=1))
    ]
    tomorrow_avgs = tomorrow_data[["pm25", "aqius"]].mean().round(1)
    tomorrow_avgs["city"] = city_name

    if DEBUG:
        print("\nYesterday's Average")
        print(yesterday_avgs)
        print("\nTomorrow's Forecast Average")
        print(tomorrow_avgs)

    return yesterday_avgs, tomorrow_avgs


system_prompt = """You are a helpful assistant providing short, one-line observations about air quality data. Be informative but slightly humorous.

    Use provided AQI and PM2.5 values to give insights about the air quality situation, and consider yesterday's actual and tmrw's forecast too. 

    Use the passed in values and AQI scale below to inform your comment:
    
    GREEN 1. Good (AQI: 0-50, PM2.5: 0-9.0 μg/m3):
    Safe for everyone. Outdoor activities and ventilation OK.

    YELLOW 2. Moderate (AQI: 51-100, PM2.5: 9.1-35.4):
    Sensitive groups should limit outdoor exercise. Avoid ventilation.

    ORANGE 3. Unhealthy for Sensitive Groups (AQI: 101-150, PM2.5: 35.5-55.4):
    Everyone may experience irritation. Public should reduce outdoor activity. Sensitive groups should avoid outdoors and use masks.

    RED 4. Unhealthy (AQI: 151-200, PM2.5: 55.5-125.4):
    Increased health risks for all. Everyone should avoid outdoors and wear masks. Use air purifiers indoors.

    PURPLE 5. Very Unhealthy (AQI: 201-300, PM2.5: 125.5-225.4):
    Public noticeably affected. Everyone should avoid outdoors, wear masks, and use air purifiers.

    MAROON 6. Hazardous (AQI: 301-500+, PM2.5: 225.5+):
    High risk for everyone. Stay indoors, use masks if outdoors, run air purifiers.
    """


def get_comment(row, model, yesterday_avgs, tomorrow_avgs):
    """Generate an LLM comment about air quality for a given city row"""

    city = row["city"]
    # Verify we're using the correct city's averages
    assert yesterday_avgs["city"] == city
    assert tomorrow_avgs["city"] == city

    # Calculate trends
    pm25_yesterday_trend = row["pm25"] - yesterday_avgs["pm25"]
    pm25_tomorrow_trend = tomorrow_avgs["pm25"] - row["pm25"]
    aqi_yesterday_trend = row["aqius"] - yesterday_avgs["aqius"]
    aqi_tomorrow_trend = tomorrow_avgs["aqius"] - row["aqius"]

    prompt = f"""Give me a one-line observation about the air quality in {row['city']}, Pakistan.
    Key metrics:
    Yesterday's averages: PM2.5 = {yesterday_avgs['pm25']}, AQI = {yesterday_avgs['aqius']}
    Current values: PM2.5 = {row['pm25']}, AQI = {row['aqius']}, Temp = {row['tp']}
    Tomorrow's forecast averages: PM2.5 = {tomorrow_avgs['pm25']}, AQI = {tomorrow_avgs['aqius']}
    """

    try:
        response = model.prompt(prompt, system=system_prompt)
        comment = response.text().strip()
    except Exception as e:
        if DEBUG:
            print(f"Anthropic API error: {str(e)}")
        comment = ""

    if DEBUG:
        print(f"\n{city} prompt: {prompt}")
        print(f"{city}: {comment}")

    return comment


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

    # add aqi level and color cols
    df[["aqi_level", "aqi_color"]] = df.apply(
        lambda row: pd.Series(get_aqi_info(row["aqius"])), axis=1
    )

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
    if DEBUG:
        station_readings = None
    else:
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
    combined_df["comment"] = pd.NA

    # Sort by timestamp and location
    # combined_df.sort_values(["ts", "city", "station"], inplace=True)

    # Print some info
    if DEBUG:
        print(f"Processed {len(dfs)} datasets")
        print(f"Total rows in DataFrame: {len(combined_df)}")
        print(f"Date range: {combined_df['ts'].min()} to {combined_df['ts'].max()}")

    # Add comments for cities' current readings
    model = llm.get_model("claude-3-haiku-20240307")

    # Create mask for current city readings
    current_city_mask = (combined_df["data_source"] == "city") & (
        combined_df["data_type"] == "current"
    )

    # Get all current cities
    masked_df = combined_df[current_city_mask]

    # this should call the get_comment func for only cities / current
    # Process each city separately
    for city in masked_df["city"].unique():
        # Create city-specific mask
        city_mask = current_city_mask & (combined_df["city"] == city)

        # Get current date for this city
        current_date = combined_df[city_mask]["date"].iloc[0]

        # Get averages for this city
        yesterday_avgs, tomorrow_avgs = get_aqi_averages(
            combined_df, city_mask, current_date
        )

        # Update comments for this city's current readings
        city_df = combined_df[city_mask]
        combined_df.loc[city_mask, "comment"] = city_df.apply(
            lambda row: get_comment(row, model, yesterday_avgs, tomorrow_avgs),
            axis=1,
        )

    return combined_df


if __name__ == "__main__":
    asyncio.run(main())
