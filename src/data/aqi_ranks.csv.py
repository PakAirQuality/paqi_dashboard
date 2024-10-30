import asyncio
import os
import sys
from datetime import datetime

import pandas as pd
from pyairvisual.cloud_api import CloudAPI
from stamina import retry

DEBUG = False

# air visual API
AIRVISUAL_KEY = os.environ.get("AIRVISUAL_KEY")
cloud_api = CloudAPI(AIRVISUAL_KEY)


@retry(
    on=Exception,
    attempts=3,  # Number of retries
    timeout=20,  # Total timeout in seconds
)
async def get_ranking(return_original=False):
    """
    Fetches air quality rankings and returns either the original JSON data or a formatted DataFrame.
    """
    ranking = await cloud_api.air_quality.ranking()
    if DEBUG:
        print(
            f"Ranks: {len(ranking)} cities info downloaded from AirVisual ranking API"
        )

    if return_original:  # return original JSON data
        return ranking
    else:  # convert to dataframe and return
        df = pd.json_normalize(ranking, sep="_")
        df.columns = df.columns.str.replace("ranking_", "")
        df.insert(0, "rank", range(1, len(df) + 1))
        return df


async def main():
    start_time = datetime.now()
    df = await get_ranking()

    # save to csv for debugging
    if DEBUG:
        current_date = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"aqi_ranks_{current_date}.csv"
        df.to_csv(filename, index=False)

        end_time = datetime.now()
        print(
            f"get_ranking total execution time: {(end_time-start_time).total_seconds():.2f} seconds."
        )

    # for observable, write to stdout
    df.to_csv(sys.stdout, index=False)


if __name__ == "__main__":
    asyncio.run(main())
