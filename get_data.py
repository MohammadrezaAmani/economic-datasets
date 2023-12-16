import aiohttp
import asyncio
import json
import os
import re
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


async def get_id(id, data_text):
    data = []
    text = requests.get(f"https://www.tgju.org/{id}").text
    for i in regex.findall(text):
        i = i.replace(' target="_blank', "")
        i = i.replace('"', "", i.count('"'))
        if i.strip() not in data_text:
            data_text.add(i.strip())
            data.append(i.strip())
    return data


async def get_price(session, id, folder):
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


async def main():
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
