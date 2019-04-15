import asyncio
import concurrent.futures
from datetime import date, timedelta
from pathlib import Path

import requests

from collect_htmls import get_url

OUTPUT_FOLDER = Path("data/")
OUTPUT_FOLDER.mkdir(exist_ok=True, parents=True)

URL_PATTERN = "https://archive.org/download/third-eye/{}-tweets.tsv"


def fetch_date(target_date):
    date_formatted = target_date.strftime("%Y-%m-%d")
    response = get_url(URL_PATTERN.format(date_formatted), use_headers=False)
    with open(str(OUTPUT_FOLDER /
                  (date_formatted + "-tweets.tsv")),
              "w") as fout:
        fout.write(response.text)
    print(f"Downloaded {date_formatted}")


async def main(base_date, end_date):
    duration = (end_date - base_date).days + 1
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=4
    )
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            executor, fetch_date, base_date + timedelta(days=i))
        for i in range(duration)
    ]
    try:
        await asyncio.gather(*tasks)
    except Exception as err:
        for task in tasks:
            task.cancel()
        raise err


if __name__ == "__main__":
    try:
        LOOP = asyncio.get_event_loop()
        LOOP.run_until_complete(main(date(2018, 7, 1), date(2018, 8, 31)))
    finally:
        LOOP.close()
