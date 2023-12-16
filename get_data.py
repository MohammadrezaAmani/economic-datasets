import aiohttp
import asyncio
import json
import re
import requests
import os

IDS = [
    'currency',
    'gold-chart',
    'coin',
    'قیمت-سکه-پارسیان',
    'نرخ-ارز-نیمایی',
    'sana',
    'bank',
    'currency',
    'currency-minor',
    'global-stocks',
    'world-market/currency',
    'diff',
    'commodities',
    'energy',
    'basemetal',
    'gold-global',
    'transfer',
]

BASE_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/{}"
data_text = []

regex = re.compile(r'href="profile/(.*?)">')
def get_id(id):
    data = []
    text = requests.get(f"https://www.tgju.org/{id}").text
    for i in regex.findall(text):
        i = i.replace(' target="_blank', "")
        i = i.replace('"', "", i.count('"'))
        if i.strip() not in data_text:
            data_text.append(i.strip())
            data.append(i.strip())
    return data


async def get_price(id: str, folder: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL.format(id)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    with open(f"datasets/{folder.replace('/','-')}/{id}.json", "w", encoding="utf-8") as f:
                        f.write(json.dumps(data, indent=4))
                    print("done", id)
                else:
                    print("error", id)
    except Exception as e:
        print(e, id)


async def main():
    tasks = []
    for i in IDS:
        list_dir = os.listdir('datasets')
        if i.replace('/','-') not in list_dir:
            os.mkdir('datasets/'+i.replace('/','-'))
        for j in get_id(i):
            tasks.append(asyncio.create_task(get_price(j, i)))
    await asyncio.gather(*tasks)


asyncio.run(main())
