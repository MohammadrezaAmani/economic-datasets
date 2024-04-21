import asyncio
import json
import os
import re
from typing import List

import aiohttp
import requests

IDS = [
    "currency",
    "gold-chart",
    "coin",
    "قیمت-سکه-پارسیان",
    "نرخ-ارز-نیمایی",
    "sana",
    "bank",
    "currency",
    "currency-minor",
    "global-stocks",
    "world-market/currency",
    "diff",
    "commodities",
    "energy",
    "basemetal",
    "gold-global",
    "transfer",
]

BASE_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/{}"
regex = re.compile(r'href="profile/(.*?)">')


async def get_id(id: str, data_text: set) -> List[str]:
    """
    Retrieves data from a specified URL based on the given ID.

    Args:
        id (str): The ID used to construct the URL.
        data_text (set): A set containing existing data.

    Returns:
        List[str]: A list of data retrieved from the URL.
    """
    data = []
    text = requests.get(f"https://www.tgju.org/{id}").text
    for i in regex.findall(text):
        i = i.replace(' target="_blank', "")
        i = i.replace('"', "", i.count('"'))
        if i.strip() not in data_text:
            data_text.add(i.strip())
            data.append(i.strip())
    return data


async def get_price(session: aiohttp.ClientSession, id: str, folder: str):
    """
    Fetches price data for a given ID from a web API and saves it to a JSON file.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session to use for making HTTP requests.
        id (str): The ID of the data to fetch.
        folder (str): The folder name where the JSON file will be saved.

    Returns:
        None
    """
    try:
        async with session.get(BASE_URL.format(id)) as resp:
            if resp.status == 200:
                data = await resp.json()
                async with aiofiles.open(
                    f"datasets/{folder.replace('/', '-')}/{id}.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    await f.write(json.dumps(data, indent=4))
                print("done", id)
            else:
                print("error", id)
    except Exception as e:
        print(e, id)


async def main() -> None:
    """
    This is the main function that retrieves data using asynchronous requests.

    It creates a client session using aiohttp and performs multiple tasks concurrently.
    For each ID in the IDS list, it checks if a corresponding directory exists in the "datasets" folder.
    If not, it creates the directory.
    Then, it calls the get_id function to retrieve data and adds the returned IDs to a list of tasks.
    Finally, it uses asyncio.gather to execute all the tasks concurrently.

    Note: This function should be called within an asyncio event loop.

    Returns:
        None
    """
    data_text = set()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in IDS:
            list_dir = os.listdir("datasets")
            if i.replace("/", "-") not in list_dir:
                os.mkdir("datasets/" + i.replace("/", "-"))
            for j in await get_id(i, data_text):
                tasks.append(get_price(session, j, i))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    import aiofiles

    asyncio.run(main())
